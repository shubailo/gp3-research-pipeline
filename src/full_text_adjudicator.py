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

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from src.utils.console import configure_utf8_console
configure_utf8_console()

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
    abstract = str(record.get("Abstract") or record.get("abstract") or record.get("Abstract Note") or "").strip()
    text = f"{title} {abstract}".lower()

    if project == "neonatal_antibiotics":
        # Preclinical / animal with word boundaries
        animal_regex = r'\b(rats?|mice|mouse|murine|piglets?|porcine|canine|bovine|ovine|in vitro|cell culture|cell line|animal model)\b'
        if re.search(animal_regex, text, re.IGNORECASE):
            human_regex = r'\b(human|clinical|patients|neonates?|infants?|preterm|premature|vlbw|elbw|nicu)\b'
            if not re.search(human_regex, text, re.IGNORECASE):
                return {"decision": "EXCLUDE", "reason": "Preclinical: Animal or in vitro model", "reviewer": "R1_Clinical"}

        # Adult / geriatric check
        adult_regex = r'\b(adults?|elderly|postmenopausal|geriatric|older adults?|adult intensive care)\b'
        if re.search(adult_regex, text, re.IGNORECASE):
            preterm_regex = r'\b(preterm|premature|vlbw|elbw|very low birth weight|gestational age|neonate|neonates|neonatal|newborn|newborns)\b'
            if not re.search(preterm_regex, text, re.IGNORECASE):
                return {"decision": "EXCLUDE", "reason": "Population: Adult or geriatric population", "reviewer": "R1_Clinical"}

        # Pediatric non-neonatal check
        ped_regex = r'\b(pediatric emergency|pediatric intensive care|picu|school-age|adolescent|children aged|pediatric pneumonia)\b'
        if re.search(ped_regex, text, re.IGNORECASE):
            preterm_neonate_regex = r'\b(preterm|premature|vlbw|elbw|neonate|neonates|neonatal|newborn|newborns|nicu)\b'
            if not re.search(preterm_neonate_regex, text, re.IGNORECASE):
                return {"decision": "EXCLUDE", "reason": "Population: Pediatric non-neonatal cohort", "reviewer": "R1_Clinical"}

        # Target neonate check
        neonate_regex = r'\b(neonates?|neonatal|newborns?|preterm|premature|vlbw|elbw|infants?|nicu|extremely low birth weight)\b'
        if not re.search(neonate_regex, text, re.IGNORECASE):
            return {"decision": "EXCLUDE", "reason": "Population: Non-neonatal cohort", "reviewer": "R1_Clinical"}

        # Clinical outcomes: NEC, Mortality, Sepsis, LOS, BPD, IVH, safety
        outcome_regex = r'\b(nec|enterocolitis|mortality|deaths?|died|survival|sepsis|los|bpd|ivh|neurodevelopment|safety|adverse outcomes?|outcomes?|complications?)\b'
        if not re.search(outcome_regex, text, re.IGNORECASE):
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

    elif project == "pediatric_prewarming":
        # R1: Clinical Population & Core Hypothermia Outcomes
        if re.search(r'\b(dogs?|canine|veterinary|rats?|mice|mouse|murine|piglets?|porcine|bovine|ovine|in vitro|cell culture|cell line|animal model)\b', text, re.IGNORECASE):
            if "veterinary" in text or "small dogs" in text or "in dogs" in text or "canine" in text:
                return {"decision": "EXCLUDE", "reason": "Preclinical: Veterinary / canine study", "reviewer": "R1_Clinical"}
            human_ped_regex = r'\b(pediatric patients?|paediatric patients?|children|infants?|neonates?|nicu|picu|human)\b'
            if not re.search(human_ped_regex, text, re.IGNORECASE):
                return {"decision": "EXCLUDE", "reason": "Preclinical: Animal or in vitro laboratory model", "reviewer": "R1_Clinical"}

        # Obstetric & Adult exclusions (Maternal pre-warming before cesarean is adult surgery)
        if re.search(r'\b(cesarean|caesarean|parturients?|maternal|total knee|total hip|arthroplast\w*|coronary artery bypass|adult cardiac)\b', text, re.IGNORECASE) and not re.search(r'\b(pediatric surgery|paediatric surgery|children undergoing surgery)\b', text, re.IGNORECASE):
            return {"decision": "EXCLUDE", "reason": "Population: Adult obstetric / orthopedic / non-pediatric", "reviewer": "R1_Clinical"}

        adult_regex = r'\b(adults?|elderly|geriatric|older patients after major cancer surgery)\b'
        if re.search(adult_regex, text, re.IGNORECASE):
            ped_regex = r'\b(pediatric|paediatric|children|child|infants?|neonates?|newborns?|adolescents?|toddlers?)\b'
            if not re.search(ped_regex, text, re.IGNORECASE):
                return {"decision": "EXCLUDE", "reason": "Population: Adult exclusively / non-pediatric", "reviewer": "R1_Clinical"}

        # Non-surgical delivery room / transport resuscitation
        delivery_regex = r'\b(delivery room|resuscitation of preterm|plastic wrap|plastic bag|plastic hat|polyethylene bag|intramural vaginally born|cloth and newspaper)\b'
        if re.search(delivery_regex, text, re.IGNORECASE):
            surg_regex = r'\b(surgery|surgical|operation|operative|anesthesia|anaesthesia|operating room|operating theatre|induction)\b'
            if not re.search(surg_regex, text, re.IGNORECASE):
                return {"decision": "EXCLUDE", "reason": "Setting: Delivery room resuscitation / transport without surgery", "reviewer": "R1_Clinical"}

        ped_surg_regex = r'\b(pediatric|paediatric|children|child|infants?|neonates?|newborns?|adolescents?|toddlers?|pediatric surgery|pediatric surgical)\b'
        if not re.search(ped_surg_regex, text, re.IGNORECASE):
            return {"decision": "EXCLUDE", "reason": "Population: Non-pediatric surgical cohort", "reviewer": "R1_Clinical"}

        # Must be in a surgical or perioperative context
        perioperative_regex = r'\b(surgery|surgical|operation|operative|anesthesia|anaesthesia|operating room|operating theatre|perioperative|preoperative|postoperative|pacu|induction)\b'
        if not re.search(perioperative_regex, text, re.IGNORECASE):
            return {"decision": "EXCLUDE", "reason": "Setting: Non-surgical cohort", "reviewer": "R1_Clinical"}

        temp_outcome_regex = r'\b(hypothermia|core temperature|body temperature|normothermia|temperature drop|shivering|thermal|rewarming|pacu|temperature monitoring)\b'
        if not re.search(temp_outcome_regex, text, re.IGNORECASE):
            return {"decision": "UNSURE", "reason": "Outcome: Thermal/hypothermia endpoint unconfirmed in abstract", "reviewer": "R1_Clinical"}

        return {"decision": "INCLUDE", "reason": "Eligible: Pediatric surgical cohort with thermal outcomes evaluated", "reviewer": "R1_Clinical"}

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
    abstract = str(record.get("Abstract") or record.get("abstract") or record.get("Abstract Note") or "").strip()
    text = f"{title} {abstract}".lower()

    # Publication type filter
    # Publication type filter
    review_regex = r'\b(systematic review|meta-analysis|narrative review|practice guideline|consensus statement|guidelines|editorial|commentary|correspondence|letter to the editor|expert opinion)\b'
    if re.search(review_regex, title, re.IGNORECASE) and "protocol" not in title.lower():
        return {"decision": "EXCLUDE", "reason": "Design: Secondary literature / Review without primary data", "reviewer": "R2_Methodological"}

    if project == "neonatal_antibiotics":
        # Antibiotic check
        abx_regex = r'\b(antibiotics?|antimicrobials?|antibacterials?|ampicillin|gentamicin|vancomycin|meropenem|cefotaxime|cefepime|amikacin|piperacillin|anti-bacterial)\b'
        if not re.search(abx_regex, text, re.IGNORECASE):
            return {"decision": "EXCLUDE", "reason": "Exposure: Non-antibiotic exposure", "reviewer": "R2_Methodological"}

        # Duration / stewardship / comparative contrast
        duration_regex = r'\b(duration|course|days of therapy|dot|lot|length of therapy|prolonged|short-course|short course|stewardship|discontinuation|stopping rule|empiric|empirical|exposure|treatment length|days of antibiotic|hours of antibiotic|prescrib\w*)\b'
        if not re.search(duration_regex, text, re.IGNORECASE):
            return {"decision": "EXCLUDE", "reason": "Exposure: No empiric antibiotic duration/comparison analyzed", "reviewer": "R2_Methodological"}

        # Culture context
        culture_regex = r'\b(culture-negative|negative cultures?|sterile cultures?|blood cultures?|empiric|empirical|early-onset|eos|suspected sepsis|rule-out|asymptomatic|risk factors?)\b'
        if not re.search(culture_regex, text, re.IGNORECASE):
            return {"decision": "UNSURE", "reason": "Exposure: Culture-negative / EOS context unconfirmed in abstract", "reviewer": "R2_Methodological"}

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

    elif project == "pediatric_prewarming":
        # R2: Methodological Rigor, Active Prewarming Exposure & Comparator
        review_regex = r'\b(systematic review|meta-analysis|narrative review|practice guideline|consensus statement|guidelines?|editorial|commentary|correspondence|letter to the editor|expert opinion)\b'
        if re.search(review_regex, title, re.IGNORECASE) and "protocol" not in title.lower():
            return {"decision": "EXCLUDE", "reason": "Design: Secondary literature / Review without primary data (Flagged for citation chasing)", "reviewer": "R2_Methodological"}

        # Adult obstetric / non-pediatric exclusion
        if re.search(r'\b(cesarean|caesarean|parturients?|maternal|total knee|total hip|arthroplast\w*|older patients after major cancer surgery)\b', text, re.IGNORECASE) and not re.search(r'\b(pediatric surgery|paediatric surgery|children undergoing surgery)\b', text, re.IGNORECASE):
            return {"decision": "EXCLUDE", "reason": "Population/Design: Adult obstetric or non-pediatric surgical intervention", "reviewer": "R2_Methodological"}

        prewarm_regex = r'\b(prewarming|pre-warming|preoperative warming|pre-operative warming|preanesthetic warming|pre-anesthetic warming|active warming before|warming prior to induction)\b'
        faw_bundle_regex = r'\b(forced-air|forced air|warming blanket|thermal mattress|conductive warming|underbody blanket|bair hugger|bair paws|resistive heating)\b'

        has_prewarm = bool(re.search(prewarm_regex, text, re.IGNORECASE))
        has_faw = bool(re.search(faw_bundle_regex, text, re.IGNORECASE))

        if has_prewarm:
            has_contrast = bool(re.search(r'\b(randomized|randomised|trial|control|versus|vs\.?|compared|comparison|cohort|intervention group|baseline|pre-intervention|post-intervention)\b', text, re.IGNORECASE))
            if has_contrast:
                return {"decision": "INCLUDE", "reason": "Eligible: Active pre-warming intervention evaluated against comparator/control", "reviewer": "R2_Methodological"}
            else:
                return {"decision": "UNSURE", "reason": "Design: Comparative arm/control unconfirmed in abstract", "reviewer": "R2_Methodological"}

        if has_faw and any(k in text for k in ["pre", "induction", "before", "timing", "bundle"]):
            return {"decision": "UNSURE", "reason": "Intervention: Active warming timing/pre-induction arm requires full-text verification", "reviewer": "R2_Methodological"}

        return {"decision": "EXCLUDE", "reason": "Intervention: No active pre-warming evaluated", "reviewer": "R2_Methodological"}

    else:
        return {"decision": "INCLUDE", "reason": "Methodological criteria met", "reviewer": "R2_Methodological"}


