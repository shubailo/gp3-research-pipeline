#!/usr/bin/env python3
"""
CTM Assistant - Centre for Translational Medicine Methodological CLI Utility
Standardized helper for CTM Meta-Analysis workflows:
  1. calculate-kappa: Calculates Cohen's Kappa from 2x2 agreement matrix and formats CTM submission text.
  2. audit-extraction: Audits Excel extraction files against CTM BoostR room data cleaning rules.
  3. search-diff: Compares old and new search records for journal revision updates and PRISMA calculation.

Usage:
  python src/ctm_assistant.py calculate-kappa --both-inc 45 --both-exc 720 --r1-only 12 --r2-only 15
  python src/ctm_assistant.py audit-extraction path/to/extraction.xlsx --sheet "ORs - RRs"
  python src/ctm_assistant.py search-diff --old old_pmids.txt --new new_pmids.txt
"""

import sys
import io
import os
import argparse
from typing import Dict, Any, Tuple, List

# Ensure safe UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def calculate_cohens_kappa(both_include: int, both_exclude: int, r1_only: int, r2_only: int) -> Dict[str, Any]:
    """
    Calculates Cohen's Kappa for 2 reviewers and maps to CTM Guidebook categories.
    Matrix:
                 Reviewer 2 Include    Reviewer 2 Exclude
    R1 Include   both_include (A)      r1_only (B)
    R1 Exclude   r2_only (C)           both_exclude (D)
    """
    total = both_include + both_exclude + r1_only + r2_only
    if total == 0:
        raise ValueError("Total number of records cannot be zero.")

    # Observed agreement Po
    po = (both_include + both_exclude) / total

    # Marginals
    r1_yes = (both_include + r1_only) / total
    r1_no = (r2_only + both_exclude) / total
    r2_yes = (both_include + r2_only) / total
    r2_no = (r1_only + both_exclude) / total

    # Expected agreement by chance Pe
    pe = (r1_yes * r2_yes) + (r1_no * r2_no)

    if pe == 1.0:
        kappa = 1.0
    else:
        kappa = (po - pe) / (1.0 - pe)

    # CTM Guidebook categorization (Page 17)
    if kappa < 0.01:
        category = "Poor / No agreement (< 0.01)"
    elif kappa <= 0.20:
        category = "Slight agreement (0.01 - 0.20)"
    elif kappa <= 0.40:
        category = "Fair agreement (0.21 - 0.40)"
    elif kappa <= 0.60:
        category = "Moderate agreement (0.41 - 0.60)"
    elif kappa <= 0.80:
        category = "Substantial agreement (0.61 - 0.80)"
    else:
        category = "Almost perfect or perfect agreement (0.81 - 1.00)"

    return {
        "total": total,
        "both_include": both_include,
        "both_exclude": both_exclude,
        "r1_only": r1_only,
        "r2_only": r2_only,
        "po": po,
        "pe": pe,
        "kappa": kappa,
        "category": category
    }

def print_kappa_report(results: Dict[str, Any]):
    print("=" * 70)
    print("📊 CTM INTERRATER AGREEMENT (COHEN'S KAPPA) REPORT")
    print("=" * 70)
    print(f"Total Records Screened: {results['total']}")
    print(f"  - Both Include (Agreed In):     {results['both_include']}")
    print(f"  - Both Exclude (Agreed Out):    {results['both_exclude']}")
    print(f"  - Reviewer 1 Only (Disagreed):  {results['r1_only']}")
    print(f"  - Reviewer 2 Only (Disagreed):  {results['r2_only']}")
    print("-" * 70)
    print(f"Observed Agreement (Po): {results['po']:.4f} ({results['po']*100:.2f}%)")
    print(f"Expected Agreement (Pe): {results['pe']:.4f} ({results['pe']*100:.2f}%)")
    print(f"Cohen's Kappa (κ):       {results['kappa']:.4f}")
    print(f"CTM Agreement Category:  {results['category']}")
    print("-" * 70)
    print("\n📝 Formatted Text for Manuscript / SMS Documentation Form:")
    print(f"\"Title and abstract selection was performed independently and in duplicate by two reviewers. "
          f"Interrater reliability was assessed using Cohen's kappa, yielding a score of κ = {results['kappa']:.3f}, "
          f"indicating {results['category'].split(' (')[0].lower()} between the two investigators. "
          f"All discrepancies were adjudicated by consensus or consultation with a third reviewer.\"")
    print("=" * 70)

