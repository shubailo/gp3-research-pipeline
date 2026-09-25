---
description: Feasibility and White Spot Assessment workflow. Runs literature search, extracts trends, identifies gaps, verifies poolability, and creates a feasibility report.
---

# /feasibility - Feasibility, Poolability & White Spot Assessment

$ARGUMENTS

---

## Purpose

This command activates **FEASIBILITY MODE** to evaluate a specific research question or systematic review idea. It automates the process of executing a targeted literature search using repository scripts, identifying quantitative trends, extracting a qualitative digest, enforcing the **Feasibility Poolability Rule**, and producing a comprehensive feasibility report.

Use this workflow when you have a defined research question (or PICO) and need to verify if it constitutes a valid "white spot" (genuine research gap) with sufficient poolable data before writing a full protocol or registering on PROSPERO.

---

## Behavior

When `/feasibility` is triggered:

1. **Formulate the Search Query:**
   - Review `$ARGUMENTS` provided by the user.
   - Formulate a comprehensive PubMed search string following the 3-Step Search Key structure:
     `1. Population [AND] 2. Exposure/Intervention [AND] 3. Therapy/Context`.
     > ⛔ **NEVER** use the `NOT` Boolean operator.

2. **Execute Literature Search via Local Engine:**
   - Run the local script from workspace root:
     ```bash
     python src/literature_search.py "<COMPLEX_QUERY>" --analyze --max-results 100 --years 5
     ```
   - Capture the output, extracting the **Quantitative Summary** (total hits, 5-year trend) and the **Abstract Digest**.

3. **Methodological & Poolability Analysis (CTM Standard):**
   - **Quantitative Status & Trends:** Total hits, publication trend over the past 2–3 years (hot research areas with high publication probability).
   - **Previous Meta-Analyses Assessment:**
     * *Inconclusive & >2–3 years old:* Update is justified; search for subsequent original research.
     * *Conclusive:* Topic is answered unless a new angle is identified (subgroup analysis, meta-regression, dose-response).
     * *Very recent:* Cannot repeat without a fundamentally distinct clinical question.
   - **Keyword Harvesting:** Analyze search keys of 5–10 previous meta-analyses per domain to ensure comprehensive coverage.
   - **White Spot Analysis:** Identify what specific aspects of the research question are absent from published literature (e.g., specific sub-populations, time windows, exposure thresholds).
   - **Feasibility Poolability Check (CTM Mandatory Gate):**
     > ⚠️ At least **3–4 key primary articles** must report **THE EXACT SAME primary outcome** with complete numerical data.
     Identify the top primary studies and verify if their primary endpoints can be quantitatively pooled.
   - **Clinical Mind Map & Preliminary Extraction:**
     * Prepare a clinical Mind Map for the project statisticians illustrating the exposure-outcome biological pathway.
     * Hold Preliminary Extraction Meetings 1 & 2 with SMS, supervisor, and statistician to approve feasibility before proceeding to protocol registration.
   - **Confounding & Bias Assessment:** Identify major sources of confounding and specify required covariates for a Confounder Matrix.

4. **Generate the Feasibility Assessment Artifact:**
   - Create or overwrite markdown artifact `feasibility_assessment.md` in the current conversation's artifact directory.
   - The artifact must include:
     - **Research Question & Query:** The exact question and PubMed syntax used.
     - **Quantitative Status:** Hits, publication trend over 5 years.
     - **Originality Verdict:** Is this a true "white spot"?
     - **Literature State:** What is known vs. what is missing.
     - **Poolability Verification Table:**
       | Study (Author, Year) | Population | Exposure / Intervention | Primary Outcome Reported | Poolable with ≥2 Others? |
       |---|---|---|---|---|
     - **Confounding Risks & Biases:** Key covariates required.
     - **Final Recommendation:** **GO** (poolable data confirmed & white spot present), **PIVOT** (outcomes heterogeneous, adjust PICO), or **NO-GO** (saturated or empty review).

5. **Inform the User:**
   - Concisely summarize the feasibility verdict, poolability status, and Go/No-Go decision in chat, directing the user to the artifact.
