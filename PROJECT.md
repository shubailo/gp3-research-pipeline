# PROJECT.md — Persistent Research State File
> **MANDATORY:** This file is the living memory of all active research projects. AI agents MUST read this file at the start of every session involving existing projects. Agents MUST update the relevant project block after any significant decision, mentor verdict, or phase transition.

---

## 🔴 HOW AGENTS USE THIS FILE

**On session start:**
1. Read this file first
2. Identify the active project(s) by status
3. Load the current phase, open questions, and mentor scores before any analysis
4. Never re-analyze what is already settled here

**On session end (after any pipeline work):**
- Update `Status`, `Current Phase`, `Open Socratic Questions`, and `Next Step`
- Append any new mentor verdict scores
- Add newly confirmed poolable studies

---

## 📁 Active Projects

---

### Project: GLP-1 Receptor Agonists on Thermoregulation & Energy Expenditure Meta-Analysis

```
Status: 🟢 PHASE 2 (Plan Generated — docs/PLAN-glp1-thermoregulation.md)
PROSPERO: ⚠️  READY FOR REGISTRATION — Draft at docs/PROSPERO-draft-glp1-thermoregulation.md
Search Retrieval: 1,488 clean hits on PubMed (Pruned: 174 noise records removed, 3/3 benchmark RCTs verified)
Last Updated: 2026-09-22
```

**PICO:**
- **P:** Adults (≥18 years) with overweight or obesity (BMI ≥25 kg/m² or ≥30 kg/m²), with or without T2DM
- **I:** GLP-1 receptor agonists (semaglutide, liraglutide, exenatide, etc.) and dual incretin mimetics (tirzepatide, survodutide)
- **C:** Placebo, caloric restriction/lifestyle intervention, active non-incretin comparator, or baseline
- **O:** Core/skin temperature ($T_c$, $T_{sk}$), resting energy expenditure (REE/RMR; absolute and FFM-adjusted), respiratory exchange ratio / respiratory quotient (RER/RQ), fat oxidation, diet-induced thermogenesis (DIT), brown adipose tissue (BAT) activity, and heat/hydration-related adverse events (hyperthermia, dehydration, heat exhaustion)
- **Title:** *"Investigating the effect of GLP-1 receptor agonists on thermoregulation, energy expenditure, and heat-related adverse events in adults with overweight or obesity: a systematic review and meta-analysis"*

**T-Stage:** T2 (Clinical Efficacy & Safety — systematic review and meta-analysis of human randomized and controlled trials)

**Suffering Narrative:**
- *Patient:* Over 1 billion individuals live with obesity worldwide, facing multifold risks of cardiometabolic morbidity (T2DM, CVD, NAFLD) and physical disability. Attempts at caloric restriction are thwarted by adaptive thermogenesis (disproportionate drop in RMR), triggering recidivism. During summer heatwaves, obese individuals suffer double the risk of heat exhaustion and heat stroke due to thick subcutaneous insulating fat and blunted cutaneous vasodilation.
- *Family:* Long-term obesity strains family finances and quality of life. Pharmacotherapy-induced dehydration, nausea, and summer heat collapse (syncope/hyperthermia) impose sudden acute hospital caregiving burdens.
- *Clinical Hope:* Determining whether GLP-1 RAs preserve metabolic rate while identifying whether central hypodipsia/dehydration predisposes to summer heat illness will directly update international clinical obesity guidelines with mandatory heat-safety and hydration protocols.

**Sensor-Pathway-Effector (Garami Pre-Check):**
- *Sensor:* GLP-1R (and glucagon / GIP receptors) in the hypothalamus (preoptic area, arcuate nucleus), hindbrain autonomic nuclei (NTS), and peripheral vagal afferents.
- *Pathway:* Sympathetic nervous system (SNS) outflow to brown/beige adipose tissue vs. central suppression of thirst (hypodipsia) and appetite, accompanied by delayed gastric emptying, natriuresis, and subclinical hypovolemia.
- *Effector:* Non-shivering thermogenesis via mitochondrial UCP-1 activation; shift towards lipid oxidation (decreased RQ/RER); altered cutaneous vasodilation and eccrine sweating capacity under heat stress.

