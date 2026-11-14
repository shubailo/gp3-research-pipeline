#!/usr/bin/env python3
"""
CTM BoostR Data Extraction Compliance Linter (GP3 Standards)
============================================================
Deterministic CLI tool to audit systematic review and meta-analysis extraction
workbooks (e.g. Data_extraction_template_v9.xlsx) against the Centre for
Translational Medicine (CTM) BoostR standards and Cochrane Handbook v6.5.

Gates Evaluated:
    1. Numeric-Only Mandate (Max 25 pts) [FATAL GATE]
       - Statistical fields must contain ONLY real numbers (int/float).
       - FATAL: "approx 12", "N/A", "38,6" (comma decimal), ">180", "[1-2]", "3320 g".
       - Any Gate 1 fatal violation results in IMMEDIATE OVERALL FAIL.
    2. Mandatory Cells Integrity & Mathematical Logic (Max 20 pts)
       - Populated rows must have Author_Year and Outcome.
       - 2x2 contingency table validity: events <= total, counts >= 0, total > 0.
       - Confidence intervals: CI_min <= CI_max, point estimate within bounds.
    3. Unique Author_Year & Arm Disaggregation (Max 15 pts)
       - Prohibits ecological double-counting of studies for the same outcome.
       - Multi-arm extractions must have distinct arm/subgroup labels (e.g. "(Mild)").
    4. Homogeneous Outcome Taxonomy (Max 20 pts)
       - Standardizes outcome nomenclature across rows within each sheet.
       - Detects casing/whitespace mismatches and synonym clashes (e.g. "Mortality" vs "Death").
    5. Unit Isolation & Risk of Bias Sheets (Max 20 pts)
       - Measurement units isolated in designated "Unit" columns.
       - Evaluates RoB worksheets (RoB 2, QUIPS, ROBINS-I) for domain completeness and valid ratings.

Threshold:
    Total Score >= 85/100 points AND ZERO Gate 1 Fatal Violations -> PASS (exit 0)
    Otherwise -> FAIL (exit 1)
"""

import sys
import os
import re
import json
import argparse
from typing import Dict, Any, List, Tuple, Optional, Set

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from src.utils.console import configure_utf8_console
configure_utf8_console()

try:
    import openpyxl
except ImportError:
    print("FATAL: openpyxl is required. Install via: pip install openpyxl")
    sys.exit(1)


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


# Common text placeholders forbidden in numeric cells
FORBIDDEN_NUMERIC_PLACEHOLDERS = {
    "n/a", "na", "-", "--", "nil", "missing", "nr", "not reported",
    "none", "unknown", "nem ismert", "tbd", "nd", "not done", "null"
}

# Standard RoB domain rating keywords
VALID_ROB_RATINGS = {
    "low", "moderate", "high", "some concerns", "unclear",
    "critical", "serious", "no information"
}

# Clinical outcome synonym clusters for taxonomy auditing
TAXONOMY_SYNONYM_CLUSTERS = [
    {
        "cluster_name": "Mortality / Death",
        "terms": ["mortality", "death", "in-hospital mortality", "all-cause mortality", "death before discharge"],
        "differentiators": ["composite", "morbidity", "or", "and", "cause-specific"]
    },
    {
        "cluster_name": "Necrotizing Enterocolitis",
        "terms": ["necrotizing enterocolitis", "nec"],
        "differentiators": ["stage", "bell", "surgical", "medical"]
    },
    {
        "cluster_name": "Late-Onset Sepsis",
        "terms": ["late-onset sepsis", "los", "late onset sepsis", "sepsis"],
        "differentiators": ["early", "proven", "clinical", "suspected", "fungal", "bacterial"]
    },
    {
        "cluster_name": "Bronchopulmonary Dysplasia",
        "terms": ["bronchopulmonary dysplasia", "bpd", "chronic lung disease", "cld"],
        "differentiators": ["mild", "moderate", "severe", "36 wk", "28d"]
    },
    {
        "cluster_name": "Intraventricular Hemorrhage",
        "terms": ["intraventricular hemorrhage", "intraventricular haemorrhage", "ivh"],
        "differentiators": ["grade", "severe", "mild", ">="]
    },
    {
        "cluster_name": "Retinopathy of Prematurity",
        "terms": ["retinopathy of prematurity", "rop"],
        "differentiators": ["stage", "severe", "treatment", "laser"]
    },
    {
        "cluster_name": "Neurodevelopmental Impairment",
        "terms": ["neurodevelopmental impairment", "ndi", "neurodevelopmental outcome", "nd disability"],
        "differentiators": ["bayley", "bsid", "18-24m", "severe", "mild", "cognitive", "motor"]
    }
]


