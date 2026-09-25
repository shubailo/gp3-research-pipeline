#!/usr/bin/env python3
"""
full_text_adjudicator.py — PRISMA 2020 Dual Independent Screening & Adjudication Engine
========================================================================================
GP3 Medical Research Pipeline — Phase 2/3 Quality Gate

Features:
  1. True Dual Independent Screening:
     - Decoupled Reviewer 1 (Clinical & Population Lead) and Reviewer 2 (Methodological & Exposure Lead).
     - Ingests two independent review files (--r1-file and --r2-file), OR evaluates columns in a unified sheet,
       OR executes isolated dual evaluation passes with zero cross-talk.
     - Strict methodological guard: Only calculates Cohen's Kappa (κ) if two genuinely independent evaluation
       streams are compared. Single-pass heuristics are strictly labeled "Automated Heuristic Pre-screening".
  2. Conflict Identification & Arbitration Table:
     - Automatically flags all discordant records (R1 != R2 or UNSURE).
     - Exports results/<project>/adjudication_conflicts.xlsx (.csv) with dedicated fields for human tie-breakers.
  3. Seamless Workflow Integration:
     - Can be invoked standalone or piped directly from src/screen_literature.py via --dual-adjudicate.
"""

import os
import sys
import io
import json
import argparse
import re
from datetime import datetime
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Safe Windows UTF-8 reconfigure without stream closure
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ─────────────────────────────────────────────────────────────────────────────
# 1. EVALUATION PROFILES (INDEPENDENT REVIEWER LOGIC)
# ─────────────────────────────────────────────────────────────────────────────

def reviewer_1_clinical(record: dict, project: str) -> dict:
    """
    Reviewer 1: Clinical Population & Primary Outcome Specialist.
    Focus: Target clinical disease, gestational age/vulnerability, patient-centered outcomes.
    """
    title = str(record.get("Title") or record.get("title") or "").strip()
    abstract = str(record.get("Abstract") or record.get("abstract") or "").strip()
    text = f"{title} {abstract}".lower()

    if project == "neonatal_antibiotics":
        # Check non-human / in vitro
        if any(a in title.lower() for a in ["piglet", "piglets", "rat", "mice", "murine", "in vitro"]):
            return {"decision": "EXCLUDE", "reason": "Preclinical: Animal/in vitro model", "reviewer": "R1_Clinical"}
        # Check adult / non-preterm
        if any(w in text for w in ["adult patients", "elderly", "postmenopausal", "geriatric"]):
            return {"decision": "EXCLUDE", "reason": "Population: Adult/geriatric population", "reviewer": "R1_Clinical"}
        # Population check: neonates / preterm
        has_neonate = any(w in text for w in ["neonate", "neonatal", "newborn", "preterm", "vlbw", "elbw", "infant"])
        if not has_neonate:
            return {"decision": "EXCLUDE", "reason": "Population: Non-neonatal cohort", "reviewer": "R1_Clinical"}
        # Clinical outcomes: NEC or Mortality or Sepsis
        has_outcome = any(w in text for w in ["nec", "enterocolitis", "mortality", "death", "died", "sepsis", "los", "bpd"])
        if not has_outcome:
            return {"decision": "UNSURE", "reason": "Outcome: Target clinical outcome unconfirmed in abstract", "reviewer": "R1_Clinical"}
        return {"decision": "INCLUDE", "reason": "Eligible: Preterm neonates with clinical outcomes evaluated", "reviewer": "R1_Clinical"}

    elif project == "meta_hyperglycaemia":
        # Check animal
        if any(a in title.lower() for a in ["piglet", "piglets", "swine", "rat", "rodent"]):
            return {"decision": "EXCLUDE", "reason": "Preclinical: Animal model", "reviewer": "R1_Clinical"}
        # Check HIE + Cooling
        has_hie_cooling = ("hie" in text or "encephalopathy" in text or "asphyxia" in text) and \
                          any(c in text for c in ["hypothermia", "cooling", "cooled", "ttm"])
        if not has_hie_cooling:
            return {"decision": "EXCLUDE", "reason": "Population: No therapeutic hypothermia in HIE", "reviewer": "R1_Clinical"}
        # Check Clinical Outcomes
        has_outcomes = any(o in text for o in ["mortality", "death", "neurodevelopment", "mri", "bayley", "seizure"])
        if not has_outcomes:
            return {"decision": "UNSURE", "reason": "Outcome: Long-term neurodevelopment/mortality not detailed", "reviewer": "R1_Clinical"}
        return {"decision": "INCLUDE", "reason": "Eligible: Human neonates with HIE undergoing cooling", "reviewer": "R1_Clinical"}

    else:
        # Generic clinical screen
        if len(text) < 50:
            return {"decision": "EXCLUDE", "reason": "Incomplete record", "reviewer": "R1_Clinical"}
        return {"decision": "INCLUDE", "reason": "Clinical screening criteria met", "reviewer": "R1_Clinical"}


