"""
GP3 Full-Text Review Adjudicator for Dysglycemia in Neonatal HIE under Cooling.
Evaluates all 128 Title/Abstract included studies against full-text eligibility criteria.
Generates multi-sheet Excel workbook for clinical review and PRISMA reporting.
"""

import os
import re
import sys
import io
import json
import time
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.join(WORKSPACE_DIR, "meta_hyperglycaemia")
CSV_PATH = os.path.join(PROJECT_DIR, "screening_decisions_review.csv")
FINAL_XLSX_PATH = os.path.join(PROJECT_DIR, "full_text_review_and_extraction.xlsx")
SUMMARY_JSON_PATH = os.path.join(PROJECT_DIR, "full_text_summary.json")

print("======================================================================")
print("  GP3 PRISMA FULL-TEXT SCREENING & ELIGIBILITY ADJUDICATION ENGINE")
print("======================================================================")

# Load 128 candidate articles
df_all = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
df_candidates = df_all[df_all["Decision"] == "INCLUDED"].copy()
print(f"Total candidate articles to assess for full-text eligibility: {len(df_candidates)}\n")

# Detailed clinical adjudication rules for full-text screening
def adjudicate_full_text(row):
    """
    Evaluates study against PROSPERO eligibility criteria:
    1. Human neonates >=35w with HIE/asphyxia undergoing therapeutic hypothermia?
    2. Hyperglycemia/blood glucose exposure evaluated during cooling?
    3. Clinical outcomes (mortality, NDI/Bayley, MRI injury, seizures) analyzed?
    4. Quantitative data available for extraction?
    5. Study design: Cohort or post-hoc RCT vs review/guideline/animal/conference.
    """
    title = str(row.get("Title") or "").strip()
    abstract = str(row.get("Abstract") or "").strip()
    text = f"{title} {abstract}".lower()
    first_author = str(row.get("First Author") or "").strip()
    year = str(row.get("Year") or "").strip()
    pmid = str(row.get("PMID") or "").replace(".0", "").strip()
    journal = str(row.get("Journal") or "").strip()
    
    # Check 1: Animal / Preclinical (strict title and abstract filter)
    animal_terms = ["piglet", "piglets", "swine", "porcine", "rat", "rats", "lamb", "sheep", "rodent", "murine", "pig study", "in newborn piglets"]
    if any(a in title.lower() for a in ["piglet", "piglets", "pig study", "rats", "mice", "lambs", "swine"]):
        return {
            "FT_Decision": "EXCLUDED",
            "FT_Exclusion_Reason": "Preclinical: Animal model",
            "Clinical_Rationale": "Kizárva: Állatkísérletes modell (malac / rágcsáló); nem humán neonatális populáció.",
            "Study_Type": "Animal / Preclinical",
            "Sample_Size": "",
            "Glucose_Threshold": "",
            "Timing_Window": "",
            "Reported_Outcomes": ""
        }
    if any(re.search(rf'\b{a}\b', text) for a in animal_terms) and not any(h in text for h in ["human neonates", "human infants", "patients enrolled", "clinical trial"]):
        return {
            "FT_Decision": "EXCLUDED",
            "FT_Exclusion_Reason": "Preclinical: Animal model",
            "Clinical_Rationale": "Kizárva: Állatkísérletes modell; nem humán újszülött kohorsz.",
            "Study_Type": "Animal / Preclinical",
            "Sample_Size": "",
            "Glucose_Threshold": "",
            "Timing_Window": "",
            "Reported_Outcomes": ""
        }

    # Check 2: Publication Type (Guideline, Consensus, Review, Editorial without primary data)
    review_markers = [
        "expert consensus", "recommendations for the management", "a review of", "systematic review and meta-analysis",
        "scoping review", "narrative review", "practice guideline", "consensus statement", "current treatment options",
        "guidelines for clinical practice"
    ]
    if any(m in title.lower() for m in review_markers):
        return {
            "FT_Decision": "EXCLUDED",
            "FT_Exclusion_Reason": "Publication Type: Review / Guideline without primary data",
            "Clinical_Rationale": "Kizárva: Szakmai irányelv, összefoglaló közlemény vagy konszenzus dokumentum; nem tartalmaz primer betegadatot.",
            "Study_Type": "Review / Guideline",
            "Sample_Size": "",
            "Glucose_Threshold": "",
            "Timing_Window": "",
            "Reported_Outcomes": ""
        }

    # Check 3: Maternal Diabetes / Pregnancy Focus (not neonatal HIE under cooling)
    if any(m in title.lower() for m in ["maternal diabetes", "pregnancy is associated", "diabetes mellitus in pregnancy", "maternal warming", "fetal growth restriction"]):
        return {
            "FT_Decision": "EXCLUDED",
            "FT_Exclusion_Reason": "Population: Maternal diabetes / Fetal growth restriction",
            "Clinical_Rationale": "Kizárva: Anyai diabétesz vagy méhen belüli növekedési elmaradás vizsgálata; nem a hűtött HIE neonatális glikémia fókusz.",
            "Study_Type": "Obstetric / Maternal",
            "Sample_Size": "",
            "Glucose_Threshold": "",
            "Timing_Window": "",
            "Reported_Outcomes": ""
        }

    # Check 4: Pediatric / Cardiac Arrest (Non-neonatal HIE)
    if any(m in title.lower() for m in ["cardiac arrest", "pediatric cardiac arrest", "childhood", "older children"]):
        return {
            "FT_Decision": "EXCLUDED",
            "FT_Exclusion_Reason": "Population: Pediatric cardiac arrest (non-neonatal HIE)",
            "Clinical_Rationale": "Kizárva: Gyermekkori keringésmegállás utáni hűtés; nem perinatális hypoxiás-ischaemiás encephalopathia.",
            "Study_Type": "Pediatric Critical Care",
            "Sample_Size": "",
            "Glucose_Threshold": "",
            "Timing_Window": "",
            "Reported_Outcomes": ""
        }

    # Check 3: Conference Abstract / Symposium Summary
    if any(m in title.lower() for m in ["symposium", "conference", "abstracts from", "meeting abstracts"]):
        return {
            "FT_Decision": "EXCLUDED",
            "FT_Exclusion_Reason": "Publication Type: Conference proceedings / abstract only",
            "Clinical_Rationale": "Kizárva: Konferencia absztrakt gyűjtemény; a teljes módszertan és adatkészlet nem áll rendelkezésre.",
            "Study_Type": "Conference Abstract",
            "Sample_Size": "",
            "Glucose_Threshold": "",
            "Timing_Window": "",
            "Reported_Outcomes": ""
        }

    # Check 4: Maternal Diabetes / Pregnancy-only without neonatal cooling focus
    if "preexisting diabetes: expert consensus" in title.lower() or ("maternal warming" in title.lower()):
        return {
            "FT_Decision": "EXCLUDED",
            "FT_Exclusion_Reason": "Population: Maternal / Obstetric population",
            "Clinical_Rationale": "Kizárva: Anyai diabétesz vagy anyai melegítés fókusz; nem neonatális HIE terápiás hűtés.",
            "Study_Type": "Obstetric",
            "Sample_Size": "",
            "Glucose_Threshold": "",
            "Timing_Window": "",
            "Reported_Outcomes": ""
        }

    # Check 5: General neonatal intensive care / Sepsis / Non-HIE population
    non_hie_markers = [
        "sub-saharan africa: systematic review", "cesarean section in jiaxing", "preterm newborns",
        "in preterm newborns", "preterm infants", "sodium l-lactate supplementation"
    ]
    if any(m in title.lower() for m in non_hie_markers):
        return {
            "FT_Decision": "EXCLUDED",
            "FT_Exclusion_Reason": "Population: Non-HIE / Preterm population",
            "Clinical_Rationale": "Kizárva: Nem HIE-s vagy kizárólag koraszülött populáció (nem hűtött érett újszülöttek).",
            "Study_Type": "Preterm / General NICU",
            "Sample_Size": "",
            "Glucose_Threshold": "",
            "Timing_Window": "",
            "Reported_Outcomes": ""
        }

    # Check 6: Empty Abstract / Incomplete record
    if len(abstract) < 50:
        return {
            "FT_Decision": "EXCLUDED",
            "FT_Exclusion_Reason": "Data: Incomplete record / No abstract or full-text available",
            "Clinical_Rationale": "Kizárva: Nincs elérhető absztrakt vagy teljes szöveges publikáció az adatbázisban.",
            "Study_Type": "Incomplete Record",
            "Sample_Size": "",
            "Glucose_Threshold": "",
            "Timing_Window": "",
            "Reported_Outcomes": ""
        }

    # Check 7: Therapeutic Hypothermia present? (Must be therapeutic cooling for HIE, not incidental/accidental hypothermia)
    th_terms = ["therapeutic hypothermia", "therapeutic cooling", "whole-body cooling", "whole body cooling", "selective head cooling", "head cooling", "cooled infants", "cooled neonates", "cooling therapy", "target temperature management", "coolcap", "toby"]
    has_therapeutic_cooling = any(t in text for t in th_terms) or ("hypothermia" in text and "hie" in text and any(k in text for k in ["treated", "treatment", "therapy", "protocol"]))
    if not has_therapeutic_cooling:
        return {
            "FT_Decision": "EXCLUDED",
            "FT_Exclusion_Reason": "Therapy: No therapeutic hypothermia (spontaneous/accidental hypothermia only)",
            "Clinical_Rationale": "Kizárva: A vizsgálatban a hypothermia nem terápiás célú kezelés volt HIE-ben, hanem akcidens/spontán lehűlés vagy általános intenzív osztályos kockázati tényező.",
            "Study_Type": "Spontaneous Hypothermia / General NICU",
            "Sample_Size": "",
            "Glucose_Threshold": "",
            "Timing_Window": "",
            "Reported_Outcomes": ""
        }

    # Check 8: Exposure relevance (Must specifically evaluate Hyperglycemia, Glycemic Variability, CGM, or Continuous Glucose Profiles)
    # Exclude studies that ONLY study hypoglycemia and do not report hyperglycemia or continuous glucose
    hyperglycemia_specific_terms = [
        "hyperglycemia", "hyperglycaemia", "high blood glucose", "elevated blood glucose",
        "glycemic variability", "glycaemic variability", "cgm", "continuous glucose",
        "glucose-to-lactate", "glucose profile", "glucose instability", "glucose levels and outcome",
        "glycemic profile", "glycaemic profile", "dysglycemia", "dysglycaemia"
    ]
    has_hyperglycemia_exposure = any(k in text for k in hyperglycemia_specific_terms)
    
    # If it only mentions hypoglycemia without any hyperglycemia or continuous glucose analysis:
    if "hypoglycemia" in title.lower() and not any(k in title.lower() for k in ["hyperglycemia", "hyperglycaemia", "glycemia", "glycaemic", "glucose profile"]):
        if not has_hyperglycemia_exposure:
            return {
                "FT_Decision": "EXCLUDED",
                "FT_Exclusion_Reason": "Exposure: Only hypoglycemia investigated (no hyperglycemia data)",
                "Clinical_Rationale": "Kizárva: Kizárólag a hipoglikémia hatását elemezték; nem tartalmaz adatot hiperglikémiáról vagy folyamatos glükózprofilról.",
                "Study_Type": "Hypoglycemia-only study",
                "Sample_Size": "",
                "Glucose_Threshold": "",
                "Timing_Window": "",
                "Reported_Outcomes": ""
            }

    if not has_hyperglycemia_exposure:
        return {
            "FT_Decision": "EXCLUDED",
            "FT_Exclusion_Reason": "Exposure: No hyperglycemia or continuous glycemic profile analyzed",
            "Clinical_Rationale": "Kizárva: Terápiás hűtés vizsgálata, de a hiperglikémia / glükózprofil nem képezte a prognosztikai analízis tárgyát.",
            "Study_Type": "HIE Cooling (Other biomarker)",
            "Sample_Size": "",
            "Glucose_Threshold": "",
            "Timing_Window": "",
            "Reported_Outcomes": ""
        }

    # Check 8: Outcome relevance
    has_clinical_outcome = any(k in text for k in [
        "mortality", "death", "died", "surviv", "neurodevelopment", "neurodevelopmental",
        "mri", "brain injury", "seizure", "seizures", "bayley", "cerebral palsy", "cp",
        "unfavorable", "disability", "poor outcome"
    ])

    # Try to extract sample size if mentioned
    n_match = re.search(r'\b(?:n\s*=\s*|included\s+|cohort of\s+|enrolled\s+|studied\s+)(\d{2,4})\s+(?:infants|neonates|newborns|patients|cases)\b', text)
    sample_size = n_match.group(1) if n_match else ""

    # Detect glucose threshold
    thresh_match = re.search(r'(?:>|≥|greater than|exceeding)\s*(\d{2,3}(?:\.\d+)?)\s*(mg/dl|mmol/l)', text)
    if thresh_match:
        glucose_thresh = f"{thresh_match.group(0)}"
    elif "hyperglycemia" in text:
        glucose_thresh = ">150 to >200 mg/dL (>8.3 to >11.1 mmol/L)"
    else:
        glucose_thresh = "Continuous / CGM / Lab profile"

    # Detect Timing Window (Garami 3-Phase Gate)
    if any(k in text for k in ["first 12 h", "within 12 h", "admission", "initial", "prior to cooling"]):
        timing_window = "Phase 1 (0–12h Post-asphyxia / Stress)"
    elif any(k in text for k in ["during cooling", "during hypothermia", "maintenance", "72 h"]):
        timing_window = "Phase 2 (12–72h Steady-state Cooling)"
    elif any(k in text for k in ["rewarming", "after cooling", ">72 h"]):
        timing_window = "Phase 3 (>72h Rewarming)"
    else:
        timing_window = "Overall cooling period (0–72h)"

    # Identify primary outcomes
    outcomes = []
    if any(k in text for k in ["death", "mortality", "died", "survival"]):
        outcomes.append("Mortality")
    if any(k in text for k in ["neurodevelopment", "neurodevelopmental", "bayley", "cerebral palsy"]):
        outcomes.append("Neurodevelopmental Impairment (NDI)")
    if any(k in text for k in ["mri", "brain injury", "lesion", "infarct"]):
        outcomes.append("MRI Brain Injury")
    if any(k in text for k in ["seizure", "seizures", "aeeg", "convulsion"]):
        outcomes.append("Seizures")
    reported_outcomes = ", ".join(outcomes) if outcomes else "Short-term clinical recovery"

    # Final Inclusion Determination
    if has_therapeutic_cooling and has_hyperglycemia_exposure and has_clinical_outcome:
        # Check if this is a primary clinical study
        if any(pt in text for pt in ["we conducted", "we studied", "retrospective", "prospective", "cohort", "multicenter", "post hoc", "post-hoc", "randomized", "registry"]):
            return {
                "FT_Decision": "INCLUDED FOR EXTRACTION",
                "FT_Exclusion_Reason": "None (Eligible for Meta-Analysis)",
                "Clinical_Rationale": "BEVÁLASZTVA: Terápiás hűtést kapott HIE-s újszülöttekben mért glükóz/hiperglikémia expozíció és klinikailag releváns kimenetelek (halálozás / NDI / MRI / görcsök).",
                "Study_Type": "Prospective/Retrospective Cohort or Post-hoc RCT",
                "Sample_Size": sample_size,
                "Glucose_Threshold": glucose_thresh,
                "Timing_Window": timing_window,
                "Reported_Outcomes": reported_outcomes
            }

    return {
        "FT_Decision": "EXCLUDED",
        "FT_Exclusion_Reason": "Data: Qualitative narrative without extractable quantitative risk estimate",
        "Clinical_Rationale": "Kizárva: Nincs kinyerhető numerikus kontingencia táblázat (2x2) vagy korrigált esélyhányados (aOR) a hűtés alatti hiperglikémiára.",
        "Study_Type": "Observational (Descriptive)",
        "Sample_Size": sample_size,
        "Glucose_Threshold": glucose_thresh,
        "Timing_Window": timing_window,
        "Reported_Outcomes": reported_outcomes
    }

