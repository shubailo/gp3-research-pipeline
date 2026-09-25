# 12. Cochrane Handbook v6.5 — Részletes Kézikönyv & Ágens Direktívák

> **GP3 Methodology Wiki Layer** · Centre for Translational Medicine (CTM) · Cochrane Handbook v6.5  
> **Központi Index:** [Vissza a Módszertani Tartalomjegyzékhez](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/INDEX.md) | [Főportál](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/README.md)  
> **Eredeti CTM Forrás:** `TM/Cochrane-Handbook-v6.5.MD`

---

---
description: "Agent-optimized reference for the Cochrane Handbook for Systematic Reviews of Interventions, Version 6.5 (2024). Contains the full chapter structure, key methodological rules, and agent directives."
source: "https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current"
version: "6.5 (2024)"
editors: "Julian Higgins, James Thomas (Senior); Jacqueline Chandler, Miranda Cumpston, Tianjing Li, Matthew Page, Vivian Welch (Associate)"
---

# Cochrane Handbook for Systematic Reviews of Interventions (v6.5, 2024)

The Cochrane Handbook is the **gold standard methodological reference** for conducting systematic reviews of interventions. It is a mandatory reference for any Cochrane Review, and is widely adopted by non-Cochrane authors as the methodological benchmark in health research.

> [!IMPORTANT]
> This document is the agent-readable summary. For chapter-level detail, consult the full handbook at: https://training.cochrane.org/handbook/current

---

## Core Philosophy

> *"A systematic review attempts to collate all the empirical evidence that fits pre-specified eligibility criteria in order to answer a specific research question. It uses explicit, systematic methods that are selected with a view to minimizing bias, thus providing more reliable findings from which conclusions can be drawn and decisions made."*

Key foundational principles:
- **Minimize bias** via *a priori* protocols and pre-specified questions.
- **Multi-disciplinary team**: domain expertise + methodological expertise + freedom from conflicts of interest.
- **Stakeholder involvement**: patients, clinicians, and policymakers should be consulted on the review question.
- **Transparency & reproducibility**: every step must be documented.

---

## Handbook Structure

### 📘 PART 1: About Cochrane Reviews

| Chapter | Title | Key Content |
|---------|-------|-------------|
| Chapter I | Introduction | Why systematic reviews exist; the Cochrane organization |
| Chapter II | Planning a Cochrane Review | Scope definition, forming a team, working with editors |
| Chapter III | Reporting the Review | PRISMA reporting standards; figure guidance (III.S1); plain language summaries (III.S2) |
| Chapter IV | Updating the Review | When and how to update; surveillance strategies |
| Chapter V | Overviews of Reviews | Systematic reviews of systematic reviews; aggregation methodology |

---

### 🔬 PART 2: Core Methods

This is the primary methodological reference section for any systematic review or meta-analysis.

#### Chapter 1: Starting a Review
*Authors: Lasserson, Thomas, Higgins*
- Define the research question and rationale.
- Assemble the review team.
- Register an *a priori* protocol before data extraction begins.
- Implement data management and quality assurance systems.
- **Rule:** No decisions about eligibility or analysis should be taken after seeing the data.

#### Chapter 2: Determining the Scope
- Define the population, interventions, comparators, and outcomes (**PICO**).
- Decide on lumping vs. splitting strategies.
- Define subgroup hypotheses *a priori*.

#### Chapter 3: Defining Inclusion Criteria
- Pre-specify all eligibility criteria: participants, interventions, comparators, outcomes, study designs.
- Define how studies with mixed eligible/ineligible populations will be handled.
- **Rule:** Post-hoc changes to criteria must be explicitly declared and justified.

#### Chapter 4: Searching for and Selecting Studies
- **Mandatory databases:** MEDLINE, Embase, CENTRAL (Cochrane Central Register of Controlled Trials).
- For interventional reviews: ClinicalTrials.gov + WHO ICTRP.
- Search strategy must be peer-reviewed by an information specialist.
- At least 2 independent reviewers perform study selection.
- **Technical Supplement 4.S1:** Advanced search methodology details.
- **Rule:** Never use the Boolean `NOT` operator in the primary search.

