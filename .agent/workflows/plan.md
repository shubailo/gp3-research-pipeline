---
description: Create project plan using project-planner agent coordinating the 6-agent GP3 medical research team.
---

# /plan - Medical Research Planning Mode

$ARGUMENTS

---

## 🔴 CRITICAL RULES

1. **NO CODE WRITING** - This command creates planning documentation only.
2. **Coordinated 6-Agent Execution** - Must coordinate the specialized research team: `research-sage`, `lit-reviewer`, `feasibility-judge`, `meta-analyzer`, `mentor-hegyi`, `mentor-garami`.
3. **Dynamic Naming** - Output plan file named dynamically based on topic: `docs/PLAN-{topic-slug}.md`.
4. **GP3 Methodological Governance & Wiki Grounding:** Ground all planning strictly in the **GP3 Methodology Wiki** ([`data/wiki/methodology/INDEX.md`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/INDEX.md)) and relevant study dossiers in [`data/wiki/<project>/studies/`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/).

---

## Task

Execute the **6-Agent GP3 Research Planning Workflow**:

```
CONTEXT:
- User Request: $ARGUMENTS
- Mode: RESEARCH PLANNING ONLY (no data collection or script execution)
- Output: docs/PLAN-{topic-slug}.md (dynamic naming)

NAMING RULES:
1. Extract 2-3 key words from the research topic
2. Lowercase, hyphen-separated
3. Max 30 characters
4. Example: "neonatal sepsis biomarkers" → PLAN-sepsis-biomarkers.md

WORKFLOW PHASES (6-Agent Collaboration):

1. **Phase 1: Hypothesis, Suffering Narrative & T1-T4 Stage (`research-sage` + `mentor-hegyi`)**
   - Formulate testable clinical question (PICO / PEO / CoCoPop / PIRD).
   - Enforce mandatory PICO Title Formula: "Investigating the effect of [E/I] on [O] in [P]".
   - Draft the Suffering Narrative: Child suffering (morbidities), Parent suffering (burden), and Clinical Hope.
   - Declare the T1–T4 translational stage and targeted Avoidable Mortality.

2. **Phase 2: Literature Rigor & Search Key Methodology (`lit-reviewer`)**
   - Execute 6-Point Quantitative Background Check (incidence per 1,000, untreated mortality/morbidity %, evidence-based gold standard, epidemiological link with numbers).
   - Construct 3-Step Search Key: 1. Review ≥10 published meta-analyses in domain → 2. AI validation → 3. Domain order (1. Population AND 2. Exposure/Intervention AND 3. Therapy/Context). Forbid 'NOT'.
   - Verify novelty and check PROSPERO for duplicates.
   - **LIVE LITERATURE SEARCH:** Execute `python src/literature_search.py "<QUERY>" --analyze --max-results 100 --years 5` to confirm publication volume, trend, and identify the top poolable primary studies. Include the hit count and 5-year trend in the plan file.

3. **Phase 3: Operational & Statistical Feasibility Gates (`feasibility-judge` + `meta-analyzer`)**
   - Enforce the Feasibility Poolability Rule: Identify at least 3 primary studies reporting THE EXACT SAME primary outcome.
   - Pre-specify Confounder Matrix and mandate QUIPS (prognostic) / RoB 2 (RCTs) / ROBINS-I.
   - Audit missing variables (narrative vs. meta-regression) and warn against ecological bias.
   - Audit physiological mechanisms via the Sensor-Pathway-Effector Triad (Garami rule).
   - For temperature interventions, apply the Thermal Dose (COIN) Standard.
   - Mandate Multilevel Meta-Analysis (RVE) for dependent effect sizes.

4. **Phase 4: The Dialectical Mentor Cross-Debate (`mentor-hegyi` vs. `mentor-garami`)**
   - Round 1: Hegyi clinical critique (Bedside urgency, SAP, 1-10 matrix) vs. Garami mechanistic critique (biological plausibility, measurement noise, 1-10 matrix).
   - Round 2: Dialectical Cross-Talk: Hegyi pushes for translational speed; Garami warns against flawed biophysical measurements.
   - Joint Socratic Gate: Focused questions bridging the clinical-mechanistic divide.

5. **Phase 5: Plan File Compilation**
   - Compile comprehensive plan into docs/PLAN-{slug}.md.
   - End with 2-3 strategic Socratic questions asking the researcher to confirm key parameters before protocol generation.
```

---

## Expected Output

| Deliverable | Location |
|---|---|
| Research Protocol Plan | `docs/PLAN-{topic-slug}.md` |
| PICO Framing, Suffering Narrative & T1-T4 Stage | Inside plan file |
| 6-Point Background & 3-Step Search Key | Inside plan file |
| Feasibility Poolability Table (≥3 studies) | Inside plan file |
| Sensor-Pathway-Effector & Thermal Dose Check | Inside plan file |
| Dialectical Mentor Cross-Debate (Hegyi vs. Garami) | Inside plan file |
| Socratic Questions for Researcher | End of plan file |

---

## After Planning

Prompt the user:
```
[OK] Research Plan created: docs/PLAN-{slug}.md

Next steps:
- Review and answer the Socratic questions at the end of the plan file.
- Once confirmed, run `/research` or generate `PROTOCOL.md` for ethical review or PROSPERO registration.
- Construct and test the systematic search strategy using `src/literature_search.py`.
```

---

## Usage Examples

```
/plan meta-analysis of rapid POC tests for neonatal sepsis
/plan translational study on metabolomics predicting late-onset sepsis
/plan prognostic review of TRPA1 activation in acute inflammatory pain
```