class ExtractionLinter:
    def __init__(self, filepath: str, strict: bool = False):
        self.filepath = filepath
        self.strict = strict
        self.wb: Optional[openpyxl.Workbook] = None
        self.issues: List[Dict[str, Any]] = []
        self.gate1_fatal: bool = False
        
        # Gate scores
        self.gate1_score: int = 25
        self.gate2_score: int = 20
        self.gate3_score: int = 15
        self.gate4_score: int = 20
        self.gate5_score: int = 20
        self.total_score: int = 100

    def add_issue(self, gate: int, severity: str, sheet: str, cell: str, row: int, col_name: str,
                  found_val: Any, expected: str, message: str):
        self.issues.append({
            "gate": gate,
            "severity": severity,
            "sheet": sheet,
            "cell": cell,
            "row": row,
            "column": col_name,
            "found_value": str(found_val),
            "expected": expected,
            "message": message
        })

    def load_workbook(self) -> bool:
        if not os.path.exists(self.filepath):
            self.add_issue(1, "FATAL", "N/A", "A1", 0, "File", "NOT_FOUND", "Valid Excel file", f"Workbook not found: {self.filepath}")
            self.gate1_fatal = True
            return False
        try:
            self.wb = openpyxl.load_workbook(self.filepath, data_only=True)
            return True
        except Exception as e:
            self.add_issue(1, "FATAL", "N/A", "A1", 0, "Workbook", str(e), "Readable workbook", f"Unable to parse workbook: {e}")
            self.gate1_fatal = True
            return False

    def scan_rows(self, ws, start_row: int = 4, max_scan: int = 3000, empty_limit: int = 15) -> List[int]:
        """Returns row indices of populated data rows, bounded to avoid 1M row Excel explosion."""
        populated = []
        empty_streak = 0
        limit = min(ws.max_row + 1, max_scan)
        for r in range(start_row, limit):
            # Check first 40 columns
            has_val = False
            for c in range(1, min(ws.max_column + 1, 40)):
                if ws.cell(r, c).value is not None:
                    has_val = True
                    break
            if has_val:
                populated.append(r)
                empty_streak = 0
            else:
                empty_streak += 1
                if empty_streak >= empty_limit:
                    break
        return populated

    # --------------------------------------------------------------------------
    # GATE 1: Numeric-Only Mandate (FATAL ON NON-NUMERIC)
    # --------------------------------------------------------------------------
    def audit_gate1_numeric(self):
        """Scans all statistical and demographic numeric columns."""
        if not self.wb:
            return

        fatal_count = 0
        string_numeric_count = 0

        # Define numeric column indices per known sheet pattern
        sheet_configs = {
            "ORs - RRs": {
                "num_cols": [13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 25, 26, 27, 28, 30],
                "header_row": 3
            },
            "Mean Difference": {
                "num_cols": [6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43],
                "header_row": 3
            },
            "Simple mean": {
                "num_cols": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
                "header_row": 3
            },
            "Ratio": {
                "num_cols": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
                "header_row": 3
            },
            "Before-After": {
                "num_cols": [5, 6, 7, 8, 13, 15, 16, 25, 26, 27, 38, 39],
                "header_row": 3
            },
            "Diagnostic test": {
                "num_cols": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
                "header_row": 3
            },
            "Correlations": {
                "num_cols": [3, 4],
                "header_row": 3
            },
            "Regression coefficient": {
                "num_cols": [2, 3, 4, 5, 6],
                "header_row": 3
            },
            "Basic layout": {
                "num_cols": [1, 3, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 21, 22, 23, 24, 25, 26, 27, 28, 29, 33, 34, 35, 36, 37, 38, 39, 40, 41],
                "header_row": 3
            }
        }

        for sname, cfg in sheet_configs.items():
            if sname not in self.wb.sheetnames:
                continue
            ws = self.wb[sname]
            h_row = cfg["header_row"]
            rows = self.scan_rows(ws, start_row=h_row + 1)
            
            for r in rows:
                for c in cfg["num_cols"]:
                    if c > ws.max_column:
                        continue
                    cell_obj = ws.cell(r, c)
                    val = cell_obj.value
                    if val is None:
                        continue
                    
                    coord = cell_obj.coordinate
                    col_name = str(ws.cell(h_row, c).value or ws.cell(h_row - 1, c).value or f"Col {c}").strip()
                    
                    # Numeric types are always valid
                    if isinstance(val, (int, float)):
                        continue
                    
                    # If string, analyze
                    val_str = str(val).strip()
                    if not val_str:
                        continue
                    
                    # Check if it parses cleanly as float
                    try:
                        float(val_str)
                        # Valid numeric literal stored as string: WARN only
                        string_numeric_count += 1
                        self.add_issue(
                            1, "WARN", sname, coord, r, col_name, val_str,
                            "Numeric Excel cell type (float/int)",
                            f"Number stored as text: '{val_str}'. Recommend storing as native numeric in Excel."
                        )
                        continue
                    except ValueError:
                        pass
                    
                    # If it cannot be parsed as float: FATAL GATE 1 ERROR!
                    fatal_count += 1
                    self.gate1_fatal = True
                    lower = val_str.lower()
                    
                    if any(ph == lower or ph in lower for ph in FORBIDDEN_NUMERIC_PLACEHOLDERS):
                        self.add_issue(
                            1, "FATAL", sname, coord, r, col_name, val_str,
                            "Completely blank cell or standard NA",
                            f"Text placeholder '{val_str}' forbidden in numeric column."
                        )
                    elif "," in val_str and re.match(r"^-?\d+,\d+$", val_str):
                        self.add_issue(
                            1, "FATAL", sname, coord, r, col_name, val_str,
                            f"{val_str.replace(',', '.')}",
                            f"Comma decimal '{val_str}' forbidden. Use standard dot decimal."
                        )
                    elif any(k in lower for k in ["approx", "kb.", "ca.", "~", ">", "<", "[", "]", "%"]):
                        self.add_issue(
                            1, "FATAL", sname, coord, r, col_name, val_str,
                            "Exact numeric value without symbols",
                            f"Text modifier / range '{val_str}' mixed into numeric column."
                        )
                    elif re.search(r"[a-zA-Z]", val_str):
                        self.add_issue(
                            1, "FATAL", sname, coord, r, col_name, val_str,
                            "Pure number (units must be in dedicated Unit column)",
                            f"Embedded unit / letters in numeric column: '{val_str}'."
                        )
                    else:
                        self.add_issue(
                            1, "FATAL", sname, coord, r, col_name, val_str,
                            "Valid numeric value",
                            f"Invalid non-numeric value: '{val_str}'."
                        )

        # Gate 1 scoring
        if self.gate1_fatal or fatal_count > 0:
            self.gate1_score = 0
        else:
            # Minor penalty for string-stored numbers (max -5)
            self.gate1_score = max(20, 25 - min(string_numeric_count * 2, 5))

    # --------------------------------------------------------------------------
    # GATE 2: Mandatory Cells Integrity & Mathematical Consistency
    # --------------------------------------------------------------------------
    def audit_gate2_mandatory_and_math(self):
        """Audits mandatory study identifiers, outcomes, 2x2 pairs, and math logic."""
        if not self.wb:
            return

        errors = 0

        # 1. Audit 'Basic layout'
        if "Basic layout" in self.wb.sheetnames:
            ws_b = self.wb["Basic layout"]
            rows = self.scan_rows(ws_b, start_row=4)
            for r in rows:
                num = ws_b.cell(r, 1).value
                author = ws_b.cell(r, 2).value
                year = ws_b.cell(r, 3).value
                
                # If row has any data, check author and year
                if not author or not str(author).strip():
                    errors += 1
                    self.add_issue(2, "ERROR", "Basic layout", f"B{r}", r, "First Author", author, "Valid Author surname", "Missing First Author in populated study row.")
                if year is None:
                    errors += 1
                    self.add_issue(2, "ERROR", "Basic layout", f"C{r}", r, "Year of publication", year, "Publication year (e.g. 2024)", "Missing Year of publication.")
                elif isinstance(year, int) and (year < 1980 or year > 2030):
                    errors += 1
                    self.add_issue(2, "ERROR", "Basic layout", f"C{r}", r, "Year of publication", year, "1980-2030", f"Implausible publication year: {year}.")

        # 2. Audit 'ORs - RRs'
        if "ORs - RRs" in self.wb.sheetnames:
            ws_or = self.wb["ORs - RRs"]
            rows = self.scan_rows(ws_or, start_row=4)
            for r in rows:
                out = ws_or.cell(r, 1).value
                study_id = ws_or.cell(r, 3).value
                
                # Mandatory Outcome & Study ID
                if not out or not str(out).strip():
                    errors += 1
                    self.add_issue(2, "ERROR", "ORs - RRs", f"A{r}", r, "Outcome", out, "Outcome Name", "Missing Outcome Name in populated row.")
                if not study_id or not str(study_id).strip():
                    errors += 1
                    self.add_issue(2, "ERROR", "ORs - RRs", f"C{r}", r, "Study ID", study_id, "Author Year", "Missing Study ID in populated row.")

                # 2x2 Contingency Table Pair Completeness & Math
                ev_i = ws_or.cell(r, 13).value
                tot_i = ws_or.cell(r, 14).value
                ev_c = ws_or.cell(r, 15).value
                tot_c = ws_or.cell(r, 16).value

                # Pair completeness (Intervention)
                if ev_i is not None and tot_i is None:
                    errors += 1
                    self.add_issue(2, "ERROR", "ORs - RRs", f"N{r}", r, "Total N0 of patients in I", tot_i, "Positive integer", "Missing denominator (Total_I) while numerator (Events_I) is present.")
                elif ev_i is None and tot_i is not None:
                    # Missing numerator is a warning
                    self.add_issue(2, "WARN", "ORs - RRs", f"M{r}", r, "N0 of patients with event in I", ev_i, "Event count or None", "Total_I present but Events_I is missing.")

                # Pair completeness (Control)
                if ev_c is not None and tot_c is None:
                    errors += 1
                    self.add_issue(2, "ERROR", "ORs - RRs", f"P{r}", r, "Total N0 of patients in C", tot_c, "Positive integer", "Missing denominator (Total_C) while numerator (Events_C) is present.")

                # Math check: Intervention
                if isinstance(ev_i, (int, float)) and isinstance(tot_i, (int, float)):
                    if ev_i < 0:
                        errors += 1
                        self.add_issue(2, "ERROR", "ORs - RRs", f"M{r}", r, "Events_I", ev_i, ">= 0", f"Negative event count in Intervention: {ev_i}.")
                    if tot_i <= 0:
                        errors += 1
                        self.add_issue(2, "ERROR", "ORs - RRs", f"N{r}", r, "Total_I", tot_i, "> 0", f"Total count in Intervention must be > 0: {tot_i}.")
                    if ev_i > tot_i:
                        errors += 1
                        self.add_issue(2, "ERROR", "ORs - RRs", f"M{r}", r, "Events_I vs Total_I", f"Events={ev_i} > Total={tot_i}", "Events <= Total", f"Mathematical impossibility: Events ({ev_i}) exceeds Total ({tot_i}) in Intervention.")

                # Math check: Control
                if isinstance(ev_c, (int, float)) and isinstance(tot_c, (int, float)):
                    if ev_c < 0:
                        errors += 1
                        self.add_issue(2, "ERROR", "ORs - RRs", f"O{r}", r, "Events_C", ev_c, ">= 0", f"Negative event count in Control: {ev_c}.")
                    if tot_c <= 0:
                        errors += 1
                        self.add_issue(2, "ERROR", "ORs - RRs", f"P{r}", r, "Total_C", tot_c, "> 0", f"Total count in Control must be > 0: {tot_c}.")
                    if ev_c > tot_c:
                        errors += 1
                        self.add_issue(2, "ERROR", "ORs - RRs", f"O{r}", r, "Events_C vs Total_C", f"Events={ev_c} > Total={tot_c}", "Events <= Total", f"Mathematical impossibility: Events ({ev_c}) exceeds Total ({tot_c}) in Control.")

                # CI Bounds Check (Crude)
                ci_min = ws_or.cell(r, 22).value
                ci_max = ws_or.cell(r, 23).value
                pe = ws_or.cell(r, 20).value
                if isinstance(ci_min, (int, float)) and isinstance(ci_max, (int, float)):
                    if ci_min > ci_max:
                        errors += 1
                        self.add_issue(2, "ERROR", "ORs - RRs", f"V{r}:W{r}", r, "CI min / max", f"{ci_min} > {ci_max}", "CI_min <= CI_max", "Inverted confidence intervals (CI min > CI max).")
                    elif isinstance(pe, (int, float)) and not (min(ci_min, ci_max) <= pe <= max(ci_min, ci_max)):
                        # Check minor rounding discrepancy tolerance (2%)
                        tol = abs(pe) * 0.05
                        if not (min(ci_min, ci_max) - tol <= pe <= max(ci_min, ci_max) + tol):
                            self.add_issue(2, "WARN", "ORs - RRs", f"T{r}", r, "Point Estimate", pe, f"[{ci_min}, {ci_max}]", f"Point estimate {pe} outside CI bounds [{ci_min}, {ci_max}].")

                # CI Bounds Check (Adjusted)
                adj_min = ws_or.cell(r, 27).value
                adj_max = ws_or.cell(r, 28).value
                adj_pe = ws_or.cell(r, 25).value
                if isinstance(adj_min, (int, float)) and isinstance(adj_max, (int, float)):
                    if adj_min > adj_max:
                        errors += 1
                        self.add_issue(2, "ERROR", "ORs - RRs", f"AA{r}:AB{r}", r, "Adjusted CI min / max", f"{adj_min} > {adj_max}", "CI_min <= CI_max", "Inverted adjusted confidence intervals (CI min > CI max).")
                    elif isinstance(adj_pe, (int, float)) and not (min(adj_min, adj_max) <= adj_pe <= max(adj_min, adj_max)):
                        tol = abs(adj_pe) * 0.05
                        if not (min(adj_min, adj_max) - tol <= adj_pe <= max(adj_min, adj_max) + tol):
                            self.add_issue(2, "WARN", "ORs - RRs", f"Y{r}", r, "Adjusted OR", adj_pe, f"[{adj_min}, {adj_max}]", f"Adjusted estimate {adj_pe} outside CI bounds [{adj_min}, {adj_max}].")

        # Gate 2 scoring: 20 pts minus 4 pts per error
        self.gate2_score = max(0, 20 - (errors * 4))

    # --------------------------------------------------------------------------
    # GATE 3: Unique Author_Year & Disaggregation Integrity
    # --------------------------------------------------------------------------
    def audit_gate3_unique_author_year(self):
        """Ensures studies are not counted multiple times for the same outcome without explicit arm differentiation."""
        if not self.wb:
            return

        duplicates = 0
        outcome_sheets = ["ORs - RRs", "Mean Difference", "Simple mean", "Before-After", "Diagnostic test"]

        for sname in outcome_sheets:
            if sname not in self.wb.sheetnames:
                continue
            ws = self.wb[sname]
            rows = self.scan_rows(ws, start_row=4)
            seen_pairs: Dict[Tuple[str, str], List[int]] = {}

            for r in rows:
                out = str(ws.cell(r, 1).value or "").strip()
                study = str(ws.cell(r, 3).value or "").strip()
                if not out or not study:
                    continue
                
                key = (out.lower(), study.lower())
                seen_pairs.setdefault(key, []).append(r)

            for (out_norm, study_norm), row_list in seen_pairs.items():
                if len(row_list) > 1:
                    # Check if there is explicit arm / factor distinction
                    # e.g. "Ali 2024 (Mild)" vs "Ali 2024 (Severe)" or arm/factor column
                    distinct_arms = True
                    first_study_str = str(ws.cell(row_list[0], 3).value).strip()
                    for next_r in row_list[1:]:
                        next_study_str = str(ws.cell(next_r, 3).value).strip()
                        # If the study string is verbatim identical
                        if first_study_str.lower() == next_study_str.lower():
                            # Check if column 2 (definition) or column 29/32 (factors) specifies arm
                            col2_a = str(ws.cell(row_list[0], 2).value or "").strip()
                            col2_b = str(ws.cell(next_r, 2).value or "").strip()
                            if col2_a.lower() == col2_b.lower():
                                distinct_arms = False
                                break

                    if not distinct_arms:
                        duplicates += 1
                        rows_str = ", ".join(f"Row {rx}" for rx in row_list)
                        self.add_issue(
                            3, "ERROR", sname, f"C{row_list[0]}", row_list[0], "Study ID",
                            first_study_str, "Disaggregated study label (e.g. 'Author 2024 (Arm A)')",
                            f"Ecological duplication: '{first_study_str}' appears {len(row_list)} times for outcome '{out_norm}' without explicit arm differentiation ({rows_str})."
                        )

        # Gate 3 scoring: 15 pts minus 5 per un-disaggregated duplicate
        self.gate3_score = max(0, 15 - (duplicates * 5))

    def _is_empty_cell(self, val: Any) -> bool:
        return val is None or str(val).strip() == ""

    def _is_administrative_exclusion_row(self, ws, r: int, outcome_val: str, sname: str) -> bool:
        """
        Determines whether a row is an administrative exclusion entry.
        Skipped from synonym clash inspection ONLY if BOTH conditions are met:
        a) Outcome field (Col 1) case-insensitively starts with:
           'EXCLUDED', 'NOT REPORTED', 'NOT APPLICABLE', 'N/A -'
        b) ALL quantitative outcome fields in that row are empty (None or blank).
        If only one condition holds, the row is inspected normally.
        """
        prefixes = ("excluded", "not reported", "not applicable", "n/a -")
        norm_val = outcome_val.strip().lower()
        if not any(norm_val.startswith(p) for p in prefixes):
            return False

        # Quantitative column indices per sheet
        if sname == "ORs - RRs":
            quant_cols = [13, 14, 15, 16, 20, 22, 23, 25, 27, 28]
        elif sname == "Mean Difference":
            quant_cols = [6, 7, 8, 13, 15, 16, 20, 25, 26, 27, 31, 36, 37, 38, 39, 40, 41]
        elif sname == "Simple mean":
            quant_cols = [5, 6, 7, 8, 13, 15, 16, 17, 18, 19, 20]
        elif sname == "Ratio":
            quant_cols = [5, 13, 14]
        elif sname == "Diagnostic test":
            quant_cols = [4, 5, 6, 7, 8, 9, 10, 11, 12]
        else:
            quant_cols = [2, 3, 4, 5, 6]

        for c in quant_cols:
            if c <= ws.max_column:
                cell_val = ws.cell(r, c).value
                if not self._is_empty_cell(cell_val):
                    return False  # Safety barrier: contains quantitative data, inspect normally!
        return True

    # --------------------------------------------------------------------------
    # GATE 4: Homogeneous Outcome Taxonomy
    # --------------------------------------------------------------------------
    def audit_gate4_taxonomy(self):
        """Audits consistency of outcome strings within each sheet (whitespace, casing, synonym clashes)."""
        if not self.wb:
            return

        discrepancies = 0
        outcome_sheets = ["ORs - RRs", "Mean Difference", "Simple mean", "Before-After", "Diagnostic test"]

        for sname in outcome_sheets:
            if sname not in self.wb.sheetnames:
                continue
            ws = self.wb[sname]
            rows = self.scan_rows(ws, start_row=4)
            
            raw_outcomes = []
            for r in rows:
                val = ws.cell(r, 1).value
                if val is not None and str(val).strip():
                    raw_outcomes.append((r, str(val)))

            if not raw_outcomes:
                continue

            unique_raw = set(o[1] for o in raw_outcomes)
            
            # 1. Whitespace anomalies (leading/trailing whitespace)
            for r, o_str in raw_outcomes:
                if o_str.strip() != o_str:
                    discrepancies += 1
                    self.add_issue(
                        4, "WARN", sname, f"A{r}", r, "Outcome", repr(o_str), o_str.strip(),
                        f"Outcome string contains leading or trailing whitespace: {repr(o_str)}."
                    )

            # 2. Casing discrepancies
            lower_map: Dict[str, Set[str]] = {}
            for o_str in unique_raw:
                lower_map.setdefault(o_str.strip().lower(), set()).add(o_str.strip())
            
            for l_str, variants in lower_map.items():
                if len(variants) > 1:
                    discrepancies += 1
                    self.add_issue(
                        4, "ERROR", sname, "Col A", 0, "Outcome", ", ".join(sorted(variants)),
                        list(variants)[0],
                        f"Casing discrepancy detected for outcome '{l_str}': {list(variants)}."
                    )

            # 3. Synonym Clashes within the same sheet
            # Filter out rows that are purely administrative exclusion notes with zero quantitative data
            active_outcomes = [
                o[1].strip() for o in raw_outcomes
                if not self._is_administrative_exclusion_row(ws, o[0], o[1], sname)
            ]
            unique_clean = sorted(list(set(active_outcomes)))
            for cluster in TAXONOMY_SYNONYM_CLUSTERS:
                c_name = cluster["cluster_name"]
                terms = cluster["terms"]
                diffs = cluster["differentiators"]
                
                # Find outcomes that hit this cluster
                matched = []
                for u in unique_clean:
                    u_lower = u.lower()
                    # If it explicitly matches one of the cluster terms
                    hit = any(re.search(rf"\b{re.escape(t)}\b", u_lower) for t in terms)
                    if hit:
                        # Check if it has an explicit differentiator making it genuinely distinct
                        has_diff = any(re.search(rf"\b{re.escape(d)}\b", u_lower) for d in diffs)
                        matched.append((u, has_diff))

                # If there are 2 or more non-differentiated variants of the same concept
                # e.g. "Mortality" and "Death" in the same sheet without differentiating descriptors
                non_diff_matched = [m[0] for m in matched if not m[1]]
                if len(non_diff_matched) > 1:
                    discrepancies += 1
                    self.add_issue(
                        4, "ERROR", sname, "Col A", 0, "Outcome", " vs ".join(non_diff_matched),
                        f"Standardized term from '{c_name}'",
                        f"Synonym clash in {sname}: {non_diff_matched}. Biological endpoints must be standardized to character-identical strings."
                    )

        # Gate 4 scoring: 20 pts minus 5 per discrepancy
        self.gate4_score = max(0, 20 - (discrepancies * 5))

    # --------------------------------------------------------------------------
    # GATE 5: Unit Isolation & Risk of Bias Worksheets
    # --------------------------------------------------------------------------
    def audit_gate5_units_and_rob(self):
        """Audits unit isolation and verifies completeness of Risk of Bias sheets."""
        if not self.wb:
            return

        unit_errors = 0
        rob_errors = 0

        # 1. Unit Isolation in Continuous Sheets
        continuous_sheets = ["Mean Difference", "Simple mean", "Before-After"]
        for sname in continuous_sheets:
            if sname not in self.wb.sheetnames:
                continue
            ws = self.wb[sname]
            rows = self.scan_rows(ws, start_row=4)
            if not rows:
                continue
            
            # Check unit column (typically Col 4 or 14)
            for r in rows:
                u1 = ws.cell(r, 4).value
                u2 = ws.cell(r, 14).value if ws.max_column >= 14 else None
                # If continuous outcome is present, unit must be indicated somewhere
                out_name = ws.cell(r, 1).value
                if out_name and not u1 and not u2:
                    unit_errors += 1
                    self.add_issue(
                        5, "WARN", sname, f"D{r}", r, "Unit", "None", "Physical unit (e.g. mmol/L, g, days)",
                        f"Missing physical measurement unit for continuous outcome '{out_name}'."
                    )

        # 2. Risk of Bias Worksheets Validation
        rob_sheet_names = ["RoB2", "QUIPS", "ROBINS", "QUADAS", "Joanna-Briggs"]
        available_rob = [s for s in rob_sheet_names if s in self.wb.sheetnames]
        
        has_outcome_data = False
        for s in ["ORs - RRs", "Mean Difference", "Simple mean", "Regression coefficient"]:
            if s in self.wb.sheetnames and len(self.scan_rows(self.wb[s], start_row=4)) > 0:
                has_outcome_data = True
                break

        if has_outcome_data and not available_rob:
            rob_errors += 1
            self.add_issue(
                5, "ERROR", "Workbook", "N/A", 0, "RoB Sheets", "None present",
                "At least one RoB sheet (RoB2, QUIPS, or ROBINS)",
                "Workbook has outcome data but no Risk of Bias appraisal sheet."
            )
        elif available_rob:
            # Audit populated RoB sheets
            total_rob_studies = 0
            unrated_studies = 0
            for r_sname in available_rob:
                ws_r = self.wb[r_sname]
                # Start row 2 for RoB sheets
                r_rows = self.scan_rows(ws_r, start_row=2, empty_limit=10)
                for r in r_rows:
                    study_cell = ws_r.cell(r, 1).value
                    if not study_cell or not str(study_cell).strip():
                        continue
                    
                    total_rob_studies += 1
                    study_str = str(study_cell).strip()
                    
                    # Check domain ratings in columns 2 to max_column
                    domain_vals = [ws_r.cell(r, c).value for c in range(2, min(ws_r.max_column + 1, 10))]
                    non_empty_domains = [v for v in domain_vals if v is not None and str(v).strip()]
                    
                    if not non_empty_domains:
                        unrated_studies += 1
                        self.add_issue(
                            5, "WARN", r_sname, f"B{r}:H{r}", r, "Domains", "ALL EMPTY",
                            "Cochrane / QUIPS domain ratings (Low, Moderate, High)",
                            f"Study '{study_str}' is registered in {r_sname} but has no domain risk ratings."
                        )
                    else:
                        # Check format of populated ratings
                        for col_idx, dv in enumerate(domain_vals, start=2):
                            if dv is None:
                                continue
                            dv_str = str(dv).strip().lower()
                            has_valid_keyword = any(kw in dv_str for kw in VALID_ROB_RATINGS)
                            if not has_valid_keyword:
                                self.add_issue(
                                    5, "WARN", r_sname, f"{ws_r.cell(r, col_idx).coordinate}", r,
                                    f"Domain {col_idx-1}", dv, "Valid rating (Low, Moderate, High, Unclear)",
                                    f"Unrecognized Risk of Bias judgment format: '{dv}'."
                                )

            if total_rob_studies > 0 and unrated_studies == total_rob_studies:
                # All studies are unrated placeholders
                rob_errors += 1
                self.add_issue(
                    5, "WARN", available_rob[0], "Sheet", 0, "RoB Ratings", "Unassessed studies",
                    "Completed risk of bias assessments",
                    "RoB sheet contains study placeholders but no completed domain assessments."
                )

        # Gate 5 scoring: 20 pts minus 5 per unit/rob error
        self.gate5_score = max(0, 20 - (unit_errors * 3) - (rob_errors * 5))

    # --------------------------------------------------------------------------
    # RUNNER & REPORT GENERATOR
    # --------------------------------------------------------------------------
    def run(self) -> Dict[str, Any]:
        if not self.load_workbook():
            self.total_score = 0
            return self.get_summary()

        self.audit_gate1_numeric()
        self.audit_gate2_mandatory_and_math()
        self.audit_gate3_unique_author_year()
        self.audit_gate4_taxonomy()
        self.audit_gate5_units_and_rob()

        # Compute total
        self.total_score = (
            self.gate1_score +
            self.gate2_score +
            self.gate3_score +
            self.gate4_score +
            self.gate5_score
        )
        return self.get_summary()

    def get_summary(self) -> Dict[str, Any]:
        threshold = 90 if self.strict else 85
        passed = (self.total_score >= threshold) and (not self.gate1_fatal)
        
        return {
            "file": self.filepath,
            "passed": passed,
            "gate1_fatal": self.gate1_fatal,
            "total_score": self.total_score,
            "threshold": threshold,
            "gate_scores": {
                "gate1_numeric": {"score": self.gate1_score, "max": 25, "fatal": self.gate1_fatal},
                "gate2_mandatory_math": {"score": self.gate2_score, "max": 20},
                "gate3_unique_studies": {"score": self.gate3_score, "max": 15},
                "gate4_taxonomy": {"score": self.gate4_score, "max": 20},
                "gate5_units_rob": {"score": self.gate5_score, "max": 20}
            },
            "issue_count": len(self.issues),
            "issues": self.issues
        }

    def print_report(self) -> int:
        summary = self.run()
        
        print("\n" + "=" * 78)
        print(f"{Colors.BOLD}{Colors.BLUE}   CTM BOOSTR DATA EXTRACTION LINTER REPORT (GP3 STANDARDS)   {Colors.RESET}")
        print("=" * 78)
        print(f"Target File: {Colors.BOLD}{self.filepath}{Colors.RESET}")
        print(f"Mode:        {'STRICT (>=90%)' if self.strict else 'STANDARD (>=85%)'}\n")

        # Table of Gates
        gates = [
            ("Gate 1: Numeric-Only Mandate (Fatal Gate)", self.gate1_score, 25, self.gate1_fatal),
            ("Gate 2: Mandatory Cells & Math Logic", self.gate2_score, 20, False),
            ("Gate 3: Unique Author_Year & Arms", self.gate3_score, 15, False),
            ("Gate 4: Outcome Taxonomy Consistency", self.gate4_score, 20, False),
            ("Gate 5: Unit Isolation & RoB Sheets", self.gate5_score, 20, False),
        ]

        print(f"{Colors.BOLD}{'Gate':<45} | {'Score':<10} | {'Status'}{Colors.RESET}")
        print("-" * 78)

        for name, score, max_s, is_fatal in gates:
            if is_fatal:
                status_str = f"{Colors.RED}[FATAL FAIL]{Colors.RESET}"
            elif score == max_s:
                status_str = f"{Colors.GREEN}[PASS]{Colors.RESET}"
            elif score >= max_s * 0.7:
                status_str = f"{Colors.YELLOW}[WARN]{Colors.RESET}"
            else:
                status_str = f"{Colors.RED}[FAIL]{Colors.RESET}"

            score_str = f"{score} / {max_s}"
            print(f"{name:<45} | {score_str:<10} | {status_str}")

        print("-" * 78)

        # Overall Score
        score_color = Colors.GREEN if summary["passed"] else Colors.RED
        print(f"\n{Colors.BOLD}Overall Compliance Score: {score_color}{self.total_score} / 100 pont ({self.total_score}%){Colors.RESET}")

        # Issues details
        if self.issues:
            print(f"\n{Colors.BOLD}DETEKTÁLT HIBÁK ÉS CELLAHIVATKOZÁSOK ({len(self.issues)} db):{Colors.RESET}")
            print("-" * 78)
            for idx, iss in enumerate(self.issues[:30], start=1):
                sev_color = Colors.RED if iss["severity"] in ["FATAL", "ERROR"] else Colors.YELLOW
                sev_tag = f"{sev_color}[{iss['severity']}]{Colors.RESET}"
                gate_tag = f"[GATE {iss['gate']}]"
                print(f"{idx}. {gate_tag}{sev_tag} Munkalap: '{iss['sheet']}', Cella: {Colors.BOLD}{iss['cell']}{Colors.RESET} (Sor {iss['row']})")
                print(f"   Oszlop: '{iss['column']}' | Talált: {repr(iss['found_value'])}")
                print(f"   ↳ {iss['message']}")
                if iss["expected"]:
                    print(f"   ↳ Elvárt: {iss['expected']}")
                print()
            
            if len(self.issues) > 30:
                print(f"   ... és további {len(self.issues) - 30} hiba (összesen: {len(self.issues)}).")

        print("=" * 78)
        if summary["passed"]:
            print(f"{Colors.GREEN}{Colors.BOLD}✅ DATA EXTRACTION VERDICT: APPROVED (CTM BoostR Ready){Colors.RESET}")
            print(f"{Colors.GREEN}Adattábla megfelel a CTM Template v9 és biostatisztikai szintéziskövetelményeknek.{Colors.RESET}")
            print("=" * 78 + "\n")
            return 0
        else:
            print(f"{Colors.RED}{Colors.BOLD}🛑 DATA EXTRACTION VERDICT: REJECTED BY CTM LINTER GATES{Colors.RESET}")
            if self.gate1_fatal:
                print(f"{Colors.RED}Gate 1 Kritikus Hiba: Szöveges/formázatlan érték található numerikus mezőben!{Colors.RESET}")
            else:
                print(f"{Colors.RED}Elért pontszám ({self.total_score}) < Elvárt küszöb ({summary['threshold']}).{Colors.RESET}")
            print(f"{Colors.YELLOW}Javítsd a fenti cellákat, mielőtt átadod a statisztikusnak vagy a mentori bírálatra bocsátod!{Colors.RESET}")
            print("=" * 78 + "\n")
            return 1


