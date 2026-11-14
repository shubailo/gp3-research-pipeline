# 05. Protocol Design & PROSPERO Registration Guide

> **GP3 Methodology Wiki Layer** · Centre for Translational Medicine (CTM / Semmelweis University) · Cochrane Handbook v6.5 · PRISMA-P  
> **Central Index:** [Back to Methodology Index](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/INDEX.md) | [Main Portal](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/README.md)  
> **Canonical CTM Source:** [`PROSPERO_REGISTRATION_GUIDE_v6.1.md`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/resources/PROSPERO_REGISTRATION_GUIDE_v6.1.md) (*CTM PROSPERO Registration Guide Version 6.0 / updated April 2025*) & `TM/protocol-registration.MD`  
> **Copy-Paste Form Template:** [`PROSPERO_REGISTRATION_TEMPLATE.md`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/templates/PROSPERO_REGISTRATION_TEMPLATE.md)

---

## 1. Executive Summary & Why Register a Protocol?

Prospective submission and public registration of key design elements of a systematic review and meta-analysis is **mandatory, non-negotiable, and time-critical**. 

Protocol registration guarantees that studies are executed to the highest international standards of reproducible scientific evidence:
1. **Prevents Unintentional Duplication:** Allows international research teams to verify ongoing work and prevents redundant waste of clinical and academic resources.
2. **Eliminates Reporting & Analytical Biases:** Establishes a transparent, timestamped *a priori* record of planned comparisons, eligibility criteria, and primary endpoints before studies are screened or extracted.
3. **Institutional & Journal Prerequisite:** Top-tier medical journals (e.g., *The Lancet*, *BMJ*, *JAMA*, *Annals of Internal Medicine*) and the Centre for Translational Medicine (CTM) require prospectively registered protocol IDs (e.g., PROSPERO `CRD4202...`) as a precondition for peer review and manuscript acceptance.

---

## 2. Mitigating Reporting Biases Through Prospective Registration

Registering a systematic review protocol prospectively directly counters the six primary forms of reporting bias recognized by the Cochrane Collaboration:

- **Publication Bias:** Studies demonstrating positive or statistically significant results are more likely to be published than studies showing null or negative results. An *a priori* protocol establishes the comprehensive clinical scope regardless of published study outcomes.
- **Time-Lag Bias:** Studies with positive findings are published substantially faster than those with negative or inconclusive findings.
- **Location Bias:** Positive and significant findings are often published across higher-impact or multiple international journals, while negative findings remain restricted to institutional or regional repositories.
- **Citation Bias:** Authors selectively cite positive studies that align with their preconceived hypotheses. A protocol commits researchers to exhaustive, objective bibliographic searches.
- **Language Bias:** Studies with statistically significant findings are disproportionately translated and published in English-language journals.
- **Selective Reporting Bias:** Investigators extract multiple clinical endpoints but report only the subset that achieved statistical significance.  
  > ⛔ **CTM Selective Reporting Rule:** You must report **ALL** outcomes prespecified in the registered protocol, regardless of whether the effect estimates are statistically significant, null, or opposite to your hypothesis.

---

## 3. The PROSPERO Database & International Standards

**PROSPERO** (International Prospective Register of Systematic Reviews), maintained by the National Institute for Health and Care Research (NIHR) and the Centre for Reviews and Dissemination (CRD) at the University of York, is the global benchmark for systematic review registration.

- **Scope:** Free-of-charge, open-access, peer-reviewed international registry.
- **Reporting Standard:** Aligned with the PRISMA-P (Preferred Reporting Items for Systematic review and Meta-Analysis Protocols) guidelines.
- **Permanent Identifiers:** Assigns a citable, unique registration number (e.g., `CRD42025xxxxxx`) upon editorial validation.
- **Mandatory Pre-Search:** Researchers must perform an exploratory search on PROSPERO *before* finalizing their research question to ensure no identical systematic review is currently underway.

---

## 4. Institutional CTM Governance & Pre-Submission Workflow

At the Centre for Translational Medicine (Semmelweis University), protocol registration follows a strict supervisory approval workflow:

