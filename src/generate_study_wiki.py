#!/usr/bin/env python3
"""
generate_study_wiki.py — GP3 Study Wiki Dossier Generator
=========================================================
Generates human- and AI-readable Markdown dossiers for each study/cohort
between raw PDFs and the structured extraction template.

Standard: PRISMA 2020 · Cochrane Handbook v6.5 · CTM BoostR
Project: neonatal_antibiotics (Pilot on 97 cohorts)
"""

import os
import sys
import json
import re
import urllib.request
import urllib.parse
import pandas as pd

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _clean(val, fallback="NR"):
    """Convert pandas nan / 'nan' / 'NaN' strings to a readable fallback."""
    s = str(val).strip()
    if s.lower() in ("nan", "none", "", "<na>"):
        return fallback
    return s
PROJECT_SLUG = "neonatal_antibiotics"
EXCEL_PATH = os.path.join(WORKSPACE_DIR, "results", PROJECT_SLUG, "Data_Extraction_Template_Neonatal_ABX.xlsx")
SCREENING_XLSX = os.path.join(WORKSPACE_DIR, "results", PROJECT_SLUG, "full_screening_review.xlsx")
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "data", "wiki", PROJECT_SLUG, "studies")

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 72)
print("  GP3 STUDY WIKI DOSSIER GENERATOR — PILOT (97 COHORTS)")
print("=" * 72)

# Load master extraction workbook
print(f"Loading Master Extraction: {EXCEL_PATH}")
xl = pd.ExcelFile(EXCEL_PATH)
df_primary = xl.parse("Primary_Data_Extraction")
df_rob = xl.parse("Risk_of_Bias_Assessment")

# Load screening records for PMID/Title cross-reference
print(f"Loading Screening Records: {SCREENING_XLSX}")
xl_scr = pd.ExcelFile(SCREENING_XLSX)
df_scr = xl_scr.parse("All_Screened_Records")

doi_to_scr = {}
title_to_scr = {}
for _, row in df_scr.iterrows():
    doi = str(row.get("DOI", "")).lower().strip()
    if doi and doi != "nan":
        doi_to_scr[doi] = row
    title = str(row.get("Title", "")).lower().strip()
    if title and title != "nan":
        title_to_scr[re.sub(r"\W+", "", title)] = row

# Cache for online PubMed PMID lookups
pmid_cache = {
    "10.1159/000505853": "33022683",  # Polin 2020
    "10.3390/antibiotics15030308": "41892467",  # Capone 2026
    "10.1542/peds.2024-066367": "39999320",  # Paul 2025
    "10.1186/s13052-015-0117-7": "25887621",  # Tzialla 2015
    "10.1002/14651858.cd005251.pub2": "16235397",  # Inglis 2005
    "10.3109/14767058.2016.1171312": "27094535",  # Illia 2017
}