**Review Team:**
- Lead Reviewer (R1): Fanni Kovács (PhD Student, Nutritionist)
- Co-Lead Reviewer (R2): Teodóra Eklics (Dóri)
- Scientific Methodology Supervisor: Dalma Dobszai
- Supervisors: Dr. András Nagy, Dr. András Garami
- Translational Medicine Director & Guarantor: Prof. Péter Hegyi

**Mentor Initial Verdict Scores (2026-09-22):**
| Dimension | Prof. Hegyi | Dr. Garami |
|-----------|-------------|------------|
| Bedside Utility & Clinical Impact | 9/10 | 8/10 |
| Causal & Mechanistic Plausibility | 8/10 | 9/10 |
| Measurement Quality & Heterogeneity Risk | 7/10 | 9/10 |
| Novelty & White-Spot Gap Filling | 9/10 | 9/10 |

**Open Socratic Questions (Blocking for Phase 2):**
1. *[Garami Normalization Gate]* — How strictly will studies reporting only absolute REE (kcal/day) without FFM adjustment be handled? (Pre-specifying FFM-adjusted REE as primary subgroup).
2. *[Garami Acute vs. Chronic Gate]* — Are acute single-dose/short-term studies (measuring pure pharmacological stimulus before weight loss) pooled separately from chronic 12-52 week studies (where body mass change dominates)?
3. *[Hegyi Dual-Agonist Gate]* — Will dual GIP/GLP-1 (tirzepatide) and GLP-1/glucagon (survodutide, SAR42589) be analyzed in a dedicated subgroup distinct from pure GLP-1 RAs?

**Next Step:** Review Socratic questions in `docs/PLAN-glp1-thermoregulation.md`, register protocol on PROSPERO, and run `/research` to compile `PROTOCOL.md`.

---

### Project: Neonatal Empirical Antibiotic Duration & Safety Meta-Analysis

```
Status: 🟢 PHASE 3 (Data Extraction In Progress — 97 Cohorts [53 Tier A + 44 Tier B] Extracted into Master Sheet)
PROSPERO: ⚠️  REGISTERED (2025-12-26, AB_PROSPERO.pdf) — Amendment v2.0 at docs/PROSPERO-draft-neonatal-antibiotics.md
Search Retrieval: 2,899 total records (PubMed: 1,071; Embase: 1,709; Cochrane CENTRAL: 119)
Deduplication: 1,836 unique records in Zotero (1,063 duplicates removed)
Reviewer 1 (R1 Shubail + AI Co-Reviewer) Audit (AB_meta.csv & AB_meta_screening_R1.xlsx):
  - R1 INCLUDE (Definite PICO Eligible / Ready for Extraction): 107 records (5.8%)
  - R1 CHECK_PDF (Targeted PDF Inspection Required): 566 records (30.8%)
  - R1 EXCLUDE (Definitively Ineligible): 1,163 records (63.3%)
  -> TOTAL CANDIDATES FOR PDF RETRIEVAL (Include + Check): 673 records (36.7%)
Full-Text PDF Retrieval & Deep Data Extraction (ab_meta/ folder, N = 105 downloaded PDFs):
  - Total Extractable Cohorts Populated: 97 studies (100% extracted into Master Excel)
    * Tier A (Primary Core Meta-Analysis - NEC/Mortality): 53 studies
    * Tier B / Tier 2 (Secondary/Supportive Endpoints - LOS, BPD, Fungal, Stewardship): 44 studies
  - Excluded at Full-Text (Abstract-only, non-cohort, or narrative review): 8 studies (7.6%)
Data Extraction Master: Data_extraction_template_v9.xlsx (Official Semmelweis CTM format)
Last Updated: 2026-09-21
```

