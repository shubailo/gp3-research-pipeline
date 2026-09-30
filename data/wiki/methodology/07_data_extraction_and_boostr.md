# 07. CTM Adatkinyerési & BoostR Útmutató (Template v9)

> **GP3 Methodology Wiki Layer** · Centre for Translational Medicine (CTM) · Cochrane Handbook v6.5  
> **Központi Index:** [Vissza a Módszertani Tartalomjegyzékhez](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/INDEX.md) | [Főportál](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/README.md)  
> **Eredeti CTM Forrás:** `TM/CTM_DATA_EXTRACTION_GUIDE.md`

---

---
description: "Comprehensive guide for adapting, populating, and cleaning data using CTM Data Extraction Template v9 and preparing datasets for BoostR meta-analysis."
---

# CTM Data Extraction & BoostR Guide (`Data_extraction_template_v9.xlsx`)

> **Standard:** Centre for Translational Medicine (CTM / Semmelweis University) Data Collection Protocol  
> **Source Workbook:** [`Data_extraction_template_v9.xlsx`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/templates/Data_extraction_template_v9.xlsx) | Üres sablon: [`Data_extraction_template_v9_BLANK.xlsx`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/templates/Data_extraction_template_v9_BLANK.xlsx)  
> **Target Audience:** Primary Reviewer (R1), Co-Investigator (R2), Project Statistician, Senior Methodology Supervisor (SMS)

---

## 📊 Overview of the 14 Standardized Sheets

`Data_extraction_template_v9.xlsx` contains 14 specialized sheets covering baseline data, all major epidemiological outcome formats, and study-design-specific Risk of Bias instruments:

| # | Sheet Name | Description & Primary Use Case | Key Columns / Data Extracted |
|---|---|---|---|
| 1 | `Basic layout` | Study identification, design, and baseline demographic characteristics | First Author, Year, DOI, Study Design, Start/End Period, Country, Centers, Age (mean/SD/median/IQR/range), Sex, Intervention and Control characteristics |
| 2 | `ORs - RRs` | Dichotomous / binary events for two-arm comparisons | Events in Intervention ($n_I$), Total Intervention ($N_I$), Events in Control ($n_C$), Total Control ($N_C$), Precalculated crude OR/RR, Precalculated adjusted aOR/aHR |
| 3 | `Mean Difference` | Continuous comparative endpoints across two groups | Sample sizes ($N_I, N_C$), Mean, SD, Median, IQR, Range for both groups, Precalculated MD/SMD |
| 4 | `Simple mean` | Single-cohort continuous parameters | Total sample size, Mean, SD, Standard Error (SE), 95% Confidence Intervals |
| 5 | `Ratio` | Single-arm event rates, prevalence, and proportions | Total population size ($N$), Event number ($n$), Event rate / proportion |
| 6 | `Before-After` | Paired continuous observations (pre- vs. post-intervention) | Pre-intervention Mean & SD, Post-intervention Mean & SD, Paired Change Mean & SD for Intervention and Comparator |
| 7 | `Diagnostic test` | Diagnostic accuracy evaluations (PIRD framework) | True Positives (TP), False Positives (FP), True Negatives (TN), False Negatives (FN), Sensitivity, Specificity, Accuracy, AUC |
| 8 | `Correlations` | Bivariate statistical correlations | Subpopulation, Sample Size, Correlation coefficient ($r$, $\rho$), Type of correlation (Pearson, Spearman) |
| 9 | `Regression coefficient`| Multivariable prognostic models & continuous exposure regressions | Outcome, Beta coefficient ($\beta$), SD, SE, 95% CI, list of specific covariates adjusted for (Factor 1, 2, 3...) |
| 10 | `RoB2` | Cochrane Risk of Bias 2 for Randomized Controlled Trials (RCTs) | Randomization process, Deviations from protocol, Missing outcome data, Measurement of outcome, Selection of reported result |
| 11 | `QUIPS` | Quality in Prognosis Studies tool for observational/etiology cohorts | Study participation, Study attrition, Prognostic factor measurement, Outcome measurement, Study confounding, Statistical analysis and reporting |
| 12 | `Joanna-Briggs` | JBI critical appraisal tool (prevalence / incidence studies) | Patient selection, Sample size, Setting, Definition of condition, Data analysis, Confounding factors / subgroups |
| 13 | `QUADAS` | QUADAS-2 for diagnostic test accuracy studies | Patient selection, Index test, Reference standard, Flow and timing |
| 14 | `ROBINS` | ROBINS-I for non-randomized two-arm interventional studies | Confounding, Selection of participants, Intervention classification, Deviations, Missing data, Outcome measurement, Selection of reported results |

