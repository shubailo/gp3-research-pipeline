# PLAN: Lab-Parameter Hub in Neonatal Thermoregulation

## 1. Goal and Research Question
The primary objective of this investigation is to establish a quantitative, evidenced-based model of the **"Lab-Parameter Hub"** in neonates. This hub represents the intersection where routine NICU laboratory markers (metabolic, inflammatory, and endocrine) modulate or predict thermoregulatory outcomes, specifically non-shivering thermogenesis (NST) and core temperature stability.

### Clinical Question (PICO)
**To what extent do routine NICU laboratory parameters correlate with body temperature stability and brown adipose tissue (BAT) activity in preterm and term neonates?**

- **P (Population):** Neonates (Preterm GA <37 and Term) in the **first 72 hours of life**.
- **I/E (Exposure):** Physiological or pathological levels of routine biomarkers:
    - **Bilirubin** (Total and Unconjugated)
    - **CRP** (as a proxy for inflammatory load)
    - **Lactate & Glucose** (Metabolic fuels/markers)
    - **TSH & free T4** (Endocrine thermogenic drivers)
- **C (Comparison):** Intra-individual stability or comparison across levels of clinical markers.
- **O (Outcome):** 
    - **Primary:** Body temperature fluctuations, incidence of hypothermia/hyperthermia.
    - **Secondary:** BAT temperature (via IRT), UCP1 expression (if available in select studies), clinical length of stay.

---

## 2. Methodology (4-Agent Planning Workflow)

### 🧪 Agent 1: Brainstorm (Hypotheses & Design)
**Study Design:** A hybrid approach consisting of a **Systematic Review & Meta-analysis** of existing clinical data (RCTs + Observational) followed by a **Retrospective Registry Analysis** of the PTE NICU database.

**Brainstormed Hypotheses:**
1.  **The Bilirubin-BAT Stimulus:** Bilirubin acts as a non-toxic signaling molecule at physiological levels to stimulate BAT mitochondrial proton leak, aiding neonatal adaptation.
2.  **The Inflammatory Thermogenic Cost:** Elevated CRP levels are inversely correlated with thermoregulatory efficiency due to the metabolic diversion of shifting resources to the immune response.
3.  **Endocrine Fragility:** Low fT4 levels directly predict poor BAT recruitment and higher sensitivity to environmental cold stress in very low birth weight (VLBW) infants.

---

### 📚 Agent 2: Litcheck (Literature Verification)
- **Search Strategy:** Strategy 1 (Broad Hub) yielded **1,314** results; Strategy 2 (BAT-refined) yielded **112** results.
- **RCT Pool:** A high-quality subset of **66 human RCTs** (specifically focusing on cooling, phototherapy, and metabolic adaptation) provides the causal evidence base.
- **Observational Pool:** **1,200+ studies** provide the "Big Data" necessary for correlation modeling.
- **Novelty:** No existing meta-analysis has integrated these disparate markers into a single "Hub" model. This research fills a critical gap in **Precision Neonatology**.

---

### 📈 Agent 3: Feasibility (Clinical & Resource)
- **Data Access:** High feasibility. Routine labs and temperature records are standard of care and digitally archived in most NICUs.
- **Statistical Power:** With 1,300+ potential studies, we have sufficient power for meta-regression to account for Gestational Age (GA) and Birth Weight (BW).
- **Ethics:** Retrospective meta-analysis is low-risk; retrospective database study requires institutional IRB approval (already indicated as possible).
- **Translational Alignment:** Perfectly fits the Hegyi model by identifying a "Knowledge Gap" in routine data that can lead to clinical "Predictive Monitoring".

---

### 🧐 Agent 4: Socratic (Decisions Reached)

1.  **Inclusion Window:** Limited to the **first 72 hours of life**, capturing the peak of thermogenic adaptation and bilirubin rise.
2.  **Outcome Standardization:** We will **collect raw data from all sites** (rectal, axillary, skin) first, then evaluate heterogeneity to decide on subgrouping or standardization factors.
3.  **Antibiotic Subgroup:** A dedicated subgroup analysis will compare infants receiving **antibiotics (Amp+Gent)** vs. those who do not, directly testing the thesis hypothesis.

---

## After Planning

[OK] Plan created: docs/PLAN-lab-parameter-hub.md

Next steps:
- Review the plan and answer the Socratic questions.
- Run `/create` to start the PRISMA search or database analysis shell.