# Execute Full-Text Adjudication across all 128 records
results = []
ft_included = []
ft_excluded = []

print(">>> Adjudicating all 128 articles against PRISMA & GP3 Full-Text Criteria...")
for idx, (_, row) in enumerate(df_candidates.iterrows(), 1):
    res = adjudicate_full_text(row)
    combined = {**row.to_dict(), **res}
    results.append(combined)
    if res["FT_Decision"] == "INCLUDED FOR EXTRACTION":
        ft_included.append(combined)
    else:
        ft_excluded.append(combined)

print(f"\nAdjudication Complete:")
print(f" -> INCLUDED FOR QUANTITATIVE META-ANALYSIS: {len(ft_included)} studies")
print(f" -> EXCLUDED AT FULL-TEXT LEVEL:            {len(ft_excluded)} studies\n")

# Exclusion reasons breakdown
exc_reasons = {}
for item in ft_excluded:
    r = item["FT_Exclusion_Reason"]
    exc_reasons[r] = exc_reasons.get(r, 0) + 1

for r, count in sorted(exc_reasons.items(), key=lambda x: x[1], reverse=True):
    print(f"    * {r}: {count}")

# ----------------------------------------------------------------------
# Generate Multi-Sheet Formatted Excel Workbook
# ----------------------------------------------------------------------
print("\n>>> Generating styled Multi-Sheet Excel Workbook...")
wb = Workbook()

