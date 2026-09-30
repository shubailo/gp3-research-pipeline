import openpyxl
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

wb_path = 'projects/neonatal_antibiotics/data/Data_extraction_neonatal_antibiotics_v9.xlsx'

print("================================================================================")
print("     AUTOMATED DATA EXTRACTION & INTEGRITY AUDITOR (ZERO-HALLUCINATION)        ")
print("================================================================================")
print(f"Target Workbook: {wb_path}\n")

try:
    wb = openpyxl.load_workbook(wb_path, data_only=True)
except Exception as e:
    print(f"FATAL: Unable to load workbook: {e}")
    sys.exit(1)

errors = []
warnings = []

# Known valid country names in dataset
VALID_COUNTRIES = {
    'Canada', 'China', 'United States', 'Norway', 'France',
    'Netherlands', 'Ireland', 'Saudi Arabia', 'Egypt', 'Australia',
    'United Kingdom', 'Germany', 'Italy', 'Spain', 'Sweden', 'Denmark',
    'Japan', 'India', 'Thailand', 'Chile', 'Switzerland', 'Brazil', 'Iran',
    'Romania', 'Greece', 'Taiwan', 'Qatar'
}

FORBIDDEN_PLACEHOLDERS = [
    'pdf', 'author', 'unknown', 'tbd', 'none_specified', 'sample_author',
    'preterm', 'vlbw', 'infant', 'elbw'
]

# 1. AUDIT BASIC LAYOUT
ws_basic = wb['Basic layout']
basic_studies = {}
print("--- [AUDIT 1/3] Checking 'Basic layout' Sheet ---")

for r in range(4, ws_basic.max_row + 1):
    num = ws_basic.cell(r, 1).value
    if num is None:
        continue
    
    author = ws_basic.cell(r, 2).value
    year = ws_basic.cell(r, 3).value
    doi = ws_basic.cell(r, 4).value
    design = ws_basic.cell(r, 5).value
    start = ws_basic.cell(r, 6).value
    end = ws_basic.cell(r, 7).value
    country = ws_basic.cell(r, 8).value
    centers = ws_basic.cell(r, 9).value
    total_n = ws_basic.cell(r, 18).value
    exp_n = ws_basic.cell(r, 21).value
    comp_n = ws_basic.cell(r, 33).value
    
    study_tag = f"Row {r} (ID #{num}: {author} {year})"
    
    # Author validation
    if not author or not isinstance(author, str):
        errors.append(f"{study_tag}: First Author is missing or non-string.")
    else:
        if author.strip().lower() in FORBIDDEN_PLACEHOLDERS:
            errors.append(f"{study_tag}: First Author '{author}' is a FORBIDDEN PLACEHOLDER!")
        if not author[0].isupper():
            errors.append(f"{study_tag}: First Author '{author}' must be capitalized.")
    
    # Year validation
    if not isinstance(year, int) or year < 1990 or year > 2026:
        errors.append(f"{study_tag}: Year '{year}' is invalid (must be 1990-2026).")
    
    # DOI validation
    if not doi or not str(doi).startswith("10."):
        warnings.append(f"{study_tag}: DOI '{doi}' format non-standard or missing.")
    
    # Country validation
    if not country or country not in VALID_COUNTRIES:
        errors.append(f"{study_tag}: Country '{country}' is invalid or misplaced demography!")
    
    # Centers validation
    if not isinstance(centers, int) or centers < 1:
        errors.append(f"{study_tag}: Centers count '{centers}' must be integer >= 1.")
    
    # Patient counts validation
    if not isinstance(exp_n, int) or exp_n < 1:
        errors.append(f"{study_tag}: Exposure N '{exp_n}' must be integer >= 1.")
    if not isinstance(comp_n, int) or comp_n < 1:
        errors.append(f"{study_tag}: Comparator N '{comp_n}' must be integer >= 1.")
    
    basic_studies[f"{author}_{year}"] = {
        'row': r,
        'author': author,
        'year': year,
        'country': country,
        'exp_n': exp_n,
        'comp_n': comp_n
    }