def reviewer_2_methodological(record: dict, project: str) -> dict:
    """
    Reviewer 2: Methodological Rigor, Exposure Assignment & Study Design Specialist.
    Focus: Exposure duration/threshold, comparator definition, confounding, publication type.
    """
    title = str(record.get("Title") or record.get("title") or "").strip()
    abstract = str(record.get("Abstract") or record.get("abstract") or "").strip()
    text = f"{title} {abstract}".lower()

    # Publication type filter
    review_markers = ["systematic review", "meta-analysis", "narrative review", "practice guideline", "consensus statement", "editorial", "commentary"]
    if any(m in title.lower() for m in review_markers) and "protocol" not in title.lower():
        return {"decision": "EXCLUDE", "reason": "Design: Secondary literature / Review without primary data", "reviewer": "R2_Methodological"}

    if project == "neonatal_antibiotics":
        # Check antibiotic exposure duration analyzed
        has_duration = any(w in text for w in ["duration", "course", "days", "dot", "lot", "prolonged", "short", "hours", "stewardship", "discontinuation", "empiric"])
        if not has_duration:
            return {"decision": "EXCLUDE", "reason": "Exposure: No empiric antibiotic duration/comparison analyzed", "reviewer": "R2_Methodological"}
        # Check culture-negative / empiric context
        has_culture_context = any(w in text for w in ["culture-negative", "negative culture", "blood culture", "empiric", "empirical", "early-onset", "eos"])
        if not has_culture_context:
            return {"decision": "UNSURE", "reason": "Exposure: Culture-negative status unclear from abstract", "reviewer": "R2_Methodological"}
        return {"decision": "INCLUDE", "reason": "Eligible: Primary empirical antibiotic exposure with comparator analyzed", "reviewer": "R2_Methodological"}

    elif project == "meta_hyperglycaemia":
        # Exposure relevance: Hyperglycemia / blood glucose
        has_glucose = any(k in text for k in ["hyperglycemia", "hyperglycaemia", "blood glucose", "glycemic", "glucose level", "dysglycemia"])
        if not has_glucose:
            return {"decision": "EXCLUDE", "reason": "Exposure: No hyperglycemia / glucose exposure analyzed", "reviewer": "R2_Methodological"}
        # Quantitative data check
        has_quant = any(q in text for q in ["cohort", "prospective", "retrospective", "trial", "odds ratio", "hazard ratio", "patients", "n="])
        if not has_quant:
            return {"decision": "UNSURE", "reason": "Methodology: Quantitative effect estimate unclear in abstract", "reviewer": "R2_Methodological"}
        return {"decision": "INCLUDE", "reason": "Eligible: Quantitative glucose exposure with contrast analyzed", "reviewer": "R2_Methodological"}

    else:
        return {"decision": "INCLUDE", "reason": "Methodological criteria met", "reviewer": "R2_Methodological"}


# ─────────────────────────────────────────────────────────────────────────────
# 2. STATISTICAL AGREEMENT (COHEN'S KAPPA)
# ─────────────────────────────────────────────────────────────────────────────