---

## 🛠️ Step-by-Step Customization Workflow

Adapting `Data_extraction_template_v9.xlsx` for a specific project must follow these rules:

### 1. Incorporate Pre-Specified Confounders into `Basic layout`
- In the `Demography`, `Intervention group`, and `Comparator/Control group` sections, insert dedicated columns for every clinically relevant confounding factor identified in the protocol's Confounder Matrix.
- *Example for Neonatal HIE:* Insert columns for Gestational age (weeks), Birth weight (g), Sarnat stage (Stage II / III), Umbilical cord pH, Base Deficit (mmol/L), Admission lactate (mmol/L), Pre-cooling seizures (Yes/No), and Cooling modality (Whole-body vs. Selective head).

### 2. Tailor Outcome Sheets (`ORs - RRs`, `Mean Difference`, etc.)
- Select the sheets corresponding to your study's outcomes and remove non-relevant sheets (e.g., delete `Diagnostic test` if your study has no diagnostic accuracy questions).
- For each distinct outcome, duplicate the entire outcome column block.
- Clearly label the **Outcome Name** and **Definition of outcome** header cells.
- If studies report both crude 2x2 data and multivariable adjusted estimates, extract raw counts into the binary columns ($n_I/N_I, n_C/N_C$) AND extract adjusted effect sizes into the `Precalculated, adjusted` columns.

### 3. Embed RoB Domains Directly per Outcome (Advanced CTM Practice)
- Because Risk of Bias is formally evaluated **per outcome**, add the relevant RoB domain columns (e.g., from the `QUIPS` or `RoB2` sheets) directly following each outcome block.
- This allows reviewers to extract quantitative effect sizes and appraise domain bias simultaneously in a single pass of the full-text paper.

---

## 🧹 BoostR Data Cleaning Checklist

Before data can be analyzed in the CTM BoostR Room or handed to the statistician, the extraction file must be verified against this mandatory checklist:

```
[ ] 1. NUMERIC ONLY
    All numerical columns (n, N, mean, SD, median, IQR, OR, CI) must contain ONLY numbers.
    - FORBIDDEN: Text strings ("not reported", "NR", "N/A", "none", "p<0.05", "approx 10").
    - Replace unavailable numeric data with completely BLANK cells or standard statistical NA as instructed.
    - FORBIDDEN: Ranges inside single cells (e.g. "10-15"). Separate into "Range min" and "Range max" columns.

[ ] 2. STANDARDIZED STUDY IDENTIFIERS
    Every single row must have a unique identifier combining Author and Year:
    - Standard format: "Perez 2023", "Ali 2024", "Chouthai 2015".
    - If an author has two publications in the same year, add distinguishing suffix: "Smith 2020a", "Smith 2020b".

[ ] 3. NO EMPTY ROWS OR INADVERTENT GAPS
    - Do NOT leave blank rows between studies in table ranges.
    - Blank rows prevent Excel and R (metafor / tidyverse) from recognizing the sheet as a continuous table.

[ ] 4. EXACT IDENTICAL OUTCOME STRINGS
    - The outcome column string defines the subsets grouped into forest plots.
    - Studies pooled into the same analysis MUST have 100% character-for-character identical strings:
      * CORRECT: All rows labeled "Mortality at discharge"
      * WRONG: Row 1 "Mortality", Row 2 "Death at discharge", Row 3 "in-hospital mortality"

[ ] 5. UNIT CONVERSION IN COPIED COLUMNS
    - All data pooled together must share the exact same physical/clinical unit (e.g. SI units: mmol/L vs. mg/dL).
    - NEVER overwrite raw extracted values during conversion!
    - Create a separate copied column: e.g., "Blood Glucose (mg/dL) [Raw]" and "Blood Glucose (mmol/L) [Converted]".
    - This preserves raw data provenance and makes errors traceable.
```

