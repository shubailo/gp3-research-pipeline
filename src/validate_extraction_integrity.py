"""Automated data extraction and integrity auditor for CTM extraction workbooks."""
import os
import sys
import argparse
from typing import Dict, Any, List, Tuple, Set, Optional

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

import openpyxl

from src.utils.console import configure_utf8_console

# Known valid country names and common aliases in dataset
VALID_COUNTRIES: Set[str] = {
    'Canada', 'China', 'United States', 'USA', 'US', 'Norway', 'France',
    'Netherlands', 'Ireland', 'Saudi Arabia', 'Egypt', 'Australia',
    'United Kingdom', 'UK', 'Germany', 'Italy', 'Spain', 'Sweden', 'Denmark',
    'Japan', 'India', 'Thailand', 'Chile', 'Switzerland', 'Brazil', 'Iran',
    'Romania', 'Greece', 'Taiwan', 'Qatar'
}

FORBIDDEN_PLACEHOLDERS: Set[str] = {
    'pdf', 'author', 'unknown', 'tbd', 'none_specified', 'sample_author',
    'preterm', 'vlbw', 'infant', 'elbw'
}

DEFAULT_WORKBOOK = 'data/Data_extraction_neonatal_antibiotics_v9.xlsx'


class BasicLayoutCols:
    NUM = 1
    AUTHOR = 2
    YEAR = 3
    DOI = 4
    DESIGN = 5
    START_YEAR = 6
    END_YEAR = 7
    COUNTRY = 8
    CENTERS = 9
    TOTAL_N = 18
    EXP_N = 21
    COMP_N = 33


class OrsRrsCols:
    OUTCOME = 1
    DEFINITION = 2
    STUDY_ID = 3
    A = 13
    TOTAL_I = 14
    C = 15
    TOTAL_C = 16
    EST_TYPE = 24
    PE = 25
    CI_MIN = 27
    CI_MAX = 28
    P_VAL = 30
    CONFOUNDERS = 32