def audit_extraction_file(filepath: str, sheet_name: str = None) -> List[str]:
    """
    Audits an Excel file against CTM BoostR rules.
    """
    try:
        import openpyxl
    except ImportError:
        print("Error: openpyxl is required. Run 'pip install openpyxl'")
        sys.exit(1)

    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    wb = openpyxl.load_workbook(filepath, data_only=True)
    sheets_to_check = [sheet_name] if sheet_name else wb.sheetnames

    issues = []
    print("=" * 70)
    print(f"🔍 CTM BOOSTR DATA CLEANING AUDIT: {os.path.basename(filepath)}")
    print("=" * 70)

    for sname in sheets_to_check:
        if sname not in wb.sheetnames:
            issues.append(f"Sheet '{sname}' not found in workbook.")
            continue
        ws = wb[sname]
        print(f"\nScanning sheet: '{sname}' (Max Rows: {ws.max_row}, Max Cols: {ws.max_column})")

        # Check for study identifier column (usually Author & Year)
        header_row = 1
        headers = []
        for r in range(1, min(6, ws.max_row + 1)):
            row_vals = [str(cell.value or "").strip() for cell in ws[r]]
            if any("author" in v.lower() for v in row_vals) or any("first author" in v.lower() for v in row_vals):
                header_row = r
                headers = row_vals
                break

        if not headers:
            # Check row 1 by default
            headers = [str(cell.value or "").strip() for cell in ws[1]]

        print(f"  Detected Header Row: {header_row}")

        # BoostR Check: Study names and empty cells
        study_col_idx = None
        for idx, h in enumerate(headers):
            if "author" in h.lower() or "study" in h.lower():
                study_col_idx = idx + 1
                break

        row_count = 0
        blank_rows = []
        outcome_names = set()
        numeric_errors = []

        for r_idx in range(header_row + 1, ws.max_row + 1):
            row_cells = [ws.cell(row=r_idx, column=c) for c in range(1, ws.max_column + 1)]
            row_vals = [c.value for c in row_cells]
            if all(v is None or str(v).strip() == "" for v in row_vals):
                blank_rows.append(r_idx)
                continue

            row_count += 1

            # Check Study Name format
            if study_col_idx:
                sval = str(ws.cell(row=r_idx, column=study_col_idx).value or "").strip()
                if not sval:
                    issues.append(f"[{sname} Row {r_idx}] Missing Study Name / Author Identifier.")
                elif not any(char.isdigit() for char in sval):
                    issues.append(f"[{sname} Row {r_idx}] Study Name '{sval}' lacks publication year (BoostR requires 'Author Year').")

            # Check Numeric fields (e.g. columns with n, N, Mean, SD, Events, Sample)
            for c_idx, h in enumerate(headers):
                hl = h.lower()
                is_num_col = any(keyword in hl for keyword in [
                    "sample size", "events", "n0", "number of patients", "total n0", 
                    "mean", "sd", "median", "odds ratio", "risk ratio", "precalculated"
                ])
                if is_num_col:
                    val = ws.cell(row=r_idx, column=c_idx + 1).value
                    if val is not None and str(val).strip() != "":
                        sval = str(val).strip()
                        # Check if string contains prohibited text
                        if any(bad in sval.lower() for bad in ["nr", "n/a", "none", "not reported", "-", "approx"]):
                            numeric_errors.append(f"[{sname} Row {r_idx}, Col '{h}'] Prohibited text string in numeric column: '{sval}' (Must be blank or valid number)")
                        elif "-" in sval and not sval.startswith("-"): # e.g. "12-15"
                            numeric_errors.append(f"[{sname} Row {r_idx}, Col '{h}'] Range inside single numeric cell: '{sval}' (Must separate into Min and Max)")

        if blank_rows:
            issues.append(f"[{sname}] Found {len(blank_rows)} completely blank rows (Rows {blank_rows[:5]}...). BoostR requires contiguous tables without blank rows.")

        issues.extend(numeric_errors[:10])
        if len(numeric_errors) > 10:
            issues.append(f"[{sname}] ... and {len(numeric_errors) - 10} more numeric format violations.")

    print("\n" + "-" * 70)
    if not issues:
        print("✅ PASS: Workbook satisfies CTM BoostR Data Cleaning Guidelines!")
    else:
        print(f"⚠️  FOUND {len(issues)} ISSUES TO RESOLVE BEFORE BOOSTR ANALYSIS:")
        for idx, iss in enumerate(issues, 1):
            print(f"  {idx}. {iss}")
    print("=" * 70)
    return issues