**PICO:**
- **P:** Culture-negative preterm infants (<34–37 weeks, VLBW <1500g) receiving empirical antibiotics in the first 72 hours of life
- **I:** Prolonged empirical antibiotic exposure (≥4–5 days or high exposure)
- **C:** Short empirical antibiotic exposure (≤48–72 hours / stopped upon negative culture) or no exposure
- **O:** Necrotizing enterocolitis (Bell stage ≥2) and all-cause in-hospital mortality
- **Title:** *"Investigating the effect of prolonged empirical antibiotic exposure on necrotizing enterocolitis and mortality in culture-negative preterm infants: a systematic review and meta-analysis"*

**T-Stage:** T2 (Patient-level clinical safety & prognosis — observational multicenter cohorts with multivariable adjustment)

**Suffering Narrative:**
- *Patient:* Preterm infants suffering necrotizing enterocolitis (NEC) face 30–40% mortality, emergency bowel resection, short bowel syndrome, stomas, and neurodevelopmental delay.
- *Family:* Months of agonizing NICU stay, trauma of surgical complications, lifelong disability burden.
- *Clinical Hope:* Halting unnecessary empirical antibiotics at 48–72h in culture-negative infants could directly prevent thousands of NEC cases and deaths globally each year.

**Sensor-Pathway-Effector (Garami Pre-Check):**
- *Sensor:* Intestinal epithelial TLR4 activation in immature gut
- *Pathway:* Broad-spectrum antibiotic microbiome ablation → loss of commensal Bifidobacteria → uninhibited pathogen attachment → TLR4/NF-κB inflammatory cascade (IL-8, TNF-α, PAF)
- *Effector:* Enterocyte apoptosis, mucosal ischemia, transmural bowel necrosis, pneumatosis intestinalis, bowel perforation (NEC)

**Review Team:**
- Lead Reviewer (R1): Abdulrahman Shubail
- Co-Lead: Teodóra Eklics (Dóri)
- Independent Reviewer (R2): Kata Fekete
- Biostatistician: Nelli Farkas
- Guarantor: Dr. András Garami
- Translational Mentor: Prof. Péter Hegyi

**Mentor & Biostatistician Verdict Scores (2026-09-20):**
| Dimension | Prof. Hegyi | Dr. Garami | Nelli Farkas |
|-----------|-------------|------------|--------------|
| Bedside Utility & Guideline Impact | 9/10 | 8/10 | 9/10 |
| Causal & Mechanistic Plausibility | 8/10 | 9/10 | 9/10 |
| Analytical Hierarchy & Model Rigor | 9/10 | 9/10 | 10/10 |
| Bias Protection & Sensitivity Matrix | 9/10 | 9/10 | 9/10 |

**4-Tier Analytical Hierarchy (Consensus AI Approved):**
1. *Primary Comparison:* Short (≤48h modern stewardship / ≤72h legacy) vs. Prolonged (≥4–5d or >72h) after negative cultures.
2. *Secondary Comparison 1:* No empirical antibiotics vs. Short empirical therapy (initiation decision).
3. *Secondary Comparison 2:* Broad-spectrum vs. Narrow-spectrum empirical therapy (fungal & mortality risk).
4. *Primary Dose-Response:* One-stage dose-response meta-analysis (log-OR per additional day, restricted cubic splines for non-linearity via `dosresmeta`).

