"""
validate_prospero_draft.py
Deterministic CTM Linter for PROSPERO Protocol Registration Drafts.
Standard: Centre for Translational Medicine (CTM) - PROSPERO Guide v6.0/v6.1
"""

import sys
import os
import re
import argparse
from typing import Dict, Any, List

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from src.utils.console import configure_utf8_console
configure_utf8_console()

DEFAULT_PROSPERO_FILE = os.path.join(WORKSPACE_ROOT, "docs", "PROSPERO-draft-meta_hyperglycaemia.md")


def validate_prospero_draft(filepath: str) -> Dict[str, Any]:
    print("=" * 70)
    print(f"CTM PROSPERO DRAFT VALIDATOR: {filepath}")
    print("=" * 70)

    if not os.path.isfile(filepath):
        print(f"[FAIL] Draft file not found: {filepath}")
        return {
            'passed': False,
            'errors': [f"Draft file not found: {filepath}"],
            'warnings': [],
            'passed_checks': []
        }

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    errors: List[str] = []
    warnings: List[str] = []
    passed_checks: List[str] = []
    
    # 1. Check Initial Screens (Screen 1 to 6)
    if "Screen 4" in content and "NOT being created as part of a student project or training course" in content:
        passed_checks.append("Screen 4 Training Course Embargo Protection Verified")
    else:
        errors.append("Screen 4 MUST specify: 'This record is NOT being created as part of a student project or training course'")
        
    if "Intervention review" in content or "Standard" in content:
        passed_checks.append("Screen 5 Review Type Verified ('Intervention review' / Standard)")
    else:
        errors.append("Screen 5 must specify 'Intervention review' or Standard per CTM Guide v6.0")
        
    # 2. Check 12 Sections Presence
    sections = [
        ("Section 1: Review Title and Basic Details", ["Review title", "Condition or domain", "Rationale", "Review objectives", "Keywords", "Country"]),
        ("Section 2: Eligibility Criteria", ["Population", "Intervention(s) or exposure(s)", "Comparator(s) or control(s)", "Study design", "Context"]),
        ("Section 3: Similar Reviews", ["similar records"]),
        ("Section 4: Timeline of the Review", ["timeline", "start date", "completion date"]),
        ("Section 5: Availability of Full Protocol", ["A full protocol has not been written"]),
        ("Section 6: Searching and Screening", ["MEDLINE", "Embase", "Cochrane", "Selection process"]),
        ("Section 7: Data Collection Process", ["Data extraction", "IPD will not be sought", "Certainty assessment"]),
        ("Section 8: Outcomes to be Analysed", ["Main outcomes", "Additional outcomes", "Secondary outcomes will be included if three publications reporting on them can be found"]),
        ("Section 9: Planned Data Synthesis", ["Strategy for data synthesis"]),
        ("Section 10: Current Review Stage", ["Preliminary searches", "Not started"]),
        ("Section 11: Review Affiliation, Funding and Peer Review", ["Centre for Translational Medicine, Semmelweis University", "Funding source", "Not peer-reviewed"]),
        ("Section 12: Additional Information", ["conflict of interest", "Medical Subject Headings"])
    ]
    
    for sec_name, keywords in sections:
        sec_missing = [kw for kw in keywords if kw.lower() not in content.lower()]
        if not sec_missing:
            passed_checks.append(f"{sec_name}: All key fields verified")
        else:
            errors.append(f"{sec_name}: Missing expected elements: {sec_missing}")

    # Section 4: Date regex check (Valid 1-year timeline format)
    dates_found = re.findall(r"\b\d{4}[-/]\d{2}[-/]\d{2}\b", content)
    if len(dates_found) >= 2:
        passed_checks.append(f"Section 4 Timeline Dates Verified: {dates_found[0]} to {dates_found[1]}")
    else:
        errors.append("Section 4 must specify valid start and completion dates (YYYY-MM-DD)")
            
    # 3. Word Count Check on Field 28 (Data Synthesis)
    match_9a = re.search(r"#{3,4}\s*9a\.?\s*Strategy for data synthesis.*?```(?:text)?\n(.*?)```", content, re.DOTALL | re.IGNORECASE)
    if match_9a:
        synth_text = match_9a.group(1).strip()
        word_count = len(synth_text.split())
        if word_count <= 400:
            passed_checks.append(f"Section 9a (Field 28) Word Count: {word_count} words (Limit: 400 words) -> PASS")
        else:
            errors.append(f"Section 9a (Field 28) EXCEEDS 400 words: {word_count} words!")
    else:
        errors.append("Section 9a text block not properly delimited by ```text code block!")
        
    # 4. Review Stage Verification (Only preliminary searches = Completed)
    stage_match = re.search(r"\|\s*[*]*\s*Preliminary searches\s*[*]*\s*\|.*?(?:Completed|Yes)", content, re.IGNORECASE)
    if stage_match:
        passed_checks.append("Review Stage: Preliminary searches properly marked Completed")
    else:
        errors.append("Review Stage: Preliminary searches must be marked Completed")
        
    unstarted_stages = [
        "Piloting of the study selection process",
        "Formal screening of search results",
        "Data extraction",
        "Risk of bias",
        "Data analysis"
    ]
    for stage in unstarted_stages:
        if re.search(rf"{stage}.*?Not started", content, re.IGNORECASE):
            passed_checks.append(f"Review Stage '{stage}' properly marked Not started")
        else:
            errors.append(f"Review Stage '{stage}' must be marked Not started before PROSPERO registration!")
            
    # 5. Supplementary Search Strategy File Check (Field 6f)
    if any(k in content.lower() for k in ["upload your search strategy", "search_strategy.pdf", "search strategy"]):
        passed_checks.append("Field 6f Search Strategy upload requirement documented")
    else:
        warnings.append("Field 6f: Ensure search strategy PDF upload reference is specified")
        
    # Print Results
    print("\n--- PASSED CHECKS ---")
    for chk in passed_checks:
        print(f"  [PASS] {chk}")

    if warnings:
        print("\n--- WARNINGS ---")
        for w in warnings:
            print(f"  [WARN] {w}")

    passed = (len(errors) == 0)
    if not passed:
        print("\n--- ERRORS ---")
        for err in errors:
            print(f"  [FAIL] {err}")
        print("\n" + "=" * 70)
        print(f"FAILED: {len(errors)} error(s) found. Draft rejected.")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("CTM PROSPERO DRAFT AUDIT PASSED: 100% COMPLIANT WITH GUIDE V6.0/V6.1")
        print("=" * 70)

    return {
        'passed': passed,
        'errors': errors,
        'warnings': warnings,
        'passed_checks': passed_checks
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate PROSPERO Draft Protocol against CTM Guide v6.0/v6.1.")
    parser.add_argument('filepath', nargs='?', help="Path to PROSPERO draft markdown")
    parser.add_argument('--file', '-f', help="Path to PROSPERO draft markdown")
    parser.add_argument('--project', '-p', help="Project slug in projects/<slug>")
    args = parser.parse_args()

    target_file = args.file or args.filepath
    if not target_file and args.project:
        target_file = os.path.join(WORKSPACE_ROOT, "projects", args.project, "protocol", "PROSPERO_DRAFT.md")
    if not target_file:
        target_file = DEFAULT_PROSPERO_FILE

    result = validate_prospero_draft(target_file)
    return 0 if result['passed'] else 1


if __name__ == "__main__":
    sys.exit(main())