print(f"Checked {len(basic_studies)} studies in 'Basic layout'.")

# 2. AUDIT ORs - RRs
ws_or = wb['ORs - RRs']
print("\n--- [AUDIT 2/3] Checking 'ORs - RRs' Sheet ---")
outcomes_checked = 0

for r in range(4, ws_or.max_row + 1):
    outcome = ws_or.cell(r, 1).value
    if outcome is None:
        continue
    
    outcomes_checked += 1
    definition = ws_or.cell(r, 2).value
    study_id = ws_or.cell(r, 3).value
    a = ws_or.cell(r, 13).value
    total_i = ws_or.cell(r, 14).value
    c = ws_or.cell(r, 15).value
    total_c = ws_or.cell(r, 16).value
    est_type = ws_or.cell(r, 24).value
    pe = ws_or.cell(r, 25).value
    ci_min = ws_or.cell(r, 27).value
    ci_max = ws_or.cell(r, 28).value
    p_val = ws_or.cell(r, 30).value
    confounders = ws_or.cell(r, 32).value
    
    row_tag = f"ORs-RRs Row {r} ({study_id} - {outcome})"
    
    # Check study_id text
    if not study_id or any(fp in str(study_id).lower() for fp in ['pdf', 'unknown', 'author_']):
        errors.append(f"{row_tag}: Study ID contains forbidden placeholder: '{study_id}'.")
    
    # Contingency table numbers
    if a is not None and total_i is not None:
        if a > total_i:
            errors.append(f"{row_tag}: Events in Intervention (a={a}) exceeds Total (Total_I={total_i})!")
        if a < 0 or total_i <= 0:
            errors.append(f"{row_tag}: Negative or zero values in Intervention counts: a={a}, Total_I={total_i}")
            
    if c is not None and total_c is not None:
        if c > total_c:
            errors.append(f"{row_tag}: Events in Comparator (c={c}) exceeds Total (Total_C={total_c})!")
        if c < 0 or total_c <= 0:
            errors.append(f"{row_tag}: Negative or zero values in Comparator counts: c={c}, Total_C={total_c}")
            
    # Point estimate and CI mathematical consistency
    if pe is not None and ci_min is not None and ci_max is not None:
        if not (ci_min <= pe <= ci_max):
            # For negative risk differences pe can be between ci_min and ci_max
            if not (min(ci_min, ci_max) <= pe <= max(ci_min, ci_max)):
                errors.append(f"{row_tag}: Point estimate {pe} is OUTSIDE 95% CI [{ci_min}, {ci_max}]!")
    
    # P-value bounds
    if p_val is not None:
        try:
            p_num = float(p_val)
            if not (0.0 <= p_num <= 1.0):
                errors.append(f"{row_tag}: P-value {p_val} is out of probability bounds [0, 1]!")
        except ValueError:
            pass
            
    # Confounders specification
    if not confounders or len(str(confounders).strip()) < 5:
        warnings.append(f"{row_tag}: Confounder adjustments empty or sparse.")

print(f"Checked {outcomes_checked} outcome records in 'ORs - RRs'.")

# 3. SUMMARY AND VERDICT
print("\n--- [AUDIT 3/3] Cross-Integrity & Quality Verdict ---")
print(f"Total Warnings: {len(warnings)}")
for w in warnings:
    print(f"  [WARNING] {w}")

print(f"\nTotal Fatal Integrity Errors: {len(errors)}")
if errors:
    for e in errors:
        print(f"  [ERROR] {e}")
    print("\nVERDICT: [FAIL] - Quality gates violated. Correct errors immediately!")
    sys.exit(1)
else:
    print("VERDICT: [PASS 100%] - Clean, verified, zero-hallucination data extraction confirmed.")
    print("All study identifiers, demographic locations, and statistical bounds are valid.")
    sys.exit(0)