**Poolable Studies Confirmed & Deep Manually Extracted from PDF Tables (k = 20 landmark cohorts with verified 2x2 counts and multivariable models):**
1. Ting et al., 2019 (*Pediatrics*, PMID: 30777949, n = 14,207 preterms, CNN Table 3) — aOR 1.02 (0.83–1.25) for NEC, aOR 1.08 (0.87–1.34) for Death, Composite aOR 1.38 (1.25–1.51)
2. Greenberg et al., 2019 (*Pediatr Res*, n = 5,730 ELBW, NICHD NRN Table 3) — aOR 0.91 (0.72–1.15) for NEC, aOR 1.17 (0.99–1.40) for Death, Fungal LOS aOR 4.95 (1.93–12.69) in non-ventilated
3. Cotten et al., 2009 (*Pediatrics*, PMID: 19117871, n = 5,693 VLBW, NICHD NRN) — aOR 1.24 (1.05–1.46) for NEC, aOR 1.34 (1.14–1.58) for Death; Daily risk +16% death (aOR 1.16), +7% NEC (aOR 1.07)
4. Ting et al., 2016 (*JAMA Pediatr*, n = 13,733 VLBW, CNN Table 3) — per 10% increase in AUR: Mortality aOR 2.04 (1.87–2.21), Composite aOR 1.18 (1.13–1.23), ROP >=3 aOR 1.18 (1.06–1.32)
5. Alexander et al., 2011 (*J Pediatr*, n = 372 VLBW, Table 3) — per-day exposure in culture-negative: aOR 1.10 (1.02–1.19); dose-response up to >10d aOR 2.94
6. Kuppala et al., 2011 (*J Pediatr*, n = 365 VLBW Table 2) — 1–4d vs >=5d: NEC aOR 1.28 (0.42–3.93), Death aOR 1.12 (0.40–3.10), LOS aOR 2.45 (1.28–4.67), Composite aOR 2.66 (1.12–6.30)
7. Mackay et al., 2026 (*Pediatr Res*, n = 3,235 preterms <32w) — <=2d vs >=5d: NEC aOR 1.44 (1.10–1.89), Death aOR 1.45 (1.19–1.76), BPD aOR 2.54 (1.94–3.33)
8. Zhu et al., 2022 (*Front Pediatr*, n = 567 VLBW, Table 3) — per day IEAT aOR 1.267 (1.128–1.423) for NEC; A/H ratio aOR 8.718 (2.450–31.030)
9. Zhu et al., 2023 (*Ital J Pediatr*, n = 480 preterms) — <=4d vs >4d: NEC aOR 5.42 (1.94–14.80), LOS aOR 2.75 (1.54–4.88)
10. Flannery et al., 2018 (*J Perinatol*, n = 4,950 preterms) — <=48h vs 3–7d: Death aOR 3.01 (1.59–5.71)
11. Abdel Ghany et al., 2012 (*J Perinatol*, n = 207 VLBW) — per day empiric therapy: NEC OR 1.31 (1.04–1.65), Death OR 1.44 (1.23–1.68)
12. Stocker et al., 2016/2017 (NeoPInS Lancet RCT, n = 1,710) — PCT-guided vs Standard: NEC RR 0.44 (0.14–1.42), Death RR 0.49 (0.12–1.95)
13. Cantey et al., 2018 (*J Pediatr*, n = 374 VLBW Table 2) — per day DOT after controlling for CRIB II: composite sepsis/NEC/death aOR 1.24 (1.17–1.31); LOT aOR 1.47 (1.32–1.64)
14. Cantey et al., 2017 (*J Pediatr*, n = 1,140 VLBW Table 2) — per day DOT adjusting for CRIB II: Death or BPD aOR 1.13 (1.09–1.16); Severe BPD aOR 1.16 (1.04–1.33)
15. Cantey et al., 2016 (SCOUT Lancet Infect Dis, n = 2,502) — 48h hard-stop stewardship safely reduced DOT by 27% without increasing NEC (3.7% vs 5.3%) or mortality (6.1% vs 6.8%)
16. Al Turk & Baier 2017 (*J Matern Fetal Neonatal Med*, n = 141 preterms <29w Table 5) — >48h vs <=48h: Death 2/17 (11.8%) vs 0/42 (0%), p = 0.024; NEC 2/17 (11.8%) vs 1/42 (2.4%)
17. Al-Mouqdad et al., 2018 (*Int J Pediatr Adolesc Med*, n = 295 preterms Table 4) — >5d vs <=5d: NEC 97/191 (50.8%) vs 5/104 (4.8%), p < 0.001; LOS 50/191 (26.2%) vs 4/104 (3.8%)
18. Tolia et al., 2016 (*Am J Perinatol*, n = 674 VLBW Table 2 & 3) — 48h ASO reduced >48h abx from 63% to 41%; NEC: 24/313 (7.7%) vs 19/361 (5.3%); Death/NEC OR 0.69 (0.46–1.05)
19. Dimopoulou et al., 2024 (*Pediatr Res*, n = 21,326 infants across 13 networks Table 1) — CN >=5d (n=7996) vs CN <5d (n=13330): Mortality 65 (0.81%) vs 162 (1.2%)
20. Rao et al., 2025 (*BMC Infect Dis*, n = 172 preterms Table 2) — Culture-negative vs Culture-positive: Death aOR 1.57 (0.52–4.74), BPD aOR 0.10 (0.02–0.52)