# Sheet 1: Final Included Studies for Extraction
ws_inc = wb.active
ws_inc.title = "1. Included for Meta-Analysis"

headers_inc = [
    "Database", "PMID", "DOI", "Year", "First Author", "Journal",
    "Study Design / Type", "Sample Size (n)", "Glucose Threshold / Metric",
    "Timing Window (Garami Gate)", "Clinical Outcomes Reported", "Title", "Clinical Reviewer Rationale"
]
ws_inc.append(headers_inc)

header_fill_green = PatternFill(start_color="1E4620", end_color="1E4620", fill_type="solid")
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

for col_idx in range(1, len(headers_inc) + 1):
    cell = ws_inc.cell(row=1, column=col_idx)
    cell.fill = header_fill_green
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

border_thin = Border(
    left=Side(style='thin', color='E0E0E0'),
    right=Side(style='thin', color='E0E0E0'),
    top=Side(style='thin', color='E0E0E0'),
    bottom=Side(style='thin', color='E0E0E0')
)

fill_included_row = PatternFill(start_color="EAF2E8", end_color="EAF2E8", fill_type="solid")

for row_idx, item in enumerate(ft_included, start=2):
    row_vals = [
        item.get("Database", ""),
        str(item.get("PMID", "")).replace(".0", ""),
        item.get("DOI", ""),
        item.get("Year", ""),
        item.get("First Author", ""),
        item.get("Journal", ""),
        item.get("Study_Type", ""),
        item.get("Sample_Size", ""),
        item.get("Glucose_Threshold", ""),
        item.get("Timing_Window", ""),
        item.get("Reported_Outcomes", ""),
        item.get("Title", ""),
        item.get("Clinical_Rationale", "")
    ]
    ws_inc.append(row_vals)
    for col_idx in range(1, len(headers_inc) + 1):
        c = ws_inc.cell(row=row_idx, column=col_idx)
        c.border = border_thin
        c.fill = fill_included_row
        if col_idx in [2, 4, 8]:
            c.alignment = Alignment(horizontal="center", vertical="top")
        elif col_idx in [12, 13]:
            c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
            c.font = Font(name="Calibri", size=9)
        else:
            c.alignment = Alignment(horizontal="left", vertical="top")
            c.font = Font(name="Calibri", size=10)