---

## 👥 Extraction Milestones & Roles

1. **Extraction Sheet Development Meeting:** Reviewer, SMS, supervisor, and statistician convene to review the tailored template.
2. **Pilot Extraction (3–4 studies):** R1 and R2 extract 3–4 studies independently, then meet to calibrate definitions.
3. **Interim Meeting at 20–30% Progress:** Mandatory checkpoint with SMS, supervisor, and statistician to audit data entry quality.
4. **Completion Meeting:** Full reconciliation of R1 and R2 sheets, arbitration of discrepancies by R3, and formal data handover to the project statistician.

---

## 🛑 Kötelező Teljes Szövegű AI Adatkinyerési Protokoll (Vak Automatizáció Tilalma)

A szisztematikus áttekintések és metaanalízisek leggyakoribb és legsúlyosabb módszertani hibái a felügyelet nélküli, automatizált adatkaparásból (scraping/regex extraction) és batch-szkriptekből erednek. A GP3 pipeline-ban ezért életbe lép a kötelező emberi/AI olvasási mandátum:

### 1. A Vak Automatizáció Szigorú Tilalma
Szigorúan tilos olyan felügyelet nélküli scripteket futtatni, amelyek a cikkek módszertanának, beválogatási kritériumainak és táblázat-lábjegyzeteinek értelmezése nélkül töltenek át számokat az extraction template-be.

### 2. A 4-Lépcsős AI Olvasási & Kinyerési Protokoll
Minden primer tanulmány feldolgozásakor az AI köteles közvetlenül elolvasni a közlemény teljes szövegét (PDF, PMC XML/HTML) az alábbi lépések szerint:

1. **Methods szekció szisztematikus átolvasása:**
   - Hogyan definiálták a beavatkozást/expozíciót?
   - Milyen pontos időablakban mérték a kimenetelt? (Pl. 24 óra, kórházi elbocsátás, 18-24 hónapos követés).
   - Mi a primer elemzési populáció (Intention-to-Treat vs. Per-Protocol / As-Treated)?
2. **Table 1 (Demográfia) & Table 2/3 (Kimenetelek) közvetlen vizsgálata:**
   - A táblázatban szereplő szám eseményszám ($n$), minta ($N$), vagy százalékos arány?
   - A folytonos adat átlag ± SD, vagy medián (IQR / range)? (Wan / Higgins konverzió kötelező, tilos a mediánt SD-ként kezelni!).
   - Mit mondanak a táblázat alatti apróbetűs lábjegyzetek (*, †, p-értékek, illesztett kovariánsok)?
3. **Szó Szerinti Provenance (Idézet-rögzítés):**
   - Minden egyes kitöltött cellához a tanulmány Markdown dossziéjában (`data/wiki/<project>/studies/<study_id>.md`) meg kell jelölni a pontos forrást:
     *Példa:* `Table 2, row 3, column 'Intervention (n=45)': "Death before discharge: 12 (26.7%)"`
4. **Kettős Ésszerűségi Ellenőrzés (Sanity Check):**
   - A csoportok részösszege megegyezik-e a beválogatott összlétszámmal? ($N_I + N_C = N_{\text{total}}$).
   - Ha a cikk nyers és korrigált becslést is közöl (crude vs. adjusted aOR/aHR), a két adat szigorúan külön oszlopba kerül-e?
