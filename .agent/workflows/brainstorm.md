---
description: Structured brainstorming for research idea generation in basic/translational medicine and meta-analysis. Explores multiple novel topic ideas before protocol development.
---

# /brainstorm - Structured Research Idea Exploration

$ARGUMENTS

---

## 🔴 CRITICAL RULES

1. **Meta-Analysis Guidance:** If the user's request involves a meta-analysis or systematic review, you MUST read and apply the guidelines in `TM/META_ANALYSIS_BRAINSTORMING_SKILL.md`. Refer to other markdown files in the `TM/` folder if specific methodological details (like PICO, search strategies, inclusion criteria) are needed.

---

## Purpose

This command activates BRAINSTORM mode for structured research idea exploration tailored to medical researchers (basic science, translational medicine, or meta-analysis). Use when you need to generate and evaluate novel research topics before committing to a full study protocol, data collection, or systematic review search strategy.

---

## Behavior

When `/brainstorm` is triggered:

1. **Understand the clinical/scientific goal**
   - What is the clinical problem or knowledge gap we are addressing?
   - What is the target population/model (e.g., PICO framework, in vitro models)?
   - What are the available resources (datasets, lab capabilities, clinical cohorts)?

2. **Pre-screen and Validate Novelty + Feasibility via Literature Search**
   - Brainstorm initial topic concepts internally.
   - **MANDATORY:** Search PubMed and academic sources (using `search_web` or the `pubmed-database` science plugin, or by instructing use of `python src/literature_search.py "<QUERY>" --max-results 50`) to verify if the study has already been done.
   - Discard or refine ideas that are heavily covered in existing literature. Ensure the proposed study fills a verified knowledge gap.
   - **MANDATORY POOLABILITY PRE-CHECK (GP3 Rule):** For any meta-analysis or systematic review idea, verify that at least 3 primary studies exist reporting the exact same primary outcome before recommending the idea. If fewer than 3 poolable primary studies are identified, flag the idea as **POOLABILITY RISK: LOW** and either recommend expanding the PICO or suggest an alternative study design (e.g., scoping review, individual cohort study). Do NOT recommend a meta-analysis topic that will fail the Phase 3 Poolability Gate.
   - **PROSPERO Duplicate Check:** Confirm no ongoing identical review exists on PROSPERO (prospero.york.ac.uk) before presenting an idea as novel.

3. **Present validated research options**
   - Provide **3-5 distinct, literature-validated research topic ideas**
   - Provide a mix of study types (e.g., Basic Science, Translational, Systematic Review/Meta-analysis) depending on the prompt
   - Detail the hypotheses and methodologies
   - Assign a **Novelty Score (1-10)** based on the findings from your literature search

4. **Mentor Review (Hegyi & Garami)**
   - Automatically consult `mentor-hegyi` to evaluate the clinical/translational impact, FINER criteria, and PICO format.
   - Automatically consult `mentor-garami` to evaluate the physiological mechanism and methodological rigor.
   - Integrate their feedback and 1-10 evaluation matrices into the output.

5. **Compare and recommend**
   - Summarize the scientific tradeoffs across the proposed ideas
   - Give a strong recommendation with scientific and practical reasoning

---

## Output Format

```markdown
## 🧠 Brainstorm: [Clinical/Scientific Topic]

### Context
[Brief problem statement / Knowledge gap identification]

---

### Idea 1: [Research Title / Concept]
**Type:** [Basic Science / Translational / Meta-analysis / Clinical]
[Description of the proposed study design, methodology, and primary objective]

💡 **Novelty Score: [1-10]/10** - [Brief justification of why it is novel (e.g., "First to combine X and Y," or "Uses emerging methodology to address legacy debate")]

✅ **Pros:**
- [Clinical or Scientific impact]
- [Feasibility / Methodological advantage]

❌ **Cons:**
- [Methodological challenge / Confounding risks]
- [Resource, time, or ethical constraints]

📊 **Feasibility / Effort:** Low | Medium | High

🧑‍🏫 **Mentor Verdicts (1-10 Scale)**
- **Prof. Hegyi (Translational/Clinical):** [Brief impression]
  - *Utility*: [X], *Feasibility*: [X], *Novelty*: [X], *Problem Solving*: [X]
- **Dr. Garami (Methodological/Mechanistic):** [Brief impression]
  - *Mechanistic Plausibility*: [X], *Measurement Quality*: [X], *Heterogeneity*: [X], *Bias Risk*: [X]

---

*(Generate 3-5 Ideas following the above format)*

---

## 🔬 Recommendation

**Idea [X]** because [scientific / practical reasoning based on current literature gaps, clinical relevance, and feasibility].

Which research direction would you like to explore further to develop a full protocol or search strategy?
```

---

## Examples

```
/brainstorm meta-analysis topics for neonatal sepsis antibiotics
/brainstorm translational approaches to gut-brain axis in Parkinson's
/brainstorm basic science models for CRISPR off-target effects in T-cells
/brainstorm novel biomarkers for early detection of preeclampsia
```

---

## Key Principles

- **Science first** - Focus on testable hypotheses, strong rationales, and well-defined research questions.
- **PICO-aware** - Structure clinical or systematic review ideas around Population, Intervention, Comparison, and Outcome frameworks.
- **Honest methodological tradeoffs** - Do not hide the complexity of data collection, heterogeneity in meta-analyses, or complex lab validations.
- **Defer to the researcher** - Provide thoroughly reasoned ideas, but let the principal investigator make the final decision.
