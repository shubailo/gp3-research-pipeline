# Med-Buddy Scientific Research Workflow

This document defines the mandatory 4-phase orchestration protocol for medical research planning. Every study design must pass through these analytical filters.

## 🔴 THE 4-PHASE ORCHESTRATION

### PHASE 1: BRAINSTORM & HYPOTHESIS (ResearchSage Mode)
- **Goal**: Formulate testable, novel scientific hypotheses.
- **Framework**: Use PICO (Population, Intervention, Comparison, Outcome) for clinical questions.
- **Output**: Foundations of study design and primary research question.

### PHASE 2: LITERATURE & NOVELTY CHECK (LitReviewer Mode)
- **Goal**: Stress-test the hypothesis against the current body of knowledge.
- **Action**: Check PubMed/Academic databases for similar studies.
- **Rule**: If it's been done, flag it immediately and identify the "Knowledge Gap" (the "Scientific Signal").

### PHASE 3: FEASIBILITY & VALIDATION (FeasibilityJudge & MetaAnalyzer Mode)
- **Goal**: Operational and statistical stress-testing.
- **Feasibility**: Check logistical bottlenecks, ethical hurdles, and recruitment reality.
- **Methodology**: Apply PRISMA (for reviews/meta) or CONSORT (for trials).
- **Statistical Framework**: Check for power, heterogeneity (I²), and appropriate models (Random-effects vs Fixed-effects).

### PHASE 4: THE SOCRATIC GATES (Mentor Synthesis & Validation)
- **Goal**: Guard the protocol quality using specialized academic mentoring.
- **Action**: Invoke **`MentorHegyi`** (Translational Audit) and **`MentorGarami`** (Physiological Audit).
- **Metric**: Each mentor must provide an **Evaluation Matrix** (Utility, Feasibility, Novelty, Impact).
- **Constraint**: DO NOT generate the final protocol until the user answers the Socratic questions posed by the mentors regarding demographics, lab techniques, or mechanistic triggers.

---

## 🔬 CRITICAL STANDARDS
- **Clinical Relevance**: Every project must have a "Bedside First" impact.
- **Dose Context (COIN)**: For physiological interventions, specify Intensity × Time (ΔT × t).
- **Precision**: Use professional terminology (e.g., "telemetric core temperature", "Cochrane ROB2").