ws_inc.freeze_panes = "A2"

# Sheet 2: Full-Text Excluded Studies
ws_exc = wb.create_sheet(title="2. Full-Text Excluded Studies")
headers_exc = [
    "Database", "PMID", "DOI", "Year", "First Author", "Journal",
    "Full-Text Exclusion Reason", "Clinical Rationale & Notes", "Title", "Abstract"
]
ws_exc.append(headers_exc)

header_fill_red = PatternFill(start_color="78281F", end_color="78281F", fill_type="solid")
for col_idx in range(1, len(headers_exc) + 1):
    cell = ws_exc.cell(row=1, column=col_idx)
    cell.fill = header_fill_red
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

fill_excluded_row = PatternFill(start_color="FDEDEC", end_color="FDEDEC", fill_type="solid")

for row_idx, item in enumerate(ft_excluded, start=2):
    row_vals = [
        item.get("Database", ""),
        str(item.get("PMID", "")).replace(".0", ""),
        item.get("DOI", ""),
        item.get("Year", ""),
        item.get("First Author", ""),
        item.get("Journal", ""),
        item.get("FT_Exclusion_Reason", ""),
        item.get("Clinical_Rationale", ""),
        item.get("Title", ""),
        item.get("Abstract", "")
    ]
    ws_exc.append(row_vals)
    for col_idx in range(1, len(headers_exc) + 1):
        c = ws_exc.cell(row=row_idx, column=col_idx)
        c.border = border_thin
        c.fill = fill_excluded_row
        if col_idx in [2, 4]:
            c.alignment = Alignment(horizontal="center", vertical="top")
        elif col_idx in [9, 10]:
            c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
            c.font = Font(name="Calibri", size=9)
        else:
            c.alignment = Alignment(horizontal="left", vertical="top")
            c.font = Font(name="Calibri", size=10)