def calculate_cohens_kappa(r1_decisions: list[str], r2_decisions: list[str]) -> dict:
    """
    Computes Cohen's kappa (κ) between two independent reviewers.
    Binary categorization: POSITIVE (INCLUDE) vs NEGATIVE (EXCLUDE / UNSURE).
    """
    if len(r1_decisions) != len(r2_decisions) or len(r1_decisions) == 0:
        return {"kappa": 0.0, "observed_agreement": 0.0, "interpretation": "Insufficient data"}

    # Binary normalization: INCLUDE -> 1, others -> 0
    bin_r1 = [1 if str(d).upper().startswith("INC") else 0 for d in r1_decisions]
    bin_r2 = [1 if str(d).upper().startswith("INC") else 0 for d in r2_decisions]

    total = len(bin_r1)
    a = sum(1 for i in range(total) if bin_r1[i] == 1 and bin_r2[i] == 1)  # Both Include
    b = sum(1 for i in range(total) if bin_r1[i] == 1 and bin_r2[i] == 0)  # R1 Inc, R2 Exc
    c = sum(1 for i in range(total) if bin_r1[i] == 0 and bin_r2[i] == 1)  # R1 Exc, R2 Inc
    d = sum(1 for i in range(total) if bin_r1[i] == 0 and bin_r2[i] == 0)  # Both Exclude

    po = (a + d) / total
    pe = (((a + b) / total) * ((a + c) / total)) + (((c + d) / total) * ((b + d) / total))

    if pe >= 1.0:
        kappa = 1.0
    else:
        kappa = (po - pe) / (1.0 - pe)

    if kappa >= 0.81:
        interp = "Almost Perfect Agreement (PRISMA Gold Standard)"
    elif kappa >= 0.61:
        interp = "Substantial Agreement (Standard Methodological Rigor)"
    elif kappa >= 0.41:
        interp = "Moderate Agreement (Reviewer Calibration Recommended)"
    elif kappa >= 0.21:
        interp = "Fair Agreement (Significant Inter-Reviewer Divergence)"
    else:
        interp = "Poor Agreement (Urgent Arbitration Required)"

    return {
        "total_screened": total,
        "both_include": a,
        "r1_only_include": b,
        "r2_only_include": c,
        "both_exclude": d,
        "observed_agreement_pct": round(po * 100, 2),
        "chance_agreement_pct": round(pe * 100, 2),
        "cohens_kappa": round(kappa, 3),
        "interpretation": interp
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. WORKBOOK GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def export_adjudication_workbooks(
    consensus_inc: list[dict],
    consensus_exc: list[dict],
    conflicts: list[dict],
    stats: dict,
    project: str,
    output_dir: str,
    is_genuinely_dual: bool
) -> tuple[str, str]:
    """Generates styled consensus workbook and dedicated conflict arbitration sheet."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Paths
    master_xlsx = os.path.join(output_dir, "adjudication_consensus.xlsx")
    conflicts_xlsx = os.path.join(output_dir, "adjudication_conflicts.xlsx")
    conflicts_csv = os.path.join(output_dir, "adjudication_conflicts.csv")

    border_thin = Border(
        left=Side(style='thin', color='E0E0E0'),
        right=Side(style='thin', color='E0E0E0'),
        top=Side(style='thin', color='E0E0E0'),
        bottom=Side(style='thin', color='E0E0E0')
    )

    # ── 1. CONFLICTS WORKBOOK (adjudication_conflicts.xlsx) ────────────────────
    wb_conf = Workbook()
    ws_c = wb_conf.active
    ws_c.title = "Adjudication Conflicts"

    headers_conf = [
        "Record_ID", "PMID", "DOI", "Year", "First_Author", "Journal",
        "R1_Decision", "R1_Rationale", "R2_Decision", "R2_Rationale",
        "Conflict_Type", "Human_Arbiter_Decision", "Arbitration_Rationale", "Title", "Abstract"
    ]
    ws_c.append(headers_conf)

    header_fill_orange = PatternFill(start_color="D35400", end_color="D35400", fill_type="solid")
    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

    for col_idx in range(1, len(headers_conf) + 1):
        cell = ws_c.cell(row=1, column=col_idx)
        cell.fill = header_fill_orange
        cell.font = font_header
        cell.alignment = Alignment(horizontal="center", vertical="center")

    fill_conflict_row = PatternFill(start_color="FEF9E7", end_color="FEF9E7", fill_type="solid")
    fill_arbiter_col = PatternFill(start_color="FCF3CF", end_color="FCF3CF", fill_type="solid")

    for row_idx, item in enumerate(conflicts, start=2):
        row_vals = [
            str(item.get("Record_ID", row_idx - 1)),
            str(item.get("PMID", "")).replace(".0", ""),
            str(item.get("DOI", "")),
            str(item.get("Year", "")).replace(".0", ""),
            str(item.get("First_Author", item.get("author", ""))),
            str(item.get("Journal", "")),
            str(item.get("R1_Decision", "")),
            str(item.get("R1_Rationale", "")),
            str(item.get("R2_Decision", "")),
            str(item.get("R2_Rationale", "")),
            str(item.get("Conflict_Type", "Discordant (R1 != R2)")),
            str(item.get("Human_Arbiter_Decision", "")),  # Empty for human filling
            str(item.get("Arbitration_Rationale", "")),   # Empty for human filling
            str(item.get("Title") or item.get("title") or ""),
            str(item.get("Abstract") or item.get("abstract") or "")[:500]
        ]
        ws_c.append(row_vals)
        for col_idx in range(1, len(headers_conf) + 1):
            c = ws_c.cell(row=row_idx, column=col_idx)
            c.border = border_thin
            c.fill = fill_arbiter_col if col_idx in [12, 13] else fill_conflict_row
            if col_idx in [1, 2, 4, 7, 9, 11]:
                c.alignment = Alignment(horizontal="center", vertical="top")
            elif col_idx in [8, 10, 14, 15]:
                c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
                c.font = Font(name="Calibri", size=9)
            else:
                c.alignment = Alignment(horizontal="left", vertical="top")

    col_widths_c = {"A": 10, "B": 12, "C": 22, "D": 8, "E": 18, "F": 22, "G": 14, "H": 30, "I": 14, "J": 30, "K": 22, "L": 22, "M": 32, "N": 40, "O": 50}
    for col_let, w in col_widths_c.items():
        ws_c.column_dimensions[col_let].width = w

    ws_c.freeze_panes = "A2"
    wb_conf.save(conflicts_xlsx)

    # Export conflicts CSV
    df_conf = pd.DataFrame(conflicts)
    if not df_conf.empty:
        df_conf.to_csv(conflicts_csv, index=False, encoding="utf-8-sig")

    # ── 2. MASTER ADJUDICATION WORKBOOK (adjudication_consensus.xlsx) ─────────
    wb_mast = Workbook()

    # Sheet 1: Consensus Included
    ws_inc = wb_mast.active
    ws_inc.title = "Consensus Included"
    headers_inc = ["Record_ID", "PMID", "DOI", "Year", "First_Author", "Journal", "R1_Decision", "R2_Decision", "Title", "Extraction_Status"]
    ws_inc.append(headers_inc)
    header_fill_green = PatternFill(start_color="1E4620", end_color="1E4620", fill_type="solid")
    for col_idx in range(1, len(headers_inc) + 1):
        cell = ws_inc.cell(row=1, column=col_idx)
        cell.fill = header_fill_green
        cell.font = font_header
        cell.alignment = Alignment(horizontal="center", vertical="center")

    fill_inc_row = PatternFill(start_color="EAF2E8", end_color="EAF2E8", fill_type="solid")
    for row_idx, item in enumerate(consensus_inc, start=2):
        row_vals = [
            str(item.get("Record_ID", row_idx - 1)),
            str(item.get("PMID", "")).replace(".0", ""),
            str(item.get("DOI", "")),
            str(item.get("Year", "")).replace(".0", ""),
            str(item.get("First_Author", item.get("author", ""))),
            str(item.get("Journal", "")),
            str(item.get("R1_Decision", "INCLUDE")),
            str(item.get("R2_Decision", "INCLUDE")),
            str(item.get("Title", item.get("title", ""))),
            "ELIGIBLE FOR EXTRACTION"
        ]
        ws_inc.append(row_vals)
        for col_idx in range(1, len(headers_inc) + 1):
            c = ws_inc.cell(row=row_idx, column=col_idx)
            c.border = border_thin
            c.fill = fill_inc_row
            if col_idx in [1, 2, 4, 7, 8]:
                c.alignment = Alignment(horizontal="center", vertical="top")
            elif col_idx == 9:
                c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
            else:
                c.alignment = Alignment(horizontal="left", vertical="top")

    ws_inc.freeze_panes = "A2"

    # Sheet 2: Consensus Excluded
    ws_exc = wb_mast.create_sheet(title="Consensus Excluded")
    headers_exc = ["Record_ID", "PMID", "DOI", "Year", "First_Author", "Journal", "Exclusion_Reason", "R1_Rationale", "R2_Rationale", "Title"]
    ws_exc.append(headers_exc)
    header_fill_red = PatternFill(start_color="78281F", end_color="78281F", fill_type="solid")
    for col_idx in range(1, len(headers_exc) + 1):
        cell = ws_exc.cell(row=1, column=col_idx)
        cell.fill = header_fill_red
        cell.font = font_header
        cell.alignment = Alignment(horizontal="center", vertical="center")

    fill_exc_row = PatternFill(start_color="FDEDEC", end_color="FDEDEC", fill_type="solid")
    for row_idx, item in enumerate(consensus_exc, start=2):
        row_vals = [
            str(item.get("Record_ID", row_idx - 1)),
            str(item.get("PMID", "")).replace(".0", ""),
            str(item.get("DOI", "")),
            str(item.get("Year", "")).replace(".0", ""),
            str(item.get("First_Author", item.get("author", ""))),
            str(item.get("Journal", "")),
            str(item.get("Exclusion_Reason", item.get("R1_Rationale", "Excluded"))),
            str(item.get("R1_Rationale", "")),
            str(item.get("R2_Rationale", "")),
            str(item.get("Title", item.get("title", "")))
        ]
        ws_exc.append(row_vals)
        for col_idx in range(1, len(headers_exc) + 1):
            c = ws_exc.cell(row=row_idx, column=col_idx)
            c.border = border_thin
            c.fill = fill_exc_row
            if col_idx in [1, 2, 4]:
                c.alignment = Alignment(horizontal="center", vertical="top")
            elif col_idx in [7, 8, 9, 10]:
                c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
                c.font = Font(name="Calibri", size=9)
            else:
                c.alignment = Alignment(horizontal="left", vertical="top")

    ws_exc.freeze_panes = "A2"

    # Sheet 3: PRISMA & Agreement Metrics
    ws_met = wb_mast.create_sheet(title="PRISMA Agreement Metrics")
    ws_met.column_dimensions["A"].width = 38
    ws_met.column_dimensions["B"].width = 24
    ws_met.column_dimensions["C"].width = 45

    header_fill_blue = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    ws_met.append(["PRISMA Screening & Adjudication Metric", "Value", "Methodological Standard"])
    for col_idx in range(1, 4):
        c = ws_met.cell(row=1, column=col_idx)
        c.fill = header_fill_blue
        c.font = font_header
        c.alignment = Alignment(horizontal="center", vertical="center")

    kappa_val_str = str(stats.get("cohens_kappa", "N/A")) if is_genuinely_dual else "N/A (Heuristic Pre-screening)"
    interp_str = stats.get("interpretation", "N/A") if is_genuinely_dual else "Single-Pass Heuristic (Kappa not applicable)"

    metric_rows = [
        ("Total Records Evaluated", stats.get("total_screened", len(consensus_inc) + len(consensus_exc) + len(conflicts)), "PRISMA 2020 Item 8"),
        ("Consensus INCLUDED (Ready for Extraction)", len(consensus_inc), "Agreed by both independent review streams"),
        ("Consensus EXCLUDED (Definitive Ineligible)", len(consensus_exc), "Concordantly excluded by both review streams"),
        ("DISCORDANT CONFLICTS (Human Arbitration)", len(conflicts), "Items logged to adjudication_conflicts.xlsx"),
        ("Screening Mode", "Dual Independent Screening" if is_genuinely_dual else "Automated Heuristic Pre-screening", "Cochrane Handbook Section 4.6"),
        ("Observed Agreement Rate (%)", f"{stats.get('observed_agreement_pct', 0.0)}%", "Po = (a + d) / Total"),
        ("Chance Agreement Rate (%)", f"{stats.get('chance_agreement_pct', 0.0)}%", "Pe = P(Inc)P(Inc) + P(Exc)P(Exc)"),
        ("Cohen's Kappa (κ)", kappa_val_str, "PRISMA Gold Standard (>=0.60 required)"),
        ("Kappa Interpretation", interp_str, "Landis & Koch (1977) scale")
    ]

    for r_idx, r_data in enumerate(metric_rows, start=2):
        ws_met.append(list(r_data))
        for col_idx in range(1, 4):
            c = ws_met.cell(row=r_idx, column=col_idx)
            c.border = border_thin
            if col_idx == 2:
                c.alignment = Alignment(horizontal="center", vertical="center")
                c.font = Font(name="Calibri", size=11, bold=True)
            else:
                c.alignment = Alignment(horizontal="left", vertical="center")

    wb_mast.save(master_xlsx)
    return master_xlsx, conflicts_xlsx


# ─────────────────────────────────────────────────────────────────────────────
# 4. MAIN ORCHESTRATION PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

def run_adjudication(
    records: list[dict],
    project: str,
    output_dir: str,
    r1_col: str = None,
    r2_col: str = None,
    is_genuinely_dual: bool = False
) -> dict:
    """Core adjudication execution pipeline."""
    print(f"\n>>> Running PRISMA Adjudication on {len(records)} records (Project: {project})...")
    print(f"    Mode: {'Dual Independent Screening' if is_genuinely_dual else 'Automated Heuristic Pre-screening'}")

    r1_decisions = []
    r2_decisions = []
    
    consensus_inc = []
    consensus_exc = []
    conflicts = []

    for idx, rec in enumerate(records, 1):
        rec_id = rec.get("Record_ID") or rec.get("record_id") or idx

        # Determine R1 decision
        if r1_col and r1_col in rec and pd.notna(rec[r1_col]):
            r1_d = str(rec[r1_col]).upper().strip()
            r1_r = str(rec.get("R1_Rationale", rec.get("R1_Reviewer_Notes", "Recorded in dataset"))).strip()
        else:
            eval_r1 = reviewer_1_clinical(rec, project)
            r1_d = eval_r1["decision"]
            r1_r = eval_r1["reason"]

        # Determine R2 decision
        if r2_col and r2_col in rec and pd.notna(rec[r2_col]):
            r2_d = str(rec[r2_col]).upper().strip()
            r2_r = str(rec.get("R2_Rationale", rec.get("R2_Reviewer_Notes", "Recorded in dataset"))).strip()
        else:
            eval_r2 = reviewer_2_methodological(rec, project)
            r2_d = eval_r2["decision"]
            r2_r = eval_r2["reason"]

        r1_decisions.append(r1_d)
        r2_decisions.append(r2_d)

        annotated = {
            **rec,
            "Record_ID": rec_id,
            "R1_Decision": r1_d,
            "R1_Rationale": r1_r,
            "R2_Decision": r2_d,
            "R2_Rationale": r2_r
        }

        # Adjudication logic
        is_r1_inc = r1_d.startswith("INC")
        is_r2_inc = r2_d.startswith("INC")
        is_r1_exc = r1_d.startswith("EXC")
        is_r2_exc = r2_d.startswith("EXC")

        if is_r1_inc and is_r2_inc:
            annotated["Adjudication_Status"] = "CONSENSUS_INCLUDE"
            consensus_inc.append(annotated)
        elif is_r1_exc and is_r2_exc:
            annotated["Adjudication_Status"] = "CONSENSUS_EXCLUDE"
            annotated["Exclusion_Reason"] = r1_r if len(r1_r) > len(r2_r) else r2_r
            consensus_exc.append(annotated)
        else:
            annotated["Adjudication_Status"] = "CONFLICT_NEEDS_ARBITRATION"
            if is_r1_inc and is_r2_exc:
                annotated["Conflict_Type"] = "Discordant: R1 Include vs R2 Exclude"
            elif is_r1_exc and is_r2_inc:
                annotated["Conflict_Type"] = "Discordant: R1 Exclude vs R2 Include"
            else:
                annotated["Conflict_Type"] = f"Unsure Flag: R1({r1_d}) vs R2({r2_d})"
            annotated["Human_Arbiter_Decision"] = ""  # Left empty for human decision
            annotated["Arbitration_Rationale"] = ""   # Left empty for human rationale
            conflicts.append(annotated)

    # Statistical evaluation
    if is_genuinely_dual:
        stats = calculate_cohens_kappa(r1_decisions, r2_decisions)
    else:
        # Prevent fake kappa
        stats = {
            "total_screened": len(records),
            "both_include": len(consensus_inc),
            "both_exclude": len(consensus_exc),
            "conflicts": len(conflicts),
            "observed_agreement_pct": round((len(consensus_inc) + len(consensus_exc)) / len(records) * 100, 2) if records else 0.0,
            "chance_agreement_pct": 0.0,
            "cohens_kappa": "N/A",
            "interpretation": "Single-Pass Heuristic Pre-screening (Kappa not applicable to avoid false rigor)"
        }

    # Export workbooks
    master_path, conflict_path = export_adjudication_workbooks(
        consensus_inc=consensus_inc,
        consensus_exc=consensus_exc,
        conflicts=conflicts,
        stats=stats,
        project=project,
        output_dir=output_dir,
        is_genuinely_dual=is_genuinely_dual
    )

    # Export JSON summary
    summary_path = os.path.join(output_dir, "adjudication_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "project": project,
            "timestamp": datetime.now().isoformat(),
            "mode": "Dual Independent Screening" if is_genuinely_dual else "Automated Heuristic Pre-screening",
            "stats": stats,
            "counts": {
                "total": len(records),
                "consensus_included": len(consensus_inc),
                "consensus_excluded": len(consensus_exc),
                "conflicts_requiring_human_arbitration": len(conflicts)
            },
            "artifacts": {
                "master_workbook": master_path,
                "conflict_workbook": conflict_path
            }
        }, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 72)
    print("  PRISMA 2020 ADJUDICATION COMPLETE")
    print("=" * 72)
    print(f"  Total records assessed:             {len(records):>5}")
    print(f"  Consensus INCLUDED for extraction:  {len(consensus_inc):>5}")
    print(f"  Consensus EXCLUDED:                 {len(consensus_exc):>5}")
    print(f"  DISCORDANT CONFLICTS (Human Arb.):  {len(conflicts):>5}")
    if is_genuinely_dual:
        print(f"  Cohen's Kappa (κ):                  {stats['cohens_kappa']:>5} ({stats['interpretation']})")
    else:
        print(f"  Cohen's Kappa:                      [N/A - Methodological Guard Applied]")
    print(f"  Conflict Workbook saved:            {conflict_path}")
    print(f"  Master Workbook saved:              {master_path}")
    print("=" * 72 + "\n")

    return {
        "consensus_included": len(consensus_inc),
        "consensus_excluded": len(consensus_exc),
        "conflicts": len(conflicts),
        "master_path": master_path,
        "conflict_path": conflict_path,
        "summary_path": summary_path
    }


def main():
    parser = argparse.ArgumentParser(description="PRISMA 2020 Dual Independent Screening & Adjudication Engine")
    parser.add_argument("--project", default="neonatal_antibiotics", help="Project slug (e.g. neonatal_antibiotics, meta_hyperglycaemia)")
    parser.add_argument("--input", help="Path to candidates CSV/XLSX/JSON file")
    parser.add_argument("--r1-file", help="Path to independent Reviewer 1 decisions JSON/CSV")
    parser.add_argument("--r2-file", help="Path to independent Reviewer 2 decisions JSON/CSV")
    parser.add_argument("--r1-col", help="Column name for Reviewer 1 decision in unified sheet")
    parser.add_argument("--r2-col", help="Column name for Reviewer 2 decision in unified sheet")
    parser.add_argument("--output-dir", help="Output directory for adjudication artifacts")
    
    args = parser.parse_args()

    # Determine default paths if not provided
    output_dir = args.output_dir or os.path.join(WORKSPACE_DIR, "results", args.project)

    records = []
    is_genuinely_dual = False

    # Scenario 1: Separate R1 and R2 files provided
    if args.r1_file and args.r2_file:
        is_genuinely_dual = True
        print(f"Loading Independent Reviewer 1: {args.r1_file}")
        print(f"Loading Independent Reviewer 2: {args.r2_file}")
        # Load R1
        df_r1 = pd.read_json(args.r1_file) if args.r1_file.endswith(".json") else pd.read_csv(args.r1_file)
        df_r2 = pd.read_json(args.r2_file) if args.r2_file.endswith(".json") else pd.read_csv(args.r2_file)
        
        # Merge on DOI or Title or Record_ID
        records = df_r1.to_dict(orient="records")
        r2_dict = {str(r.get("DOI", r.get("Title", ""))): r for r in df_r2.to_dict(orient="records")}
        for rec in records:
            key = str(rec.get("DOI", rec.get("Title", "")))
            if key in r2_dict:
                rec["R2_Decision"] = r2_dict[key].get("decision") or r2_dict[key].get("R2_Decision", "EXCLUDE")
                rec["R2_Rationale"] = r2_dict[key].get("reason") or r2_dict[key].get("R2_Rationale", "")

    # Scenario 2: Input file provided
    elif args.input:
        in_path = args.input if os.path.isabs(args.input) else os.path.join(WORKSPACE_DIR, args.input)
        if not os.path.exists(in_path):
            print(f"❌ Input file not found: {in_path}")
            sys.exit(1)
        
        if in_path.endswith(".xlsx") or in_path.endswith(".xls"):
            df_in = pd.read_excel(in_path)
        elif in_path.endswith(".json"):
            with open(in_path, "r", encoding="utf-8") as f:
                raw_j = json.load(f)
            df_in = pd.DataFrame(raw_j if isinstance(raw_j, list) else raw_j.get("included", []) + raw_j.get("unsure", []))
        else:
            df_in = pd.read_csv(in_path, encoding="utf-8-sig")

        records = df_in.to_dict(orient="records")

        # Check if unified sheet already contains two distinct reviewer columns
        if args.r1_col and args.r2_col and args.r1_col in df_in.columns and args.r2_col in df_in.columns:
            is_genuinely_dual = True
        elif "R1_Shubail_Decision" in df_in.columns and "CoLead_Dori_Decision" in df_in.columns:
            # Check if both have decisions
            non_null_r1 = df_in["R1_Shubail_Decision"].dropna().count()
            non_null_r2 = df_in["CoLead_Dori_Decision"].dropna().count()
            if non_null_r1 > 0 and non_null_r2 > 0:
                is_genuinely_dual = True
                args.r1_col = "R1_Shubail_Decision"
                args.r2_col = "CoLead_Dori_Decision"

    # Scenario 3: Fallback project defaults
    else:
        if args.project == "meta_hyperglycaemia":
            in_path = os.path.join(WORKSPACE_DIR, "meta_hyperglycaemia", "screening_decisions_review.csv")
            if os.path.exists(in_path):
                df_in = pd.read_csv(in_path, encoding="utf-8-sig")
                records = df_in[df_in.get("Decision") == "INCLUDED"].to_dict(orient="records")
        elif args.project == "neonatal_antibiotics":
            in_path = os.path.join(WORKSPACE_DIR, "results", "neonatal_antibiotics", "pilot_screening_100.xlsx")
            if os.path.exists(in_path):
                df_in = pd.read_excel(in_path)
                records = df_in.to_dict(orient="records")
                if "AI_Decision" in df_in.columns and "R1_Shubail_Decision" in df_in.columns:
                    if df_in["AI_Decision"].dropna().count() > 0 and df_in["R1_Shubail_Decision"].dropna().count() > 0:
                        is_genuinely_dual = True
                        args.r1_col = "AI_Decision"
                        args.r2_col = "R1_Shubail_Decision"

    if not records:
        print(f"❌ No records loaded for adjudication in project '{args.project}'. Specify --input.")
        sys.exit(1)

    run_adjudication(
        records=records,
        project=args.project,
        output_dir=output_dir,
        r1_col=args.r1_col,
        r2_col=args.r2_col,
        is_genuinely_dual=is_genuinely_dual
    )

if __name__ == "__main__":
    main()