def resolve_project_workbook(project_slug: str) -> Optional[str]:
    """Finds the extraction workbook for a project in projects/<slug>/data/*.xlsx."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(base_dir, "projects", project_slug, "data"),
        os.path.join(base_dir, "projects", project_slug)
    ]
    for d in candidates:
        if os.path.exists(d):
            for fname in os.listdir(d):
                if fname.endswith(".xlsx") and ("extraction" in fname.lower() or "template" in fname.lower()):
                    return os.path.join(d, fname)
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Audit systematic review extraction workbooks against CTM BoostR standards.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--file", "-f", type=str, help="Path to Excel extraction workbook (.xlsx)")
    parser.add_argument("--project", "-p", type=str, help="Project slug to locate extraction workbook (e.g. meta_hyperglycaemia)")
    parser.add_argument("--strict", action="store_true", help="Enforce 90%% score threshold instead of 85%%")
    parser.add_argument("--json", action="store_true", help="Output audit results in JSON format")

    args = parser.parse_args()

    wb_path = args.file
    if not wb_path and args.project:
        wb_path = resolve_project_workbook(args.project)
        if not wb_path:
            print(f"{Colors.RED}Error: No extraction workbook found for project '{args.project}' in projects/{args.project}/data/*.xlsx{Colors.RESET}")
            sys.exit(1)

    if not wb_path:
        # Default fallback: check if neonatal_antibiotics or meta_hyperglycaemia exists
        wb_path = resolve_project_workbook("neonatal_antibiotics") or resolve_project_workbook("meta_hyperglycaemia")

    if not wb_path:
        print(f"{Colors.RED}Error: Please specify --file <path_to_excel> or --project <project_slug>{Colors.RESET}")
        sys.exit(1)

    linter = ExtractionLinter(filepath=wb_path, strict=args.strict)
    
    if args.json:
        result = linter.run()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result["passed"] else 1)
    else:
        sys.exit(linter.print_report())


if __name__ == "__main__":
    main()