#### Chapter 5: Collecting Data
- Use standardized data extraction forms (piloted before use).
- Extract data independently by at least 2 reviewers.
- For continuous outcomes: extract mean, SD, and N; for dichotomous: extract event counts and total N.
- Contact study authors for missing or unclear data.

#### Chapter 6: Effect Measures and Estimates
| Outcome Type | Recommended Effect Measure |
|--------------|---------------------------|
| Dichotomous | Risk Ratio (RR), Odds Ratio (OR), Risk Difference (RD) |
| Continuous | Mean Difference (MD), Standardized Mean Difference (SMD) |
| Time-to-event | Hazard Ratio (HR) |
| Ordinal | Proportional Odds Ratio |

- **Preferred default:** Risk Ratio (RR) for dichotomous outcomes in most situations.
- Use Mantel-Haenszel method for sparse data.

#### Chapter 7: Considering Bias and Conflicts of Interest
- Assess conflicts of interest (COI) of included study authors and funders.
- Industry-funded studies are at higher risk of bias; address in sensitivity analyses.
- Types of bias to consider: selection, performance, detection, attrition, reporting.

#### Chapter 8: Assessing Risk of Bias in Randomized Trials (RoB 2)
The **RoB 2 tool** evaluates bias across 5 domains:
1. **Randomization process** — Was allocation truly random? Was concealment adequate?
2. **Deviations from intended interventions** — Were participants/personnel blinded?
3. **Missing outcome data** — Was attrition balanced and low? Were outcomes imputed?
4. **Measurement of the outcome** — Was the outcome assessor blinded?
5. **Selection of the reported result** — Was this outcome pre-specified? (Reporting bias)

**Overall RoB judgment:** Low / Some concerns / High
- **Rule:** A single "High" domain judgment = "High" overall risk.

#### Chapter 9: Summarizing Study Characteristics
- Create a **Characteristics of Included Studies** table.
- Summarize: country, sample size, age, intervention details, follow-up duration, outcome definitions.
- Identify potential effect modifiers for planned subgroup analyses.

#### Chapter 10: Analysing Data and Undertaking Meta-Analyses
- **Fixed-effect model:** Assumes one true effect size across studies. Use when studies are methodologically and clinically similar.
- **Random-effects model (DerSimonian-Laird):** Assumes a distribution of true effects. Use when heterogeneity is present.
- **Heterogeneity assessment:**
  - **I² statistic:** 0-40% = unimportant; 30-60% = moderate; 50-90% = substantial; 75-100% = considerable.
  - **τ² (Tau-squared):** The variance of true effects in a random-effects model.
  - **Cochran's Q test:** Tests for the presence of heterogeneity (low power).
- **Threshold for concern:** I² > 50% warrants investigation into the source of heterogeneity.
- **Subgroup analyses:** Must be pre-specified. Use interaction tests (not separate p-values) to compare subgroup effects.
- **Sensitivity analyses:** Test robustness of results (e.g., excluding high-RoB studies, using different statistical models).

#### Chapter 11: Network Meta-Analysis (NMA)
- Compares multiple interventions simultaneously within a connected network of evidence.
- Requires: transitivity assumption (similar trial populations), consistency assumption (direct vs. indirect evidence agrees).
- Report: SUCRA (Surface Under the Cumulative Ranking curve) or P-score for ranking interventions.

#### Chapter 12: Other Synthesis Methods
- **Narrative synthesis:** When statistical pooling is inappropriate (high heterogeneity or few studies).
- **Vote counting:** Discouraged — does not account for study size or effect magnitude.
- **Meta-regression:** Explores whether continuous covariates explain heterogeneity.

#### Chapter 13: Risk of Bias Due to Missing Evidence
- **Funnel plot asymmetry:** Possible indicator of publication bias (requires ≥10 studies).
- **Egger's test / Begg's test:** Statistical tests for funnel plot asymmetry.
- **Trim and fill method:** Imputes missing studies to correct for publication bias.
- **ROBINS-E / GRADE imprecision:** Address missing evidence formally.