```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ CTM PROTOCOL REGISTRATION TIMELINE & GOVERNANCE GATE                                  │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Feasibility & Search Key Approval (SMS Gate 1 & 2 passed)                          │
│                                  │                                                    │
│                                  ▼                                                    │
│ 2. Create Shared PROSPERO Account (Share credentials with your SMS)                   │
│                                  │                                                    │
│                                  ▼                                                    │
│ 3. Complete PROSPERO Online Draft (Strictly following CTM Guide v6.0 / this playbook) │
│                                  │                                                    │
│                                  ▼                                                    │
│ 4. ⛔ "DO NOT SUBMIT" GATE: SMS Formal Review & Audit                                 │
│    • Only the SMS-approved draft may be officially submitted to NIHR PROSPERO.        │
│                                  │                                                    │
│                                  ▼                                                    │
│ 5. Formal Submission & Identifier Receipt (CRD4202...)                                │
│    • Physical timing gate: Screening & extraction CANNOT begin before submission.     │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **Account Credential Sharing:** When creating your PROSPERO account, use a password that you do not mind sharing with your Scientific Methodology Supervisor (SMS). The SMS will log into your account to perform the final compliance audit prior to submission.

> [!CAUTION]
> **⛔ The "DO NOT SUBMIT" Rule:** Under no circumstances should a researcher click the final submission button on PROSPERO without explicit written confirmation and signoff from their SMS. Submissions with methodological flaws cause weeks of review delay or irreversible rejection.

---

## 5. Starting a New Project: Screens 1 to 6

When logging into PROSPERO to initiate a new project, follow these initial navigation steps:

### 1) Create a New Record
Click **`"Create a new PROSPERO record..."`** in your My PROSPERO dashboard.

### 2) Read and Accept Terms of Use
Carefully review the terms and check:  
`☑ I have read and understand the terms above and agree to abide by them`.

### 3) Human or Animal Project?
- **Option to select:** `"A systematic review of studies with people/humans as participants"`
- > [!WARNING]
  > **Animal Reviews Suspended:** As of April 2025, NIHR PROSPERO has temporarily suspended the registration of animal pre-clinical reviews. Systematic reviews involving animal models cannot currently be registered on PROSPERO.

### 4) Student Project vs. Professional Review Trap (CRITICAL)
- **Question:** *"Is this registration record being created by a student as part of a course or module?"*
- **Mandatory Selection:**  
  `🔘 This record is NOT being created as part of a student project or training course`
- > [!CAUTION]
  > **Fatal Rejection Pitfall:** If you select *"This PROSPERO record is being created as part of a training course"*, PROSPERO will **NOT publish your record on the public website**; it will only be archived internally for educational evaluation and will lack a public citable registration link required by scientific journals! Even as a PhD or master's student at CTM, your research is an intended peer-reviewed scientific publication, so you must select **`"This record is NOT being created as part of a student project or training course"`**.

### 5) Choose Your Review Type
- **Mandatory Selection:**  
  `🔘 Intervention review`
- > [!NOTE]
  > As of April 2025, only `"Intervention review"` is open for active selection in the updated NIHR PROSPERO platform (diagnostic, prognostic, and incidence/prevalence options are marked as "Coming soon"). CTM mandates selecting `"Intervention review"` for **all review designs** until additional specialized forms are re-enabled.

### 6) Initiate Protocol
Click **`"Register your review now"`** to open the 12-section protocol editor.

---

## 6. Field-by-Field CTM Playbook: The 12 Canonical Sections

### Section 1: Review Title and Basic Details

- **a) Review Title:**
  - **Standard:** Use the working title exactly as approved at your CTM Group Meeting.
  - **Mandatory Suffix:** Must explicitly include `"Systematic review and Meta-analysis"`.
  - *Format:* `Investigating the effect of [Exposure/Intervention] on [Outcome] in [Population]: A Systematic Review and Meta-Analysis`
- **b) Condition or Domain Being Studied:**
  - **PICO Tags:** Select 2–4 relevant standardized PICO tags from the dropdown.
  - **Background Text:** Provide a concise (5–6 sentences) biological and clinical overview of the disease, intervention, or exposure being investigated (derived from your Group Meeting presentation).
- **c) Rationale for the Review:**
  - Explain why this review is necessary now, what gap in knowledge it fills, and how it informs clinical guidelines, health economics, or bedside patient survival.
- **d) Review Objectives:**
  - State your primary clinical question formulated in strict PICO structure (e.g., *"To assess the efficacy and safety of [Intervention] compared with [Comparator] in [Population] for reducing [Outcomes]."*).
- **e) Keywords:**
  - Enter $\ge 3$ MeSH or high-yield clinical keywords separated by commas (e.g., `heart failure; sodium-glucose transporter 2 inhibitors; mortality; cardiovascular outcomes` or `infant, premature; sepsis; anti-bacterial agents; mortality`).
- **f) Country:**
  - Select: `Hungary`.

---

### Section 2: Eligibility Criteria

- **a) Population:**
  - **Inclusion Criteria:** Clearly specify the target clinical cohort (e.g., *"Adult patients (≥18 years) with confirmed heart failure with reduced ejection fraction (HFrEF ≤40%)"* or *"Preterm infants (<37 weeks gestational age) receiving empirical antibiotic therapy for suspected early-onset sepsis"*).
  - **Exclusion Criteria:** Clearly specify excluded groups (e.g., *"Patients with end-stage renal disease on dialysis, cardiogenic shock at baseline, or age <18 years"* or *"Neonates with major congenital malformations, known chromosomal abnormalities, or confirmed viral infection"*).
- **b) Intervention(s) or Exposure(s):**
  - **PICO Tags:** Search and assign appropriate tags.
  - **Inclusion Criteria:** Describe the intervention or exposure in precise clinical terms. If investigating comorbidities or biomarker ranges, list every parameter explicitly.
  - **Exclusion Criteria:** Specify non-eligible exposures or combinations.
- **c) Comparator(s) or Control(s):**
  - **Question:** *"Does this review compare the intervention with another treatment or with a control?"*
  - Select the appropriate radio button based on your project design:
    - `🔘 This review compares intervention(s) with a control or other intervention(s)` *(Standard for comparative reviews)*
    - `🔘 This review includes both comparative and non-comparative studies`
    - `🔘 This review does not have any comparator(s) or control(s)` *(Single-arm prevalence/prognosis)*
  - Assign comparator PICO tags and describe comparator inclusion/exclusion criteria.
- **d) Study Design:**
  - **Checkboxes:** Check `☑ Randomised studies` and/or `☑ Non-randomised studies` according to your protocol.
  - **Inclusion Text:** Specify eligible designs (e.g., *"Randomized controlled trials, prospective cohort studies, retrospective cohort studies, and registry-based analyses."*).
  - **Exclusion Text:** Explicitly exclude low-evidence designs: *"Case reports, case series (n < 10), letters, editorials, conference abstracts without full methodology, and review articles."*
- **e) Context:**
  - Provide relevant care setting constraints without repeating PICO text (e.g., *"Hospital inpatient settings (Level III/IV Neonatal Intensive Care Units). Studies conducted in low-, middle-, and high-income countries will be included."*).

---

### Section 3: Similar Reviews Check & Duplication Evaluation

- **Step 1:** Under *"Check similar PROSPERO registrations?"*, select:  
  `🔘 Show similar records`
- **Step 2:** Review the automatically generated list of existing registrations.
- **Step 3 (If No Overlap Exists):** Select:  
  `🔘 This review is different to our review`
- **Step 4 (If Similar Records Exist):**
  - Select: `🔘 This review is similar to our review. It addresses a similar research question`
  - Select: `🔘 I will proceed with my registration`
  - Under *"Give your reasons for proceeding?"*, check all that apply:
    - `☑ There are differences in population`
    - `☑ There are differences in intervention or comparator`
    - `☑ Our review looks at additional or different outcomes`
  - > [!IMPORTANT]
    > **Supervisory Rule:** If a similar PROSPERO record exists, you must consult your SMS and senior supervisor before proceeding to confirm your study's distinct clinical justification.

---

### Section 4: Timeline of the Review

- **Anticipated Start Date:** Beginning of the academic year (e.g., `2025/09/01` or `2026/09/01`).
- **Anticipated Completion Date:** Exactly one calendar year after the start date (e.g., `2026/08/31` or `2027/08/31`).

---

### Section 5: Availability of Full Protocol

- **Mandatory Selection:**  
  `🔘 A full protocol has not been written`
- *CTM Rationale:* In standard CTM workflows, we do not author and publish a standalone protocol paper prior to PROSPERO registration; the PROSPERO record itself serves as the official prospectively published protocol.

---

### Section 6: Searching and Screening

- **a) Search for Unpublished Studies:**
  - Select: `🔘 We will search for published studies`
- **b) Main Bibliographic Databases Searched:**
  - **Mandatory Core Databases:** Check `☑ PubMed`, `☑ Embase`, and `☑ Cochrane Central Register of Controlled Trials (CENTRAL)`.
  - **Supplementary Databases:** Add `Scopus`, `Web of Science`, or clinical trials registries (`ClinicalTrials.gov`) under `"Other"` as required by your project protocol.
- **c) Search Language Restrictions:**
  - Select: `🔘 No search language restrictions`
- **d) Search Date Restrictions:**
  - Select: `🔘 There are no search date restrictions` (unless justified by historical emergence, e.g., December 2019 for COVID-19).
- **e) Other Methods of Identifying Studies:**
  - Select:
    - `☑ contacting authors or experts`
    - `☑ reference list checking`
    - `☑ searching trial or study registers`
    - `☑ looking through all the articles that cite the papers included in the review ("snowballing")`
    - *(Check `☑ searching conference proceedings` only if conference abstracts are eligible)*
- **f) Link to Search Strategy (MANDATORY PDF UPLOAD):**
  - Select: `🔘 Upload your search strategy to PROSPERO in PDF format`
  - Prepare a clean, standalone PDF containing the full, reproducible search keys adapted for all target databases (PubMed, Embase, CENTRAL) following the CTM 3-domain architecture. Upload this PDF directly.
- **g) Selection Process:**
  - Select: `🔘 Studies screened independently by at least 2 people (or person/machine combination) with a process to resolve differences`
  - Text description: *"Two independent review authors will screen titles and abstracts against eligibility criteria in Rayyan. Potentially eligible articles will be evaluated in full text. Disagreements will be resolved through consensus or arbitration by a third senior reviewer."*
- **h) Other Relevant Information:** Leave blank or note reference management software (e.g., EndNote, Rayyan).

---

### Section 7: Data Collection Process

- **a) Data Extraction from Published Articles:**
  1. *Extracting data:* Select `🔘 Data will be extracted independently by at least two people (or person/machine combination) with a process to resolve differences`.
  2. *Individual Participant Data (IPD):* Select `🔘 No – IPD will not be sought` (unless an IPD meta-analysis has been specifically designed).
- **b) Study Risk of Bias or Quality Assessment:**
  1. *Will risk of bias be assessed?* Select `🔘 Risk of bias/study quality will be assessed`.
  2. *Tools utilized:* Select tools strictly matching your included study designs:
     - Randomized Controlled Trials: **RoB 2** (Risk of Bias 2)
     - Non-Randomized Studies of Interventions: **ROBINS-I**
     - Prognostic / Observational Cohort Studies: **QUIPS** (Quality in Prognosis Studies)
     - Diagnostic Test Accuracy: **QUADAS-2**
     - Prevalence Studies: **JBI Critical Appraisal Tools**
  3. *Assessors:* Select `🔘 Studies will be assessed independently by at least two people (or person/machine combination) with a process to resolve differences`.
  4. *Additional information from investigators:* Select `🔘 No, additional information will not be sought from study investigators`.
- **c) Reporting Bias Assessment:**
  - Select: `🔘 No - risk of bias due to missing results will not be assessed`
- **d) Certainty Assessment:**
  - Select `🔘 Yes` or `🔘 No`. If Yes, state: *"The certainty of evidence will be evaluated using the Grading of Recommendations Assessment, Development and Evaluation (GRADE) framework across risk of bias, inconsistency, indirectness, imprecision, and publication bias."*

---

### Section 8: Outcomes to be Analyzed

- **a) Main Outcomes:**
  - Specify each primary endpoint, its exact clinical definition, measurement tool/scale, time point of assessment, and intended effect measure (MD, SMD, OR, RR, HR).
  - > [!IMPORTANT]
    > **The 1 Safety + 1 Efficacy Rule:** In CTM systematic reviews, main outcomes MUST contain **at least one efficacy outcome** (e.g., neurodevelopmental impairment, clinical cure, survival) and **at least one safety outcome** (e.g., all-cause mortality, adverse events, severe intraventricular hemorrhage).
- **b) Additional (Secondary) Outcomes:**
  - List all planned secondary outcomes using standardized CTM conditional phrasing:  
    > *"If enough data will be eligible, we will analyze the following secondary outcomes: [List outcomes]..."*  
    > *Or:* *"Secondary outcomes will be included if three publications reporting on them can be found."*

---

### Section 9: Planned Data Synthesis

- **a) Is Formal Data Synthesis Planned?**
  - Select: `🔘 Formal synthesis is planned`
- **b) How Will Data Be Combined?**
  - Standard CTM phrasing (derived from CTM Statistical Template):  
    *"Random-effects meta-analyses will be performed using the inverse-variance method for continuous variables and the Mantel-Haenszel method (or restricted maximum likelihood / Paule-Mandel) for dichotomous outcomes. Statistical heterogeneity will be assessed using the I² statistic, τ², and Cochran's Q test. For studies reporting multiple timepoints or correlated subgroups, multilevel random-effects modeling (Robust Variance Estimation — RVE) will be applied. Subgroup and sensitivity analyses will be conducted if at least three studies are available per stratum. Statistical analyses will be conducted in R using the 'meta' and 'metafor' packages."*
  - If the project involves complex biostatistics, consult the CTM biostatistics team.

---

### Section 10: Current Review Stage (CTM Critical Gate)

- **a) Stage of Review at Submission:**
  - > [!CAUTION]
    > **THE "NOT STARTED" MANDATE:** Initial PROSPERO registrations are strictly prohibited once data extraction has begun. To comply with NIHR prospective standards and avoid immediate audit rejection, the status grid must be completed EXACTLY as follows:

| Review Activity Stage | Required Selection |
|---|:---:|
| **Pilot work (pilot searching, testing forms, etc.)** | `🔘 Completed` |
| **Formal searching / study identification** | `🔘 Not started` |
| **Screening search results against inclusion criteria** | `🔘 Not started` |
| **Data extraction or receipt of IPD** | `🔘 Not started` |
| **Risk of bias / quality assessment** | `🔘 Not started` |
| **Data synthesis** | `🔘 Not started` |

- **b) Current Review Status:**
  - Select: `🔘 The review is planned or ongoing`
- **c) Publication of Review Results:**
  - Select: `🔘 We plan to publish the results of this review`
  - In the language box, enter: `English`.

---

### Section 11: Review Affiliation, Funding, and Peer Review

- **a) Review Team Members:**
  - The first author remains the named contact and review guarantor.
  - Click `"Add a team member"`, click the edit icon, and complete full details (name, email, affiliation, ORCID) for all team members, supervisors, and methodologists.
- **b) Review Affiliation:**
  - Enter verbatim:  
    `Centre for Translational Medicine, Semmelweis University, Budapest, Hungary`
- **c) Funding Source:**
  - Select: `🔘 Review has no specific/external funding but is supported by guarantor/review team (non-commercial) institutions.`  
  *(If supported by a specific grant such as OTKA or TKP, specify grant code and funding body).*
- **d) Peer Review:**
  - Select: `🔘 Not peer-reviewed`

---

### Section 12: Additional Information

- **a) Additional Information:** Leave blank or include project notes.
- **b) Review Conflict of Interest:**
  - Select: `🔘 No other potential conflicts of interest to declare for this review`
- **c) Medical Subject Headings (MeSH):**
  - Click **`"MeSH on demand..."`**. Review the automatically suggested terms, save relevant headings, and add supplementary MeSH keywords manually.

---

## 7. Autonomous Agent Directives

When operating within the GP3 pipeline, agents must enforce the following behaviors:

1. **`research-sage`:**
   - Enforce the 1 Safety + 1 Efficacy outcome rule in Section 8.
   - Formulate Section 1 Title according to the canonical formula: `"Investigating the effect of [E] on [O] in [P]: A Systematic Review and Meta-Analysis"`.
2. **`lit-reviewer`:**
   - Compile the 3-domain search key PDF required for Section 6f upload.
   - Verify PROSPERO duplication (Section 3) before finalizing Phase 2.
3. **`feasibility-judge`:**
   - Enforce the Timing Gate: Data extraction cannot begin until the PROSPERO protocol is submitted and timestamped.
   - Enforce the Section 10 "Not started" mandate.
4. **`documentation-writer`:**
   - Pre-populate [`PROSPERO_REGISTRATION_TEMPLATE.md`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/templates/PROSPERO_REGISTRATION_TEMPLATE.md) during Phase 5 protocol assembly.

---

## 8. Summary of Rejection Traps & Pre-Flight Checklist

Before sending the draft to your SMS for submission approval, verify each item:

- [ ] Account password shared with your SMS.
- [ ] Marked `"This record is NOT being created as part of a student project..."` (Screen 4).
- [ ] Review type marked `"Intervention review"` (Screen 5).
- [ ] Title includes `"Systematic review and Meta-analysis"`.
- [ ] Country set to `Hungary`.
- [ ] Similar records searched on PROSPERO; distinct rationale documented if overlaps exist.
- [ ] Timeline set to academic year (`YYYY/09/01` to `YYYY+1/08/31`).
- [ ] Full protocol marked `"A full protocol has not been written"`.
- [ ] Core databases: PubMed, Embase, and CENTRAL all checked.
- [ ] Standalone search strategy PDF generated and uploaded.
- [ ] Dual independent screening and extraction specified.
- [ ] Outcomes include at least **one safety** and **one efficacy** endpoint.
- [ ] Secondary outcomes use CTM conditional phrasing (`"If enough data will be eligible..."`).
- [ ] Review stage: **ONLY "Pilot work" is "Completed"**; all 5 subsequent stages are `"Not started"`.
- [ ] Affiliation set to `"Centre for Translational Medicine, Semmelweis University, Budapest, Hungary"`.
- [ ] **SMS formal signoff obtained before clicking submit.**
