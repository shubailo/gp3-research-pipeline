---
description: Initialize a new research project. Launches interactive Socratic wizard, creates PROJECT.md entry, PLAN skeleton, PROSPERO draft, and folder structure. Run this before any other command for a brand-new research idea.
---

# /new-project — Research Project Initialization Wizard

$ARGUMENTS

---

## 🔴 CRITICAL RULES

1. **Read `PROJECT.md` first** — check if this project already exists before creating a duplicate entry.
2. **Complete all 5 wizard steps** before writing any files. Do NOT skip steps.
3. **Activate `mentor-hegyi` and `mentor-garami`** to evaluate the initial idea at the end of the wizard.
4. **Do NOT start a literature search** during this wizard — that is Phase 2 (/plan or /research).

---

## Purpose

This command bootstraps a new medical research project from scratch. It asks structured questions to capture the critical design decisions **on Day 1**, before anyone forgets the original intent, preventing the most common failure mode: a protocol that diverges from the original research question.

**What it creates:**
- An entry in `PROJECT.md` (persistent memory)
- `docs/PLAN-{slug}.md` (planning skeleton)
- `docs/PROSPERO-draft-{slug}.md` (pre-filled with 22 mandatory PROSPERO fields)
- `results/{slug}/` directory (for future search outputs)

---

## 🧙 The 5-Step Wizard

Execute ALL steps sequentially. Do NOT skip or merge steps.

### STEP 1: The Clinical Problem & Research Question

Ask the researcher (or use `$ARGUMENTS` if provided):

```
"What is the single clinical problem you want to solve?
Be as specific as possible — patient population, the gap in knowledge, and why it matters now."
```

From the answer, extract:
- Target **population** (age group, condition, clinical setting)
- **Knowledge gap** (what is unknown or contested)
- **Clinical urgency** (why this matters for patient outcomes)

Apply `mentor-hegyi` SAP Rule:
> *"Formulate this into ONE Single Attackable Problem sentence. If you cannot do it in one sentence, the question is too broad."*

### STEP 2: Study Design & PICO Classification

Classify the study type:
- **Systematic Review / Meta-analysis** → PICO / PEO / CoCoPop / PIRD
- **Clinical Trial** → PICO
- **Observational / Prognostic** → PEO
- **Basic Science** → Mechanistic hypothesis + Sensor-Pathway-Effector triad

Ask:
```
"What study design fits this question?
- Do you have enough primary studies for a meta-analysis? (~3+ with identical outcomes)
- Or is this a new clinical or basic science study?"
```

Generate the PICO table and derive the **mandatory PICO Title Formula:**
> *"Investigating the effect of [Exposure/Intervention] on [Outcome] in [Population]"*

### STEP 3: Suffering Narrative (Mandatory — Mentor Hegyi Rule)

Ask the researcher to answer all 3:
```
1. Patient Suffering: What specific morbidities occur? (cognitive, motor, sensory, organ failure)
   — Give numbers: "X% develop Y condition"
2. Family Burden: How does the family suffer? (emotional, financial, caregiving)
3. Clinical Hope: If this question is answered, what changes? How many patients benefit?
```

Do NOT proceed to Step 4 without all 3 answers.

### STEP 4: Biological Mechanism (Garami Pre-Check)

Apply the Sensor-Pathway-Effector Triad:
```
"Before we proceed, let's confirm biological plausibility:
1. What is the molecular sensor/receptor activated? (e.g., TRPV1, TLR4, GLP-1R)
2. What is the transmission pathway? (neural, hormonal, cellular cascade)
3. What is the effector organ/response? (thermogenesis, cytokine release, glucose uptake)"
```

If the researcher cannot answer all 3: flag as **MECHANISTIC GAP** and suggest consulting a physiology reference before proceeding.

### STEP 5: Resources & Constraints

Ask:
```
1. Which databases do you have access to? (PubMed, EMBASE, Cochrane, local hospital registry)
2. What is the target journal or submission deadline?
3. Do you have a co-reviewer available? (2-reviewer screening is mandatory for PRISMA)
4. IRB/Ethics committee approval needed? (if prospective data collection)
```

---

## Output: Files to Create

After completing all 5 wizard steps:

### 1. Update `PROJECT.md`

Add a new project block under `## 📁 Active Projects` using this template:

```markdown
### Project: [Title from PICO Formula]

\`\`\`
Status: 🟡 ACTIVE — Phase 1 (Initialized)
PROSPERO: ⚠️  NOT YET REGISTERED — Draft at docs/PROSPERO-draft-{slug}.md
Last Updated: [TODAY'S DATE]
\`\`\`

**PICO:**
- **P:** [Population]
- **I:** [Intervention/Exposure]
- **C:** [Comparator]
- **O:** [Outcome]
- **Title:** *"[Full PICO Title Formula]"*

**T-Stage:** [T0/T1/T2/T3/T4] — [Brief justification]

**Suffering Narrative:**
- *Patient:* [Answer from Step 3.1]
- *Family:* [Answer from Step 3.2]
- *Clinical Hope:* [Answer from Step 3.3]

**Sensor-Pathway-Effector:**
- *Sensor:* [Answer from Step 4.1]
- *Pathway:* [Answer from Step 4.2]
- *Effector:* [Answer from Step 4.3]

**Resources:** [Databases, co-reviewer, deadline]

**Open Socratic Questions (Blocking):**
1. [Auto-generated from wizard gaps]

**Next Step:** Run `/plan [PICO Title]` to initiate full 6-agent pipeline
```

### 2. Create `docs/PROSPERO-draft-{slug}.md`

Pre-fill all 22 mandatory PROSPERO fields from the wizard answers. Use the template at `.agent/skills/brainstorming/PROSPERO_TEMPLATE.md` if available, or generate inline using the PROSPERO 2025 field list:

```markdown
# PROSPERO Draft: {PICO Title}
> ⚠️ DRAFT — NOT YET SUBMITTED. Register at: https://www.crd.york.ac.uk/prospero/

## 1. Review title
{PICO Title Formula}

## 2. Anticipated or actual start date
{TODAY}

## 3. Anticipated completion date
{TODAY + 12 months, or researcher-specified}

## 4. Registration stage
Protocol (pre-registration)

## 5. Named contact
[Lead researcher name — to be filled]

## 6. Named contact email
[To be filled]

## 7. Organisational affiliation
[Institution — to be filled]

## 8. Review team members
[To be filled — include all co-authors who will approve registration]

## 9. Funding sources
[To be filled]

## 10. Conflicts of interest
None declared / [To be filled]

## 11. Condition or domain
{Extracted from PICO — Population's condition}

## 12. Rationale
{Suffering Narrative: Patient + Family + Clinical Hope}

## 13. Objectives
Primary: {PICO Title Formula}
Secondary: [To be defined in /plan phase]

## 14. Eligibility criteria

### Population (P)
Included: {P from PICO}
Excluded: [To be defined]

### Intervention / Exposure (I/E)
{I/E from PICO}

### Comparator (C)
{C from PICO}

### Outcomes (O)
Primary: {O from PICO}
Secondary: [To be defined]

### Study types
[Specify: RCTs only / Observational / Both]

## 15. Information sources
PubMed, EMBASE (via Ovid), Cochrane Central Register of Controlled Trials (CENTRAL)
[Add others based on researcher's access]

## 16. Main outcome(s)
{Primary outcome with measurement tool and timepoint}

## 17. Additional outcomes
[To be defined]

## 18. Data extraction (selection and coding)
Two independent reviewers will screen titles/abstracts and full texts.
Conflicts resolved by consensus or third reviewer.
Data extraction form: [To be developed]

## 19. Risk of bias (quality) assessment
[RoB 2 / ROBINS-I / QUIPS / QUADAS-2 — specify based on study design]

## 20. Strategy for data synthesis
Random-effects meta-analysis (DerSimonian-Laird or REML).
Heterogeneity assessed via I² and τ².
GRADE Summary of Findings Table will be produced.

## 21. Analysis of subgroups or subsets
[To be pre-specified in /plan phase]

## 22. Language
English [add others if applicable]

---
> **Next step:** Complete fields marked [To be filled], then submit at PROSPERO.
> Run `python src/validate_protocol.py docs/PROSPERO-draft-{slug}.md` before submission.
```

### 3. Create `results/{slug}/` directory

```bash
mkdir -p results/{slug}
```

### 4. Mentor Initial Verdict

After all files are created, provide initial mentor assessments:

**Prof. Hegyi's first impression (1-10 matrix, brief):**
- *Utility*: [X], *Feasibility*: [X], *Novelty*: [X], *Problem Solving*: [X]
- Key concern or encouragement in his voice

**Dr. Garami's mechanistic pre-check:**
- *Mechanistic Plausibility*: [X], *Measurement Quality*: [X]
- Flag any measurement standardisation concerns

---

## Completion Message

```
✅ New Project Initialized: {PICO Title}

Files created:
  📄 PROJECT.md — updated with project state
  📄 docs/PROSPERO-draft-{slug}.md — 22 PROSPERO fields pre-filled
  📁 results/{slug}/ — search output directory

Next steps (in order):
  1. Complete the [To be filled] fields in PROSPERO-draft-{slug}.md
  2. Run /plan {PICO Title} to generate the full 6-agent research plan
  3. Once plan is confirmed, register on PROSPERO before data collection begins
  4. Run /research {PICO Title} for full 5-phase protocol generation
```

---

## Usage Examples

```
/new-project
/new-project meta-analysis of fever management in sepsis
/new-project translational study on TRPM8 in neuropathic pain
/new-project systematic review of probiotics in neonatal NEC
```