**PRISMA 2020 Flow & Title/Abstract Screening Results:**
- **Databases Searched:** PubMed (1,071), Embase Articles (1,638), Embase Trials (71), Cochrane CENTRAL (119)
- **Total Records Retrieved:** 2,899 (2,780 local file parsed)
- **Duplicates Removed:** 960 (local parser) / 1,063 (Zotero deduplication)
- **Unique Records Screened at Title & Abstract:** **1,820 records** (or 1,836 in Zotero)
- **Excluded at Title/Abstract:** **1,127 records (61.9%)**
  - No duration / course length analyzed: 477
  - Animal / in vitro model: 353
  - Narrative review / guidelines / secondary literature: 111
  - Term infants / non-preterm older pediatric: 64
  - No target clinical outcome (NEC / mortality / sepsis): 47
  - Insufficient PICO match: 41
  - No antibiotic therapy: 20
  - Adult / geriatric: 7
  - Structural congenital surgical malformations: 5
  - Post-NEC treatment duration: 2
- **Retained for Full-Text PDF Review:** **693 candidate records (38.1%)**
  - Clear PICO Match (High Probability): **116 records (6.4%)**
  - Borderline / Culture-negativity Verification Required: **577 records (31.7%)**
- **Generated Workbooks & Data Files:**
  - Master Workbook: [`results/neonatal_antibiotics/full_screening_review.xlsx`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/results/neonatal_antibiotics/full_screening_review.xlsx) & `C:\Users\shuba\Downloads\full_screening_review.xlsx`
  - Shortlisted Candidates Workbook: [`results/neonatal_antibiotics/full_text_candidates.xlsx`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/results/neonatal_antibiotics/full_text_candidates.xlsx) & `C:\Users\shuba\Downloads\full_text_candidates.xlsx`
  - Summary JSON: [`results/neonatal_antibiotics/full_screening_summary.json`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/results/neonatal_antibiotics/full_screening_summary.json)

**Open Socratic Questions (Resolved & Operationalized):**
1. *[Hegyi Comparison Gate - RESOLVED]* — 4-tier hierarchy pre-specified: Primary analysis evaluates Short vs. Prolonged after negative cultures.
2. *[Farkas Dose-Response Gate - RESOLVED]* — One-stage dose-response meta-analysis pre-specified using restricted cubic splines (`dosresmeta`) alongside categorical cutoffs.
3. *[Garami Immortal Time Gate - RESOLVED]* — Death <48h excluded; studies classified by exposure assignment window (fixed 48–72h vs. cumulative DOT); sensitivity analysis excluding studies with >48h survival entry criteria.
4. *[Confounder Matrix Gate - RESOLVED]* — Mandatory tracking of SNAPPE-II/CRIB-II, mechanical ventilation, inotropes, maternal IAP, and feeding ecology (human milk vs. formula).

