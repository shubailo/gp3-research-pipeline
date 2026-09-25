# PLAN-hypothermia-lmic: Therapeutic Hypothermia in LMICs Post-HELIX

## Goal Description
This research aims to conduct a systematic review and meta-analysis to evaluate the safety and efficacy of therapeutic hypothermia (TH) for neonatal hypoxic-ischemic encephalopathy (HIE) in Low- and Middle-Income Countries (LMICs), specifically focusing on data emerging after the landmark HELIX trial (2021). The central question is whether improved intensive care standards and better patient selection in recent years have mitigated the mortality risk identified by HELIX.

---

## 4-Agent Workflow Results

### 1. Brainstorm Agent: Hypotheses & Methodology
**Hypotheses:**
- **Primary:** TH in LMIC settings with advanced servo-controlled devices and tertiary NICU support (comparable to HELIX) still shows no mortality benefit but improves long-term neurodevelopment.
- **Secondary:** "Low-tech" cooling (ice packs/phase change materials) without continuous monitoring correlates with higher mortality due to temperature instability.
- **Safety:** TH increases the risk of clinically significant hemorrhage and persistent metabolic acidosis in LMIC settings.

**Proposed Methodology:**
- **Search Strategy:** PubMed, Embase, Cochrane Library, and Google Scholar (2015–2025).
- **Inclusion Criteria:** RCTs and prospective cohort studies in LMICs (World Bank classification) involving neonates ≥35 weeks GA with HIE.
- **Outcomes:** 
    - *Primary:* Mortality (neonatal/at 18 months), Death or severe disability.
    - *Secondary:* Major bleeding (gastric, pulmonary, IVH), Sepsis, Thrombocytopenia, HIE-related seizures.
- **Statistical Plan:** Random-effects meta-analysis (DerSimonian-Laird), $I^2$ for heterogeneity, Egger’s test for publication bias. Subgrouping by cooling method and country income level.

### 2. Litcheck Agent: Novelty Verification
- **Current Landscape:** The 2021 HELIX trial (n=408) revolutionized the field by showing increased mortality (RR 1.35). A 2022 meta-analysis confirmed this trend but showed benefits if HELIX was removed. 
- **Novelty:** A 2024 meta-analysis reported improved neurodevelopment at 6 months+ despite mortality neutral results. However, there is a gap in specifically analyzing the **safety profile** (hemorrhagic complications) across the most recent 2023-2024 cohorts which were not fully captured in the 2021-2022 peaks.
- **Conclusion:** The topic is highly relevant as clinical practice in many LMICs is currently in flux (some centers halted cooling, others refined protocols).

### 3. Feasibility Agent: Resource & Ethical Assessment
- **Data Availability:** High. Multiple registers and smaller trials from Pakistan, Turkey, and Egypt have been published recently.
- **Clinical/Ethical:** Highly feasible. As this is a secondary meta-analysis, no new patient recruitment is needed. The results could directly inform WHO/ILCOR policy updates.
- **Heterogeneity Risk:** High. Mitigation strategy includes strict sensitivity analysis based on the quality of "intensive care support" (e.g., availability of invasive ventilation).

### 4. Socratic Agent: Principal Investigator Review (Questions for User)
Before finalizing the protocol, please clarify the following:
1. **PICO Refinement:** Should we strictly exclude studies using "low-tech" cooling (ice packs without servo-control) to focus on whether TH itself is the problem, or should we include them to capture the "real-world" LMIC scenario?
2. **Outcome Priority:** Given that recent reviews (2024) show neurodevelopmental benefit but mortality risk remains the "stumbling block," should our primary outcome be **"Survival without severe disability"** (composite) or should we keep **Mortality** as a standalone primary to address the HELIX safety concerns directly?
3. **Sub-classification:** Do you wish to differentiate between "Traditional LMICs" (South Asia/Africa) and "Emerging Middle Income" (e.g., Turkey/Brazil) where NICU standards might be closer to HICs?

---

## Verification Plan
### Automated Tests
- [ ] Run `scripts/verify_search_string.py` to ensure the PubMed API returns >10 unique post-2021 results (once implemented).
- [ ] Validate the PICO consistency using a Python-based keyword extraction script against the drafted Inclusion/Exclusion criteria.

### Manual Verification
- Review this PLAN file for alignment with the HELIX trial's methodology (to ensure direct comparability).