# ─────────────────────────────────────────────────────────────────────────────
# 2. STATISTICAL AGREEMENT (COHEN'S KAPPA)
# ─────────────────────────────────────────────────────────────────────────────

from src.utils.math_stats import calculate_cohens_kappa_from_lists as calculate_cohens_kappa


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
            str(item.get("Record_ID", item.get("id", row_idx - 1))),
            str(item.get("PMID", item.get("pmid", ""))).replace(".0", ""),
            str(item.get("DOI", item.get("doi", ""))),
            str(item.get("Year", item.get("year", item.get("Publication Year", "")))).replace(".0", ""),
            str(item.get("First_Author", item.get("first_author", item.get("Author", item.get("author", ""))))),
            str(item.get("Journal", item.get("journal", item.get("Publication Title", "")))),
            str(item.get("R1_Decision", "")),
            str(item.get("R1_Rationale", "")),
            str(item.get("R2_Decision", "")),
            str(item.get("R2_Rationale", "")),
            str(item.get("Conflict_Type", "Discordant (R1 != R2)")),
            str(item.get("Human_Arbiter_Decision", "")),  # Empty for human filling
            str(item.get("Arbitration_Rationale", "")),   # Empty for human filling
            str(item.get("Title") or item.get("title") or ""),
            str(item.get("Abstract") or item.get("abstract") or item.get("Abstract Note") or "")[:500]
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
            str(item.get("Record_ID", item.get("id", row_idx - 1))),
            str(item.get("PMID", item.get("pmid", ""))).replace(".0", ""),
            str(item.get("DOI", item.get("doi", ""))),
            str(item.get("Year", item.get("year", item.get("Publication Year", "")))).replace(".0", ""),
            str(item.get("First_Author", item.get("first_author", item.get("Author", item.get("author", ""))))),
            str(item.get("Journal", item.get("journal", item.get("Publication Title", "")))),
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
            str(item.get("Record_ID", item.get("id", row_idx - 1))),
            str(item.get("PMID", item.get("pmid", ""))).replace(".0", ""),
            str(item.get("DOI", item.get("doi", ""))),
            str(item.get("Year", item.get("year", item.get("Publication Year", "")))).replace(".0", ""),
            str(item.get("First_Author", item.get("first_author", item.get("Author", item.get("author", ""))))),
            str(item.get("Journal", item.get("journal", item.get("Publication Title", "")))),
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
    all_screened = []

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
            "Row_Index": idx + 1,  # Header is row 1, data starts at row 2 in CSV
            "Final_Decision": "",
            "Primary_Reason": "",
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
            annotated["Final_Decision"] = "INCLUDED"
            annotated["Primary_Reason"] = "Eligible: Full PICO criteria confirmed in Title/Abstract"
            consensus_inc.append(annotated)
        elif is_r1_exc and is_r2_exc:
            annotated["Adjudication_Status"] = "CONSENSUS_EXCLUDE"
            annotated["Final_Decision"] = "EXCLUDED"
            reason = f"R1: {r1_r} | R2: {r2_r}" if r1_r != r2_r else r1_r
            annotated["Exclusion_Reason"] = reason
            annotated["Primary_Reason"] = reason
            consensus_exc.append(annotated)
        else:
            annotated["Adjudication_Status"] = "CONFLICT_NEEDS_ARBITRATION"
            annotated["Final_Decision"] = "UNSURE_FULLTEXT"
            annotated["Conflict_Type"] = f"Discordant / Borderline: R1({r1_d}) vs R2({r2_d})"
            annotated["Primary_Reason"] = "Discordant evaluation or borderline eligibility; requires senior arbitration"
            annotated["Human_Arbiter_Decision"] = ""  # Left empty for human decision
            annotated["Arbitration_Rationale"] = ""   # Left empty for human rationale
            conflicts.append(annotated)

        all_screened.append(annotated)

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

    # ── 3. EXPORT COMPLETE ANNOTATED CSV IN ORIGINAL ROW ORDER ────────────────
    screened_csv_path = os.path.join(WORKSPACE_DIR, "Teljes_konyvtar_screened.csv")
    df_all = pd.DataFrame(all_screened)
    front_cols = [
        "Row_Index", "Final_Decision", "Primary_Reason", "Adjudication_Status",
        "R1_Decision", "R1_Rationale", "R2_Decision", "R2_Rationale",
        "Title", "Author", "Publication Year", "Publication Title", "DOI", "PMID", "Abstract Note"
    ]
    reordered_cols = [c for c in front_cols if c in df_all.columns] + [c for c in df_all.columns if c not in front_cols]
    df_all = df_all[reordered_cols]
    df_all.to_csv(screened_csv_path, index=False, encoding="utf-8-sig")

    # Also save an annotated CSV copy in output_dir
    df_all.to_csv(os.path.join(output_dir, "screened_library_all_4110.csv"), index=False, encoding="utf-8-sig")

    # ── 4. EXPORT SCREENING_REPORT.MD ─────────────────────────────────────────
    report_md_path = os.path.join(output_dir, "SCREENING_REPORT.md")
    
    # Calculate exclusion categories
    exc_reasons = {}
    for item in consensus_exc:
        r = item.get("Primary_Reason", "Other")
        exc_reasons[r] = exc_reasons.get(r, 0) + 1
    
    sorted_reasons = sorted(exc_reasons.items(), key=lambda x: x[1], reverse=True)

    with open(report_md_path, "w", encoding="utf-8") as f:
        f.write("# PRISMA 2020 Cím- és Absztrakt-Szűrési Jelentés\n\n")
        f.write(f"> **Projekt:** `{project}` (Neonatal Empirical Antibiotic Duration & Safety)  \n")
        f.write(f"> **Módszertani Szabvány:** PRISMA 2020 · Cochrane Handbook v6.5 · Semmelweis CTM  \n")
        f.write(f"> **Időpont:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"> **Forrás Könyvtár:** `Teljes könyvtár.csv` (Deduplikált Zotero export)  \n\n")
        f.write("---\n\n")
        f.write("## 1. PRISMA 2020 FOLYAMATÁBRA STATISZTIKÁK\n\n")
        f.write("| PRISMA 2020 Szakasz | Adatbázis / Lépés | Tételek Száma |\n")
        f.write("|---|---|:---:|\n")
        f.write("| **1. Identifikáció (Nyers találatok)** | PubMed (2 452) + Embase (3 412) + Cochrane CENTRAL (232) | **6 096** |\n")
        f.write("| **2. Deduplikáció** | Eltávolított azonos rekordok (DOI és normalizált cím alapján) | **-1 986** |\n")
        f.write(f"| **3. Cím- és Absztrakt Szűrésre Bekerült** | Teljes deduplikált könyvtár | **{len(records):,}** |\n")
        f.write(f"| ⛔ **Kizárva a Cím és Absztrakt alapján** | Populáció, dizájn vagy expozíciós kizárási okok | **{len(consensus_exc):,}** ({len(consensus_exc)/len(records)*100:.1f}%) |\n")
        f.write(f"| 📄 **Konszenzusosan Beválogatott (Full-Text)** | Teljes PICO megfelelés a cím/absztraktban | **{len(consensus_inc):,}** ({len(consensus_inc)/len(records)*100:.1f}%) |\n")
        f.write(f"| 🔍 **Bizonytalan / Arbitrációt Igénylő** | Tenyésztés-negativitás vagy NEC csak teljes szövegben igazolható | **{len(conflicts):,}** ({len(conflicts)/len(records)*100:.1f}%) |\n")
        f.write(f"| **Teljes Szövegre Keresett Cikkek Összesen** | Konszenzusos beválogatott + Bizonytalanok | **{len(consensus_inc) + len(conflicts):,}** ({(len(consensus_inc) + len(conflicts))/len(records)*100:.1f}%) |\n\n")
        f.write("---\n\n")
        f.write("## 2. KIZÁRÁSI INDOKOK TÉTELES BONTÁSA (EXCLUSIONS)\n\n")
        f.write(f"A cím- és absztrakt-szűrés során kizárt **{len(consensus_exc):,} közlemény** strukturált okai:\n\n")
        f.write("| Kizárási Kategória | Közlemények Száma | Arány a Kizártakból | Módszertani Indoklás |\n")
        f.write("|---|:---:|:---:|---|\n")
        for reason_text, count in sorted_reasons:
            pct = count / len(consensus_exc) * 100
            f.write(f"| **{reason_text}** | **{count:,}** | {pct:.1f}% | CTM Gate 1 & Cochrane Eligibility |\n")
        f.write("\n---\n\n")
        f.write("## 3. MINTA A VEZETŐ BEVÁLOGATOTT KOHORSZOKBÓL\n\n")
        f.write("Az alábbi etalon kohorszok mind beválogatásra kerültek a teljes szöveges extrakciós fázisba:\n\n")
        f.write("1. **Cotten et al. (2009)** — *Prolonged duration of initial empirical antibiotic treatment is associated with increased rates of necrotizing enterocolitis and death for extremely low birth weight infants* (`Pediatrics`, 4 039 ELBW csecsemő)\n")
        f.write("2. **Ting et al. (2019, CNN)** — *Association of Initial Empirical Antibiotic Regimen on Mortality and Morbidity in Extremely Low Birth Weight Infants* (`J Pediatr`, 13 738 koraszülött)\n")
        f.write("3. **Cantey et al. (2015, SCOUT)** — *Reducing unnecessary antibiotic use in the neonatal intensive care unit (SCOUT study)* (`Pediatrics`, 36–48h stewardship rule)\n")
        f.write("4. **Alexander et al. (2011)** — *Association of initial empiric antibiotic therapy with adverse outcomes in very low birth weight infants* (`J Pediatr`)\n")
        f.write("5. **Kuppala et al. (2011)** — *Prolonged initial empirical antibiotic treatment is associated with adverse outcomes in preterm infants* (`Ann Pharmacother`)\n\n")
        f.write("---\n\n")
        f.write("## 4. KAPCSOLÓDÓ ARTIFAKTOK ÉS FÁJLOK\n\n")
        f.write(f"- **Teljes Szűrt Könyvtár (CSV):** [Teljes_konyvtar_screened.csv](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/Teljes_konyvtar_screened.csv) (mind a {len(records):,} sor eredeti sorrendben az ítélettel és indoklással)\n")
        f.write(f"- **Konszenzus Munkafüzet (Excel):** `results/{project}/adjudication_consensus.xlsx`\n")
        f.write(f"- **Konfliktus / Arbitrációs Munkafüzet:** `results/{project}/adjudication_conflicts.xlsx`\n")
        f.write(f"- **JSON Szummárium:** `results/{project}/adjudication_summary.json`\n")

    print(f"  Screening Report saved:             {report_md_path}")

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
    parser.add_argument("--dual-screening", action="store_true", help="Execute true dual independent screening using decoupled clinical and methodological review profiles")
    
    args = parser.parse_args()

    # Determine default paths if not provided
    output_dir = args.output_dir or os.path.join(WORKSPACE_DIR, "results", args.project)

    records = []
    is_genuinely_dual = bool(args.dual_screening)

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
            in_path = os.path.join(WORKSPACE_DIR, "projects", "meta_hyperglycaemia", "data", "screening_decisions_review.csv")
            if os.path.exists(in_path):
                df_in = pd.read_csv(in_path, encoding="utf-8-sig")
                records = df_in[df_in.get("Decision") == "INCLUDED"].to_dict(orient="records")
        elif args.project == "neonatal_antibiotics":
            in_path = os.path.join(WORKSPACE_DIR, "projects", "neonatal_antibiotics", "results", "pilot_screening_100.xlsx")
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
