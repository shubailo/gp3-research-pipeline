# PROSPERO Protokoll Tervezet: Kísérletes Endotoxémia és Fájdalomérzékelés

Ez a dokumentum az **Ötlet 1** (A gyulladásos citokinek és a fájdalomküszöb változásának dózis-válasz meta-analízise kísérletes endotoxémiában) alapján készült strukturált protokoll tervezet, amely készen áll a PROSPERO adatbázisba történő feltöltésre.

## Review title
Dose-response relationship between inflammatory cytokines and pain threshold changes in experimental endotoxemia: a systematic review and meta-analysis in healthy human volunteers

## Condition or domain being studied
Inflammation; Pain; Hyperalgesia; Experimental Endotoxemia; Cytokines

## Rationale for the review
While systemic inflammation is known to induce 'sickness behavior' and modulate pain perception, the exact dose-response relationship between specific systemic inflammatory mediators (e.g., TNF-α, IL-6) and the magnitude of hyperalgesia remains unclear. Understanding this quantitative relationship in a standardized human model of experimental endotoxemia (intravenous lipopolysaccharide administration) is crucial to translating these findings to clinical settings, such as perioperative or sepsis-associated pain.

## Review objectives
1. **Primary objective:** To evaluate the effect of experimentally induced systemic inflammation via intravenous bacterial lipopolysaccharide (LPS) administration on pain sensitivity (hyperalgesia/allodynia) in healthy human volunteers compared to placebo.
2. **Secondary objective:** To determine the dose-response relationship between serum inflammatory cytokine levels (specifically TNF-α and IL-6) and the magnitude of changes in pain thresholds using meta-regression.

## PICO (Eligibility criteria)

### Population (P)
**Included:** Healthy adult human volunteer subjects (typically aged 18-65 years).
**Excluded:** Patients with pre-existing acute or chronic pain conditions, chronic inflammatory diseases, or those taking analgesic/anti-inflammatory medications.

### Intervention (I)
**Included:** Intravenous administration of bacterial lipopolysaccharide (LPS) / experimental endotoxemia.

### Comparator (C)
**Included:** Placebo administration (e.g., normal saline).

### Outcomes (O)
**Primary Outcome:**
- Changes in pain sensitivity measured by Quantitative Sensory Testing (QST), such as Pressure Pain Threshold (PPT), Heat Pain Threshold, or electrical pain threshold.

**Secondary Outcomes:**
- Serum/plasma concentrations of key inflammatory cytokines (TNF-α, IL-6), specifically peak concentrations or Area Under the Curve (AUC).
- Correlation coefficients or regression metrics linking cytokine levels with pain threshold changes.

### Study design
**Included:** Randomized Controlled Trials (RCTs), including crossover and parallel-group designs.
**Excluded:** Observational studies, animal studies, in vitro experiments, non-randomized trials, reviews, and case reports.

## Search strategy
We will search the following databases from inception to present without language restrictions:
- PubMed / MEDLINE
- Embase
- Cochrane Central Register of Controlled Trials (CENTRAL)
- Web of Science

*Draft PubMed Search String:*
`("experimental endotoxemia" OR "endotoxemia" OR "lipopolysaccharide" OR "LPS") AND ("pain" OR "pain perception" OR "hyperalgesia" OR "allodynia" OR "nociception" OR "pain threshold") AND ("cytokines" OR "TNF-alpha" OR "IL-6" OR "inflammatory mediators")`

## Data extraction (selection and coding)
Two independent reviewers will screen titles and abstracts, followed by full-text screening using a standardized tool (e.g., Rayyan). Disagreements will be resolved by a third investigator. Data extraction will include study characteristics, participant demographics, LPS source and dose, QST modalities, cytokine measurement timepoints, and quantitative outcome data (mean, SD, n).

## Risk of bias (quality) assessment
Two independent reviewers will assess the risk of bias using the Cochrane Risk of Bias 2 (RoB 2) tool for randomized trials.

## Strategy for data synthesis
We will perform a meta-analysis using R or RevMan. Continuous outcomes (pain thresholds) will be pooled using Standardized Mean Differences (SMD) with 95% Confidence Intervals (CI) due to potential variations in QST methodologies. Random-effects models will be employed to account for anticipated clinical and methodological heterogeneity. Meta-regression will be used to analyze the relationship between peak cytokine levels (or administered LPS dose) and the effect size of hyperalgesia.
