---
name: meta-analysis-brainstorming
description: Skill for brainstorming, designing, and validating systematic reviews and meta-analysis ideas.
---

# Meta-Analysis Brainstorming & Design Guidelines

This skill consolidates the core methodological rules from the Translational Medicine (TM) course. Use this file as your primary framework when brainstorming meta-analysis topics with the user.

## 1. Idea Generation & Validation (The FINER Framework)
When proposing a meta-analysis idea, validate it against the FINER criteria:
- **Feasible:** Are there enough primary studies available? (Avoid empty reviews). Can we access the data?
- **Interesting:** Does the topic appeal to the medical community, practitioners, and patients?
- **Novel:** Has this exact question been answered recently? (Must check PROSPERO for duplicates).
- **Ethical:** Does the research align with medical ethics?
- **Relevant:** Does it solve a real-world clinical problem and improve healthcare delivery?

## 2. Framing the Question
Identify the type of systematic review the user wants to conduct and apply the mandatory framework:
- **Interventional:** Use **PICO** (Patients, Intervention, Comparator, Outcome).
- **Prevalence/Incidence:** Use **CoCoPop** (Condition, Context, Population).
- **Diagnostic Accuracy:** Use **PIRD** (Patients, Index Test, Reference standard, Diagnosis).
- **Prognostic/Etiology:** Use **PEO** (Population, Exposure, Outcome).

## 3. Scoping & Heterogeneity
- Clearly define if the scope is **Narrow** (highly specific PICO) or **Broad** (highly generalizable).
- Define how heterogeneity will be handled: **Lumping** (combining diverse studies) vs. **Splitting** (analyzing subgroups separately).

## 4. Preliminary Search Protocol
Do NOT skip the preliminary search phase when brainstorming:
1. Search **PROSPERO** to ensure no ongoing review covers the same topic.
2. Construct a basic search string using the PICO elements (connected with `AND`).
3. Locate **3-5 key articles** that exactly match the criteria. If found, the idea is feasible.

## 5. Agent Workflow Rules
- **MANDATORY:** Never start a meta-analysis project without a pre-registered protocol.
- **MANDATORY:** Warn against publication/reporting bias; all planned outcomes must be reported regardless of significance.
- **MANDATORY:** Emphasize that the study design of the included articles dictates the level of evidence (e.g., an MA of RCTs is the gold standard).
- **MANDATORY:** Exclude gray literature (unless pre-specified) and explicitly forbid the use of the `NOT` Boolean operator in the primary search strategy.

## 6. Risk of Bias Assessment
This is a **non-negotiable step** that must occur after study selection and before synthesis.
- **For RCTs:** Use the **RoB 2** tool (Cochrane Risk of Bias tool, version 2). Domains: randomization, allocation concealment, blinding, missing outcome data, reporting bias.
- **For non-randomized (interventional) studies:** Use **ROBINS-I**.
- **For prognostic observational studies:** Use **QUIPS (Quality in Prognosis Studies)** paired with a strict Confounder Matrix (prespecify what must be adjusted for).
- **For diagnostic studies:** Use **QUADAS-2**.
- **For pure prevalence studies:** Use **NOS** (Newcastle-Ottawa Scale) or **JBI critical appraisal tools**.
- **Output:** Produce a traffic-light RoB summary table (low / some concerns / high) for all included studies.
- **MANDATORY:** Studies with critical or high overall RoB should be flagged for sensitivity analysis, not automatically excluded.

> **Note:** For specific detailed rules on study selection, database search strategies, or inclusion criteria, refer to the individual markdown files in the `TM` directory. For the full statistical and methodological framework (GRADE, RoB 2, ROBINS-I, heterogeneity, NMA), consult `TM/Cochrane-Handbook-v6.5.MD`.

## 7. Critical Feasibility & Methodological Pitfalls
To avoid fatal flaws during the design phase, rigorously check against these common pitfalls:
- **Causal Overreach:** NEVER design a meta-analysis asserting causality (interventional claims) from observational data. Frame it strictly as a "prognostic association" review.
- **Missing Variable Feasibility:** If the proposed meta-regression relies on variables that are rarely reported in primary literature (e.g., specific drug dosages, granular treatment strategies), force the protocol to use a **narrative synthesis** for those variables instead of quantitative meta-regression.
- **Ecological Bias:** Warn against regressing patient-level outcomes on study-level averages (e.g., using mean cohort temperature to predict individual morbidity).
- **Dependent Data (Multilevel Analysis):** If primary studies report multiple dependent effect sizes (e.g., outcomes at multiple glucose thresholds from the same cohort), mandate the use of **Multilevel Meta-Analysis (Robust Variance Estimation - RVE)** to prevent unit-of-analysis errors.