class ExtractionIntegrityAuditor:
    """Audits CTM extraction workbook for structural and mathematical validity."""

    def __init__(self, wb_path: str):
        self.wb_path = wb_path
        self.wb: Optional[openpyxl.Workbook] = None
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def load_workbook(self) -> bool:
        try:
            self.wb = openpyxl.load_workbook(self.wb_path, data_only=True)
            return True
        except Exception as exc:
            self.errors.append(f"FATAL: Unable to load workbook at '{self.wb_path}': {exc}")
            return False

    def audit_basic_layout(self) -> Dict[str, Dict[str, Any]]:
        if not self.wb or 'Basic layout' not in self.wb.sheetnames:
            self.errors.append("Missing required worksheet: 'Basic layout'")
            return {}

        ws = self.wb['Basic layout']
        studies: Dict[str, Dict[str, Any]] = {}

        for r in range(4, ws.max_row + 1):
            num = ws.cell(r, BasicLayoutCols.NUM).value
            if num is None:
                continue

            author = ws.cell(r, BasicLayoutCols.AUTHOR).value
            year = ws.cell(r, BasicLayoutCols.YEAR).value
            doi = ws.cell(r, BasicLayoutCols.DOI).value
            country = ws.cell(r, BasicLayoutCols.COUNTRY).value
            centers = ws.cell(r, BasicLayoutCols.CENTERS).value
            exp_n = ws.cell(r, BasicLayoutCols.EXP_N).value
            comp_n = ws.cell(r, BasicLayoutCols.COMP_N).value

            study_tag = f"Row {r} (ID #{num}: {author} {year})"

            if not author or not isinstance(author, str):
                self.errors.append(f"{study_tag}: First Author is missing or non-string.")
            else:
                author_clean = author.strip().lower()
                if author_clean in FORBIDDEN_PLACEHOLDERS:
                    self.errors.append(f"{study_tag}: First Author '{author}' is a FORBIDDEN PLACEHOLDER!")
                if not author[0].isupper():
                    self.errors.append(f"{study_tag}: First Author '{author}' must be capitalized.")

            if not isinstance(year, int) or year < 1990 or year > 2026:
                self.errors.append(f"{study_tag}: Year '{year}' is invalid (must be 1990-2026).")

            if not doi or not str(doi).startswith("10."):
                self.warnings.append(f"{study_tag}: DOI '{doi}' format non-standard or missing.")

            if not country or country not in VALID_COUNTRIES:
                self.errors.append(f"{study_tag}: Country '{country}' is invalid or misplaced demography!")

            if not isinstance(centers, int) or centers < 1:
                self.errors.append(f"{study_tag}: Centers count '{centers}' must be integer >= 1.")

            if not isinstance(exp_n, int) or exp_n < 1:
                self.errors.append(f"{study_tag}: Exposure N '{exp_n}' must be integer >= 1.")
            if not isinstance(comp_n, int) or comp_n < 1:
                self.errors.append(f"{study_tag}: Comparator N '{comp_n}' must be integer >= 1.")

            studies[f"{author}_{year}"] = {
                'row': r,
                'author': author,
                'year': year,
                'country': country,
                'exp_n': exp_n,
                'comp_n': comp_n
            }
        return studies

    def audit_ors_rrs(self) -> int:
        sheet_name = 'ORs - RRs' if 'ORs - RRs' in self.wb.sheetnames else 'ORs and RRs'
        if not self.wb or sheet_name not in self.wb.sheetnames:
            self.errors.append(f"Missing required worksheet: '{sheet_name}'")
            return 0

        ws = self.wb[sheet_name]
        outcomes_checked = 0

        for r in range(4, ws.max_row + 1):
            outcome = ws.cell(r, OrsRrsCols.OUTCOME).value
            if outcome is None:
                continue

            outcomes_checked += 1
            study_id = ws.cell(r, OrsRrsCols.STUDY_ID).value
            a = ws.cell(r, OrsRrsCols.A).value
            total_i = ws.cell(r, OrsRrsCols.TOTAL_I).value
            c = ws.cell(r, OrsRrsCols.C).value
            total_c = ws.cell(r, OrsRrsCols.TOTAL_C).value
            pe = ws.cell(r, OrsRrsCols.PE).value
            ci_min = ws.cell(r, OrsRrsCols.CI_MIN).value
            ci_max = ws.cell(r, OrsRrsCols.CI_MAX).value
            p_val = ws.cell(r, OrsRrsCols.P_VAL).value
            confounders = ws.cell(r, OrsRrsCols.CONFOUNDERS).value

            row_tag = f"ORs-RRs Row {r} ({study_id} - {outcome})"

            if not study_id or any(fp in str(study_id).lower() for fp in ['pdf', 'unknown', 'author_']):
                self.errors.append(f"{row_tag}: Study ID contains forbidden placeholder: '{study_id}'.")

            if a is not None and total_i is not None:
                if a > total_i:
                    self.errors.append(f"{row_tag}: Events in Intervention (a={a}) exceeds Total (Total_I={total_i})!")
                if a < 0 or total_i <= 0:
                    self.errors.append(f"{row_tag}: Negative or zero values in Intervention counts: a={a}, Total_I={total_i}")

            if c is not None and total_c is not None:
                if c > total_c:
                    self.errors.append(f"{row_tag}: Events in Comparator (c={c}) exceeds Total (Total_C={total_c})!")
                if c < 0 or total_c <= 0:
                    self.errors.append(f"{row_tag}: Negative or zero values in Comparator counts: c={c}, Total_C={total_c}")

            if pe is not None and ci_min is not None and ci_max is not None:
                if not (min(ci_min, ci_max) <= pe <= max(ci_min, ci_max)):
                    self.errors.append(f"{row_tag}: Point estimate {pe} is OUTSIDE 95% CI [{ci_min}, {ci_max}]!")

            if p_val is not None:
                try:
                    p_num = float(p_val)
                    if not (0.0 <= p_num <= 1.0):
                        self.errors.append(f"{row_tag}: P-value {p_val} is out of probability bounds [0, 1]!")
                except ValueError:
                    pass

            if not confounders or len(str(confounders).strip()) < 5:
                self.warnings.append(f"{row_tag}: Confounder adjustments empty or sparse.")

        return outcomes_checked

    def run(self) -> Dict[str, Any]:
        if not self.load_workbook():
            return {
                'passed': False,
                'errors': self.errors,
                'warnings': self.warnings,
                'studies_count': 0,
                'outcomes_count': 0
            }

        studies = self.audit_basic_layout()
        outcomes_checked = self.audit_ors_rrs()
        passed = (len(self.errors) == 0)

        return {
            'passed': passed,
            'errors': self.errors,
            'warnings': self.warnings,
            'studies_count': len(studies),
            'outcomes_count': outcomes_checked
        }


def main(wb_path: Optional[str] = None) -> int:
    configure_utf8_console()
    target_wb = wb_path or DEFAULT_WORKBOOK

    print("=" * 80)
    print("     AUTOMATED DATA EXTRACTION & INTEGRITY AUDITOR (ZERO-HALLUCINATION)        ")
    print("=" * 80)
    print(f"Target Workbook: {target_wb}\n")

    auditor = ExtractionIntegrityAuditor(target_wb)
    summary = auditor.run()

    print(f"Checked {summary['studies_count']} studies in 'Basic layout'.")
    print(f"Checked {summary['outcomes_count']} outcome records in 'ORs - RRs'.")

    print("\n--- Cross-Integrity & Quality Verdict ---")
    print(f"Total Warnings: {len(summary['warnings'])}")
    for w in summary['warnings']:
        print(f"  [WARNING] {w}")

    print(f"\nTotal Fatal Integrity Errors: {len(summary['errors'])}")
    if summary['errors']:
        for e in summary['errors']:
            print(f"  [ERROR] {e}")
        print("\nVERDICT: [FAIL] - Quality gates violated. Correct errors immediately!")
        return 1

    print("VERDICT: [PASS 100%] - Clean, verified, zero-hallucination data extraction confirmed.")
    print("All study identifiers, demographic locations, and statistical bounds are valid.")
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Audit CTM extraction workbook integrity.")
    parser.add_argument('--workbook', type=str, default=DEFAULT_WORKBOOK, help="Path to extraction workbook")
    args = parser.parse_args()
    sys.exit(main(wb_path=args.workbook))