**Next Step:** Full-text PDF retrieval for the 693 shortlisted candidates (focusing first on the 116 high-probability cohorts), followed by dual-reviewer eligibility assessment and data extraction into `Data_extraction_template_v9.xlsx`.

---

### Project: Hyperglycaemia & Therapeutic Hypothermia Meta-Analysis

```
Status: 🟢 ADVANCED — Protocol Validated (100/100, 8 Gates Passed)
PROSPERO: ⚠️  READY FOR REGISTRATION — Protocol at meta_hyperglycaemia/meta_analysis_protocol_PROSPERO.md
Last Updated: 2026-09-19
```

**PICO:**
- **P:** Neonates with hypoxic-ischaemic encephalopathy (HIE) undergoing therapeutic hypothermia
- **I:** Hyperglycaemia (elevated blood glucose) during cooling
- **C:** Normoglycaemia during cooling
- **O:** Neurodevelopmental outcomes (Bayley scores, mortality, MRI injury)
- **Title:** *"Investigating the effect of hyperglycaemia on neurodevelopmental outcomes in neonates with HIE undergoing therapeutic hypothermia"*

**T-Stage:** T2 (Patient-level clinical efficacy — systematic review of observational cohorts)

**Suffering Narrative:**
- *Patient:* Neonates with HIE suffer cerebral palsy (15-20%), cognitive impairment, epilepsy, and 15-25% mortality
- *Family:* Lifelong caregiving burden; 40-60% of affected families report depression, financial strain from specialist care
- *Clinical Hope:* Identifying hyperglycaemia as a modifiable risk factor could enable glucose monitoring protocols that reduce neurodevelopmental disability in 20,000+ neonates/year globally

**Mentor Scores (Last Updated: 2026-09-19):**
| Dimension | Prof. Hegyi | Dr. Garami |
|-----------|-------------|------------|
| Utility / Mechanistic Plausibility | 8/10 | 8/10 |
| Feasibility / Measurement Quality | 8/10 | 7/10 |
| Novelty / Heterogeneity Risk | 7/10 | 6/10 |
| Problem Solving / Bias Risk | 9/10 | 7/10 |