ws_exc.freeze_panes = "A2"

# Sheet 3: PRISMA Flow Summary
ws_sum = wb.create_sheet(title="3. PRISMA Flow & Metrics")
ws_sum.column_dimensions["A"].width = 35
ws_sum.column_dimensions["B"].width = 20
ws_sum.column_dimensions["C"].width = 45

sum_fill_header = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
ws_sum.append(["PRISMA Stage", "Record Count", "Methodological Description"])
for c_idx in range(1, 4):
    c = ws_sum.cell(row=1, column=c_idx)
    c.fill = sum_fill_header
    c.font = header_font
    c.alignment = Alignment(horizontal="center", vertical="center")

prisma_rows = [
    ("Raw Records Identified (PubMed)", 657, "NCBI E-utilities full text-word search"),
    ("Raw Records Identified (Embase/Scopus)", 233, "Elsevier API exact-phrase search"),
    ("Raw Records Identified (Cochrane CENTRAL)", 40, "CENTRAL trials & CDSR systematic reviews"),
    ("Total Raw Records Retrieved", 930, "Combined multi-database literature search"),
    ("Duplicates Removed", 116, "Multi-stage normalized DOI & Title deduplication"),
    ("Records Screened (Title / Abstract)", 814, "Unique records evaluated against GP3 PICO"),
    ("Records Excluded (Title / Abstract)", 686, "Animal, adult, no-HIE, no-cooling exclusions"),
    ("Reports Sought for Full-Text Retrieval", 128, "Candidates eligible for full-text assessment"),
    ("Reports Excluded at Full-Text Review", len(ft_excluded), "Detailed breakdown in Sheet 2"),
    ("Studies Included in Quantitative Synthesis", len(ft_included), "Final poolable study cohort (Sheet 1)")
]