def search_difference(old_file: str, new_file: str):
    """
    Computes set difference between old search results and new search update.
    """
    if not os.path.exists(old_file) or not os.path.exists(new_file):
        print("Error: Both old and new files must exist.")
        sys.exit(1)

    with open(old_file, 'r', encoding='utf-8') as f:
        old_ids = set(line.strip() for line in f if line.strip())

    with open(new_file, 'r', encoding='utf-8') as f:
        new_ids = set(line.strip() for line in f if line.strip())

    added = new_ids - old_ids
    removed = old_ids - new_ids
    retained = new_ids.intersection(old_ids)

    print("=" * 70)
    print("🔄 CTM SEARCH UPDATE DIFF (REVISION PROTOCOL)")
    print("=" * 70)
    print(f"Old Search Records:     {len(old_ids)}")
    print(f"New Search Records:     {len(new_ids)}")
    print(f"Retained (Unchanged):   {len(retained)}")
    print(f"New Records to Screen:  {len(added)}")
    print(f"Records No Longer Found:{len(removed)}")
    print("-" * 70)
    print("📋 PRISMA Flowchart Update Formula (Guidebook p. 43):")
    print(f"  - Total Search Hits:      {len(new_ids)}")
    print("  - Duplicates Removed:     (Old Duplicates + New Duplicates from added pool)")
    print(f"  - New Records Screened:   {len(added)} (Screen in duplicate in Rayyan)")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description="CTM Assistant - Centre for Translational Medicine Pipeline Utility")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: calculate-kappa
    kappa_parser = subparsers.add_parser("calculate-kappa", help="Calculate Cohen's Kappa agreement matrix")
    kappa_parser.add_argument("--both-inc", type=int, required=True, help="Both agreed to INCLUDE")
    kappa_parser.add_argument("--both-exc", type=int, required=True, help="Both agreed to EXCLUDE")
    kappa_parser.add_argument("--r1-only", type=int, required=True, help="Reviewer 1 included, Reviewer 2 excluded")
    kappa_parser.add_argument("--r2-only", type=int, required=True, help="Reviewer 2 included, Reviewer 1 excluded")

    # Command: audit-extraction
    audit_parser = subparsers.add_parser("audit-extraction", help="Audit Excel extraction file for BoostR readiness")
    audit_parser.add_argument("filepath", type=str, help="Path to Excel extraction file (.xlsx)")
    audit_parser.add_argument("--sheet", type=str, default=None, help="Specific sheet to audit")

    # Command: search-diff
    diff_parser = subparsers.add_parser("search-diff", help="Compare old and new search records for revision updates")
    diff_parser.add_argument("--old", type=str, required=True, help="File containing old search IDs/PMIDs (one per line)")
    diff_parser.add_argument("--new", type=str, required=True, help="File containing new search IDs/PMIDs (one per line)")

    args = parser.parse_args()

    if args.command == "calculate-kappa":
        res = calculate_cohens_kappa(args.both_inc, args.both_exc, args.r1_only, args.r2_only)
        print_kappa_report(res)
    elif args.command == "audit-extraction":
        audit_extraction_file(args.filepath, args.sheet)
    elif args.command == "search-diff":
        search_difference(args.old, args.new)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