**Poolable Studies Confirmed (k = 4, Pooled OR = 2.057 [1.065, 3.972], I² = 55.9%):**
| Author, Year | Population | Glucose Threshold | Primary Outcome | Full Text | Poolable? |
|---|---|---|---|:---:|:---:|
| Perez et al., 2023 ([PMID: 37655394](https://pubmed.ncbi.nlm.nih.gov/37655394)) | n = 491, HIE + TH | BG > 200 mg/dL (>11.1 mmol/L) | In-hospital mortality & Death/NDI | ✅ Yes | ✅ **YES** |
| Ali et al., 2024 ([PMID: 38782623](https://pubmed.ncbi.nlm.nih.gov/38782623)) | n = 153, HIE + TH | BG > 180 mg/dL (>10.0 mmol/L) | Mortality & Unfavorable NDO | ✅ Yes | ✅ **YES** |
| Chouthai et al., 2015 ([PMID: 26410436](https://pubmed.ncbi.nlm.nih.gov/26410436)) | n = 102, HIE + TH | BG > 180 mg/dL (>10.0 mmol/L) | Mortality & Brain injury on MRI | ✅ Yes | ✅ **YES** |
| Basu et al., 2017 ([PMID: 27799322](https://pubmed.ncbi.nlm.nih.gov/27799322)) | n = 107, HIE + TH | BG > 150 mg/dL (>8.3 mmol/L) | Mortality & Death or Severe NDI | ✅ Yes | ✅ **YES** |

**Search Key (3-Domain Empirically Validated across 3 Databases):**
- **PubMed (594 clean hits):**
  `("Hypoxia-Ischemia, Brain"[MeSH] OR neonat* OR newborn* OR infant* OR perinatal*) AND (glyce* OR glycae* OR hyperglyce* OR hypoglyce* OR "blood glucose" OR "glucose level") AND (hypotherm* OR cool*)`
- **Embase (1,561 clean hits):**
  `('newborn'/exp OR neonat* OR newborn* OR perinatal* OR 'premature infant'/exp OR preterm*) AND ('hyperglycemia'/exp OR hyperglyce* OR 'hypoglycemia'/exp OR hypoglyce* OR 'blood glucose'/exp OR glyce* OR glycae* OR 'glucose level*') AND ('hypothermia, induced'/exp OR hypotherm* OR cool*)`
- **Cochrane CENTRAL (23 hits / 15 Trials):**
  `("therapeutic hypothermia" OR "cooling therapy" OR "therapeutic cooling" OR "whole body cooling" OR "head cooling") AND ("hyperglycemia" OR "hyperglycaemia" OR "hypoglycemia" OR "hypoglycaemia" OR "blood glucose" OR "glycemia" OR "glycaemia" OR "glucose level") AND ("neonatal" OR "neonate" OR "newborn")`
- *Empirically pruned noise:* `rewarming` (cardiopulmonary bypass surgery noise), `insulin` (animal IGF-1/adult T1D noise), `asphyxi*` in Embase (adult toxicology/animal stunning noise), `lability`, `CGM`, `target temperature management`. `glucose level` kept (protects Beken 2014 cohort).

**Search & Screening Library (PRISMA Ingestion Completed 2026-09-19):**
- **Raw Records Retrieved (N = 930):** PubMed (657), Embase / Scopus via Elsevier API (233), Cochrane CENTRAL/CDSR (40), Web of Science (Clarivate requires institutional API key, documented for PRISMA flowchart).
- **Deduplication:** 116 cross-database duplicates removed; 814 unique records evaluated.
- **Full-Text Eligibility Screening Results (PRISMA Full-Text Adjudication Completed 2026-09-19):**
  - **Reports Assessed at Full-Text:** 128 records
  - **EXCLUDED at Full-Text:** 112 records
    - *No therapeutic hypothermia (spontaneous/accidental hypothermia only):* 47
    - *No hyperglycemia or glycemic profile analyzed (other biomarkers only):* 41
    - *Review / Guideline / Consensus without primary data:* 7
    - *Qualitative narrative without extractable quantitative risk estimates:* 7
    - *Animal / Preclinical model:* 4
    - *Non-HIE / Preterm population:* 2
    - *Maternal diabetes / Fetal growth restriction:* 2
    - *Conference proceedings / abstract only:* 1
    - *Pediatric cardiac arrest (non-neonatal):* 1
  - **INCLUDED IN QUANTITATIVE META-ANALYSIS:** **16 landmark studies** (CoolCap post-hoc RCT cohorts, multicenter prospective/retrospective HIE cohorts, and CGM monitoring cohorts).
- **Review Artifacts:**
  - Styled Multi-Sheet Review & Extraction Workbook: [`meta_hyperglycaemia/full_text_review_and_extraction.xlsx`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/meta_hyperglycaemia/full_text_review_and_extraction.xlsx)
  - Full-Text Summary JSON: [`meta_hyperglycaemia/full_text_summary.json`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/meta_hyperglycaemia/full_text_summary.json)
  - Baseline Screening Library (814 records): [`meta_hyperglycaemia/screening_decisions_review.xlsx`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/meta_hyperglycaemia/screening_decisions_review.xlsx)

**Open Socratic Questions (Resolved & Operationalized):**
1. *[Hegyi Confounder Gate - RESOLVED]* — Protocol updated with Tier 1 (crude) and Tier 2 (multivariable adjusted aOR controlling for Sarnat, pH, base deficit, lactate) dual synthesis.
2. *[Garami Timing Gate - RESOLVED]* — Glucose timing stratified into 3 physiological windows: 0–12h (asphyxia/stress), 12–72h (steady-state cooling), and >72h (rewarming).
3. *[Garami Threshold Gate - RESOLVED]* — Pre-specified subgroup analysis across >8.0, >10.0, and >11.1 mmol/L cutoffs.

**Next Step:** Submit protocol to PROSPERO (with attached PRISMA-trAIce annex), perform 2-reviewer duplicate data extraction on the 16 included studies, and run the two-tier meta-analytic synthesis (crude OR + confounder-adjusted aOR).

---

### Project: LPS-Induced Pain Hyperalgesia Meta-Analysis

```
Status: 🟡 ACTIVE — Phase 1 (PICO + Suffering Narrative)
PROSPERO: ⚠️  NOT YET REGISTERED — Draft at docs/meta_analysis_protocol_LPS_pain_PROSPERO.md
Last Updated: 2026-09-19
```

**PICO:**
- **P:** Healthy adult human volunteers (18–65y)
- **I:** Intravenous LPS administration (experimental endotoxemia)
- **C:** Placebo (normal saline)
- **O:** Pain threshold changes (hyperalgesia/allodynia — quantitative sensory testing)
- **Title:** *"Investigating the effect of experimental LPS endotoxemia on pain sensitivity in healthy human volunteers"*

**T-Stage:** T1 (Bench-to-human translation — first-in-human biology of cytokine-pain pathway)

**Sensor-Pathway-Effector (Garami Pre-Check):**
- *Sensor:* TLR4 (Toll-like receptor 4) activated by LPS endotoxin
- *Pathway:* NF-κB → COX-2 upregulation → PGE2 release → central sensitisation via spinal cord dorsal horn
- *Effector:* Reduced pain thresholds (PPT/HPT via quantitative sensory testing)

**Open Socratic Questions (Blocking):**
1. Garami Q: What is the LPS dose-response standardisation across studies? Different doses (0.2 vs. 1.0 ng/kg) produce different cytokine peaks — pooling is only valid within dose bands
2. Hegyi Q: Is there a clinical population this translates to? (Sepsis? Post-operative pain?) The translational bridge must be explicit

**Next Step:** Phase 2 literature search — confirm ≥3 studies report identical pain outcome metric (PPT in kPa, or HPT in °C) before proceeding

---

### Project: TRPA1 Neurogenic Flare Meta-Analysis

```
Status: 🟢 ADVANCED — Protocol drafted
PROSPERO: ⚠️  NOT YET REGISTERED — Draft at docs/meta_analysis_protocol_TRPA1_flare_PROSPERO.md
Last Updated: 2026-09-19
```

**PICO:** [See docs/meta_analysis_protocol_TRPA1_flare_PROSPERO.md for full protocol]

**Next Step:** Run `python src/validate_protocol.py docs/meta_analysis_protocol_TRPA1_flare_PROSPERO.md` then register on PROSPERO

---

## 📋 System Health

```
validate_protocol.py:    ✅ Operational (7 gates, tested)
screen_literature.py:    ✅ Operational (multi-source, PICO filter)
literature_search.py:    ✅ Operational (PubMed live search)
citation_verifier.py:    🆕 NEW — Available at src/citation_verifier.py
prisma_trace_reporter.py: 🆕 NEW — Available at src/prisma_trace_reporter.py
forest_plot_builder.py:  🆕 NEW — Available at src/forest_plot_builder.py
```

---

## 📌 Global Rules Reminders

- NEVER use `NOT` boolean operator in search keys
- Poolability Gate: ≥3 primary studies with **identical** primary outcome required before meta-analysis
- PROSPERO registration MUST occur before data extraction begins
- All PROTOCOL.md files require `python src/validate_protocol.py` score ≥70/100
- GRADE Summary of Findings Table is mandatory for all synthesis reports