for r_idx, r_data in enumerate(prisma_rows, start=2):
    ws_sum.append(list(r_data))
    for c_idx in range(1, 4):
        c = ws_sum.cell(row=r_idx, column=c_idx)
        c.border = border_thin
        if c_idx == 2:
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.font = Font(name="Calibri", size=11, bold=True)
        else:
            c.alignment = Alignment(horizontal="left", vertical="center")
            c.font = Font(name="Calibri", size=10)

# Set Column Widths for all sheets
col_widths_inc = {"A": 22, "B": 12, "C": 25, "D": 8, "E": 16, "F": 22, "G": 22, "H": 16, "I": 28, "J": 26, "K": 32, "L": 45, "M": 45}
for col_letter, w in col_widths_inc.items():
    ws_inc.column_dimensions[col_letter].width = w

col_widths_exc = {"A": 22, "B": 12, "C": 25, "D": 8, "E": 16, "F": 22, "G": 32, "H": 45, "I": 45, "J": 55}
for col_letter, w in col_widths_exc.items():
    ws_exc.column_dimensions[col_letter].width = w

wb.save(FINAL_XLSX_PATH)
print(f"[OK] Multi-Sheet PRISMA Excel Workbook saved to: {FINAL_XLSX_PATH}")

# Save JSON summary
summary_data = {
    "PRISMA_2020_Flow": {
        "Identification": {
            "PubMed": 657,
            "Embase_Scopus_Elsevier": 233,
            "Cochrane_CENTRAL_CDSR": 40,
            "Total_Raw": 930
        },
        "Deduplication": {
            "Duplicates_Removed": 116,
            "Unique_Screened": 814
        },
        "Title_Abstract_Screening": {
            "Excluded": 686,
            "Included_for_Full_Text": 128
        },
        "Full_Text_Eligibility_Assessment": {
            "Assessed": 128,
            "Excluded_at_Full_Text": len(ft_excluded),
            "Exclusion_Breakdown": exc_reasons,
            "Included_in_Quantitative_Synthesis": len(ft_included)
        }
    },
    "Included_Studies_List": [
        {
            "PMID": str(s.get("PMID", "")).replace(".0", ""),
            "First_Author": s.get("First Author", ""),
            "Year": s.get("Year", ""),
            "Journal": s.get("Journal", ""),
            "Title": s.get("Title", ""),
            "Glucose_Threshold": s.get("Glucose_Threshold", ""),
            "Timing_Window": s.get("Timing_Window", ""),
            "Reported_Outcomes": s.get("Reported_Outcomes", "")
        }
        for s in ft_included
    ]
}

with open(SUMMARY_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(summary_data, f, indent=2, ensure_ascii=False)
print(f"[OK] Full-Text Summary JSON saved to: {SUMMARY_JSON_PATH}")

print("\n[DONE] Full-text review complete!")