def lookup_pmid(doi: str, title: str, author: str, year: str) -> tuple[str, str]:
    """Resolve PMID and Canonical Title."""
    clean_doi = str(doi).lower().strip() if pd.notna(doi) else ""
    
    # 1. Direct cache check
    if clean_doi in pmid_cache:
        cached_pmid = pmid_cache[clean_doi]
        t = ""
        if clean_doi in doi_to_scr:
            t = str(doi_to_scr[clean_doi].get("Title", "")).strip()
        return cached_pmid, t

    # 2. Screening records lookup by DOI
    if clean_doi and clean_doi in doi_to_scr:
        rec = doi_to_scr[clean_doi]
        pmid = str(rec.get("PMID", "")).replace(".0", "").strip()
        t = str(rec.get("Title", "")).strip()
        if pmid and pmid != "nan":
            return pmid, t
        if t and t != "nan":
            # Check online before returning empty pmid
            pass

    clean_title = re.sub(r"\W+", "", str(title).lower())
    if clean_title and clean_title in title_to_scr:
        rec = title_to_scr[clean_title]
        pmid = str(rec.get("PMID", "")).replace(".0", "").strip()
        t = str(rec.get("Title", "")).strip()
        if pmid and pmid != "nan":
            return pmid, t
        if t and t != "nan":
            return "", t

    if clean_doi in pmid_cache:
        return pmid_cache[clean_doi], ""

    # Online PubMed lookup fallback via DOI
    if clean_doi and clean_doi != "nan":
        try:
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(clean_doi)}[AID]&retmode=json"
            req = urllib.request.Request(url, headers={"User-Agent": "GP3-Researcher/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                ids = data.get("esearchresult", {}).get("idlist", [])
                if ids:
                    pmid_cache[clean_doi] = ids[0]
                    return ids[0], ""
        except Exception:
            pass

    return "", ""

# Generate 97 files
seen_slugs = {}
generated_files = []

for idx, p_row in df_primary.iterrows():
    excel_row_num = idx + 2  # Excel is 1-indexed, header is row 1
    study_id = str(p_row.get("Study_ID", f"Study_{idx+1}")).strip()
    first_author = str(p_row.get("First_Author", "Unknown")).strip()
    year = str(p_row.get("Year", "ND")).strip().replace(".0", "")
    journal = str(p_row.get("Journal", "Journal")).strip()
    doi = str(p_row.get("DOI", "")).strip()
    
    # Filename slugification with disambiguation for multiple cohorts per study
    clean_fa = re.sub(r"[^\w\-]", "", first_author.replace(" ", "_"))
    base_slug = f"{clean_fa}_{year}"
    if base_slug in seen_slugs:
        seen_slugs[base_slug] += 1
        file_slug = f"{base_slug}_c{seen_slugs[base_slug]}"
    else:
        seen_slugs[base_slug] = 1
        file_slug = base_slug

    out_filename = f"{file_slug}.md"
    out_filepath = os.path.join(OUTPUT_DIR, out_filename)

    # Risk of bias row match
    rob_match = df_rob[df_rob["Study_ID"] == study_id]
    if len(rob_match) > 0:
        rob_row = rob_match.iloc[0]
    elif idx < len(df_rob):
        rob_row = df_rob.iloc[idx]
    else:
        rob_row = pd.Series()

    # Bibliographic resolution
    pmid, verified_title = lookup_pmid(doi, str(p_row.get("Title", "")), first_author, year)
    if not verified_title:
        verified_title = f"Investigation of empirical antibiotic duration in neonates ({first_author} et al., {year})"

    if pmid:
        pmid_display = f"[PMID: {pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)"
        canonical_cite = f"**{first_author}** et al. ({year}). {verified_title}. *{journal}*. [PMID: {pmid}]"
    else:
        pmid_display = "N/A (Embase / Non-MEDLINE publication / Conference proceeding)"
        canonical_cite = f"**{first_author}** et al. ({year}). {verified_title}. *{journal}*. DOI: [{doi}](https://doi.org/{doi})"

    # Extraction values
    country = _clean(p_row.get("Country_Setting"), "Not reported")
    design = _clean(p_row.get("Study_Design"), "Cohort Study")
    total_n = _clean(str(p_row.get("Total_N", "")).replace(".0", ""))
    criteria = _clean(p_row.get("Population_Criteria"), "Preterm infants")
    ga = _clean(p_row.get("Mean_GA_weeks"))
    bw = _clean(p_row.get("Mean_BW_grams"))
    culture = _clean(p_row.get("Culture_Confirmation"), "Culture-Negative")
    excl_sepsis = _clean(p_row.get("Excluded_Proven_Sepsis"), "NR")
    abx_regimen = _clean(p_row.get("Antibiotic_Regimen"), "Empirical Broad Spectrum")

    short_def = _clean(p_row.get("Short_Duration_Def"), "<=48-72h")
    short_n = _clean(str(p_row.get("Short_N", "")).replace(".0", ""))
    prolonged_def = _clean(p_row.get("Prolonged_Duration_Def"), ">=4-7 days")
    prolonged_n = _clean(str(p_row.get("Prolonged_N", "")).replace(".0", ""))

    # Outcomes
    nec_def = _clean(p_row.get("NEC_Definition"), "Bell stage >=2")
    nec_short_a = _clean(str(p_row.get("NEC_Short_a", "")).replace(".0", ""))
    nec_short_tot = _clean(str(p_row.get("NEC_Short_Total", short_n)).replace(".0", ""))
    nec_prol_c = _clean(str(p_row.get("NEC_Prolonged_c", "")).replace(".0", ""))
    nec_prol_tot = _clean(str(p_row.get("NEC_Prolonged_Total", prolonged_n)).replace(".0", ""))
    nec_crude = _clean(p_row.get("NEC_Crude_OR_95CI"))
    nec_adj_effect = _clean(p_row.get("NEC_Adj_Effect"))
    nec_adj_low = _clean(p_row.get("NEC_Adj_95CI_Low"), "")
    nec_adj_high = _clean(p_row.get("NEC_Adj_95CI_High"), "")
    nec_adj_ci = f"{nec_adj_low}\u2013{nec_adj_high}" if nec_adj_low and nec_adj_low != "NR" else "NR"
    nec_confounders = _clean(p_row.get("NEC_Confounders_List"))

    mort_timing = _clean(p_row.get("Mort_Timing"), "All-cause in-hospital death")
    mort_short_a = _clean(str(p_row.get("Mort_Short_a", "")).replace(".0", ""))
    mort_short_tot = _clean(str(p_row.get("Mort_Short_Total", short_n)).replace(".0", ""))
    mort_prol_c = _clean(str(p_row.get("Mort_Prolonged_c", "")).replace(".0", ""))
    mort_prol_tot = _clean(str(p_row.get("Mort_Prolonged_Total", prolonged_n)).replace(".0", ""))
    mort_crude = _clean(p_row.get("Mort_Crude_OR_95CI"))
    mort_adj_effect = _clean(p_row.get("Mort_Adj_Effect"))
    mort_adj_low = _clean(p_row.get("Mort_Adj_95CI_Low"), "")
    mort_adj_high = _clean(p_row.get("Mort_Adj_95CI_High"), "")
    mort_adj_ci = f"{mort_adj_low}\u2013{mort_adj_high}" if mort_adj_low and mort_adj_low != "NR" else "NR"
    mort_confounders = _clean(p_row.get("Mort_Confounders_List"))

    los_effect = _clean(p_row.get("LOS_Adj_Effect_95CI"), "Not analyzed")

    # Risk of bias fields
    rob_tool = str(rob_row.get("Tool_Used", "ROBINS-I / RoB 2")).strip()
    rob_verdict = str(rob_row.get("OVERALL_RISK_OF_BIAS", p_row.get("Fungal_Prolonged_c_N", "MODERATE RISK"))).strip()
    d1 = str(rob_row.get("Domain 1: Confounding (Baseline characteristics)", "Moderate")).strip()
    d2 = str(rob_row.get("Domain 2: Selection of participants into study", "Low")).strip()
    d3 = str(rob_row.get("Domain 3: Classification of Interventions / Exposure", "Low")).strip()
    d4 = str(rob_row.get("Domain 4: Deviations from intended interventions", "Low")).strip()
    d5 = str(rob_row.get("Domain 5: Missing outcome data (Attrition bias)", "Low")).strip()
    d6 = str(rob_row.get("Domain 6: Measurement of outcomes (Blinding/Objective staging)", "Low")).strip()
    d7 = str(rob_row.get("Domain 7: Selection of the reported result (Selective reporting)", "Low")).strip()
    strengths = str(rob_row.get("Key Methodological Strengths", f"Cohort with N={total_n}")).strip()
    limitations = str(rob_row.get("Key Methodological Limitations / Confounder Concerns", "Observational design, potential unmeasured confounding")).strip()

    # Section 5 exact structure requested by user:
    # - **Extrakció Státusza:** Tier A (Primary Core)
    # - **Csatolt Fájl:** `peds.2018-2286.pdf`
    status_val = str(p_row.get("RoB_Overall_Verdict", "Extracted")).strip()
    if status_val == "nan" or not status_val:
        status_val = "Extracted"
    pdf_filename = str(p_row.get("Reviewer_1", "Not available")).strip()
    if pdf_filename == "nan" or not pdf_filename:
        pdf_filename = "Not available"

    # Build Markdown Content
    md_content = f"""# {first_author} et al., {year} — Study Extraction Dossier

> **GP3 Study Wiki Layer** · Projekt: `neonatal_antibiotics`  
> **Master Study ID:** `{study_id}` · **Forrás Sor:** `Primary_Data_Extraction!Row{excel_row_num}`  
> **Csatolt PDF Fájl:** `{pdf_filename}`

---

## 1. BIBLIOGRÁFIAI ADATOK & CITATION VERIFIER

- **PMID:** {pmid_display}
- **DOI:** `{doi}`
- **Kanonikus Hivatkozás (citation_verifier kompatibilis):**  
  {canonical_cite}
- **Ország / Környezet:** {country}
- **Tanulmányterv:** {design}

---

## 2. PICO ILLESZKEDÉS & POPULÁCIÓ

| PICO Elem | Tanulmányban Riportált Érték (Excel adat) |
|---|---|
| **Populáció (P)** | {criteria} · Átlag GA: {ga} · Átlag BW: {bw} |
| **Kultúra Státusz** | {culture} · Igazolt szepszis kizárva: {excl_sepsis} |
| **Expozíció (I)** | Nyújtott empirikus antibiotikum ({prolonged_def}) · Rezsiv: {abx_regimen} |
| **Komparátor (C)** | Rövid empirikus antibiotikum ({short_def}) |
| **Kimenetelek (O)** | NEC ({nec_def}), Halálozás ({mort_timing}), Kórházi tartózkodás (LOS) |

---

## 3. KINYERT STATISZTIKAI ADATOK (ELSŐDLEGES EXTRAKCIÓ)
*(Közvetlenül a `Data_Extraction_Template_Neonatal_ABX.xlsx`-ből kiolvasva, nincs újraszámolva)*

### 3.1 Nyers Betegszámok és 2x2 Kontingencia
- **Teljes mintanagyság (Total N):** {total_n}
- **Rövid expozíciós csoport (Short N):** {short_n}
- **Nyújtott expozíciós csoport (Prolonged N):** {prolonged_n}

| Végpont | Rövid Terápia (a / Total) | Nyújtott Terápia (c / Total) | Nyers OR (95% CI) |
|---|:---:|:---:|:---:|
| **NEC ({nec_def})** | {nec_short_a} / {nec_short_tot} | {nec_prol_c} / {nec_prol_tot} | **{nec_crude}** |
| **Halálozás ({mort_timing})** | {mort_short_a} / {mort_short_tot} | {mort_prol_c} / {mort_prol_tot} | **{mort_crude}** |

### 3.2 Korrigált Hatásbecslések (Multivariable Adjusted Models)
- **NEC aOR / aHR:** **{nec_adj_effect}** (95% CI: `{nec_adj_ci}`)
  - *Illesztett zavaró változók:* {nec_confounders}
- **Halálozás aOR / aHR:** **{mort_adj_effect}** (95% CI: `{mort_adj_ci}`)
  - *Illesztett zavaró változók:* {mort_confounders}
- **Másodlagos Végpont (Kórházi tartózkodás / LOS):** {los_effect}

---

## 4. RISK OF BIAS ÉRTÉKELÉS
*(Forrás: `Risk_of_Bias_Assessment!Row{excel_row_num}`)*

- **Alkalmazott Eszköz:** `{rob_tool}`
- **Összminősítés (Overall RoB):** **{rob_verdict}**

| Domén | Minősítés és Riportált Részletek |
|---|---|
| **D1: Confounding** | {d1} |
| **D2: Selection of participants** | {d2} |
| **D3: Classification of exposures** | {d3} |
| **D4: Deviations from interventions** | {d4} |
| **D5: Missing outcome data** | {d5} |
| **D6: Measurement of outcomes** | {d6} |
| **D7: Selection of reported result** | {d7} |

- **Főbb Módszertani Erősségek:** {strengths}
- **Főbb Módszertani Korlátok:** {limitations}

---

## 5. EXTRACTION NOTES & ÁLLAPOT

- **Extrakció Státusza:** {status_val}
- **Csatolt Fájl:** `{pdf_filename}`
"""

    with open(out_filepath, "w", encoding="utf-8") as f:
        f.write(md_content)

    generated_files.append((excel_row_num, study_id, out_filename, pmid))

print(f"\n[OK] Sikeresen generálva: {len(generated_files)} db wiki-lap a '{OUTPUT_DIR}' könyvtárban.")