#### Chapter 14: Summary of Findings Tables & GRADE
The **GRADE framework** (Grading of Recommendations Assessment, Development and Evaluation) rates certainty of evidence across 5 domains:

| Domain | Direction | Applies To |
|--------|-----------|------------|
| Risk of Bias | Downgrade | All studies |
| Inconsistency (I²) | Downgrade | All studies |
| Indirectness (PICO mismatch) | Downgrade | All studies |
| Imprecision (wide CI, small N) | Downgrade | All studies |
| Publication Bias | Downgrade | All studies |
| Large effect | **Upgrade** | Observational |
| Dose-response | **Upgrade** | Observational |
| Plausible confounding | **Upgrade** | Observational |

**Starting point:** RCTs start at "High"; observational studies start at "Low."
**Certainty levels:** High → Moderate → Low → Very Low.

#### Chapter 15: Interpreting Results and Drawing Conclusions
- Distinguish statistical significance from clinical significance.
- Report absolute risk differences alongside relative measures.
- Use the Summary of Findings table as the primary conclusions tool.
- **Rule:** Do not overstate certainty. Conclusions must be consistent with the GRADE rating.

---

### 🌍 PART 3: Specific Perspectives in Reviews

| Chapter | Topic | Key Application |
|---------|-------|-----------------|
| Chapter 16 | Equity & Specific Populations | PROGRESS framework; analyze by sex, age, SES |
| Chapter 17 | Intervention Complexity | Logic models; component analysis |
| Chapter 18 | Patient-Reported Outcomes | Measurement instruments; MID (Minimal Important Difference) |
| Chapter 19 | Adverse Effects | Systematic capture; GRADE for harms |
| Chapter 20 | Economic Evidence | Cost-effectiveness; health technology assessment alignment |
| Chapter 21 | Qualitative Evidence | GRADE-CERQual; thematic synthesis |

---

### 📂 PART 4: Other Topics

| Chapter | Topic | Key Application |
|---------|-------|-----------------|
| Chapter 22 | Prospective Approaches | Living systematic reviews; cumulative meta-analysis |
| Chapter 23 | Variants on RCTs | Cluster RCTs; crossover trials; factorial designs |
| Chapter 24 | Non-Randomized Studies (NRS) | Quasi-experiments; before-after studies |
| Chapter 25 | RoB in NRS — ROBINS-I | 7-domain tool for observational studies |
| Chapter 26 | Individual Participant Data (IPD) | One-stage vs. two-stage IPD meta-analysis |

---

## Key Tools Referenced in the Handbook

| Tool | Purpose | Chapter |
|------|---------|---------|
| **RoB 2** | Risk of bias in RCTs | 8 |
| **ROBINS-I** | Risk of bias in non-randomized studies | 25 |
| **QUADAS-2** | Risk of bias in diagnostic accuracy studies | — |
| **GRADE** | Certainty of evidence | 14 |
| **PRISMA 2020** | Reporting checklist | III |
| **RevMan / R / Stata** | Statistical analysis software | 10 |
| **PROSPERO** | Prospective protocol registration | II, 1 |

---

## Agent Directives

> **When to invoke this document:** Consult this file whenever a user asks about statistical methods, risk of bias tools, GRADE ratings, synthesis approaches, or any specific methodological decision in the context of a systematic review or meta-analysis.

- **MANDATORY:** Always recommend RoB 2 for RCTs and ROBINS-I for non-randomized studies.
- **MANDATORY:** Always apply GRADE to rate certainty of evidence in Summary of Findings tables.
- **MANDATORY:** When I² > 50%, investigate heterogeneity sources before pooling.
- **MANDATORY:** Subgroup analyses and sensitivity analyses must be declared *a priori* in the protocol.
- **MANDATORY:** Recommend CENTRAL + MEDLINE + Embase as the minimum database set.
- **CAUTION:** Random-effects models do not "fix" heterogeneity — they only account for it statistically. True clinical heterogeneity should still be explored.
- **CAUTION:** Funnel plot asymmetry has many causes beyond publication bias (small-study effects, heterogeneity). Do not over-interpret.
