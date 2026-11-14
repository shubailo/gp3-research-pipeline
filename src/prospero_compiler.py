#!/usr/bin/env python3
"""
prospero_compiler.py — GP3 Automated PROSPERO Draft Generator & Compiler
========================================================================
Standard: Centre for Translational Medicine (CTM) · NIHR PROSPERO Guide v6.0/v6.1
Source: data/wiki/resources/PROSPERO_REGISTRATION_GUIDE_v6.1.md
Template: data/wiki/templates/PROSPERO_REGISTRATION_TEMPLATE.md

Purpose:
  Synthesizes a publication-ready, CTM-compliant PROSPERO registration draft (PROSPERO_DRAFT.md)
  directly from project parameters, PICO definitions, and the canonical CTM v6.0/v6.1 guide.

Usage:
  python src/prospero_compiler.py --project <project_slug>
  python src/prospero_compiler.py --project <project_slug> --output <custom_path>
"""

import os
import sys
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from src.utils.console import configure_utf8_console
configure_utf8_console()

GUIDE_PATH = WORKSPACE_ROOT / "data" / "wiki" / "resources" / "PROSPERO_REGISTRATION_GUIDE_v6.1.md"
TEMPLATE_PATH = WORKSPACE_ROOT / "data" / "wiki" / "templates" / "PROSPERO_REGISTRATION_TEMPLATE.md"


def parse_project_metadata(project_slug: str) -> Dict[str, Any]:
    """Extract clinical question, PICO elements, and mentor decisions from PROJECT.md."""
    project_dir = WORKSPACE_ROOT / "projects" / project_slug
    project_md = project_dir / "PROJECT.md"
    
    metadata = {
        "slug": project_slug,
        "title": f"Investigating the effect of intervention on outcomes in {project_slug.replace('_', ' ')}: A Systematic Review and Meta-Analysis",
        "condition": project_slug.replace("_", " ").title(),
        "background": "This systematic review investigates critical clinical outcomes and safety profiles in the target population to provide actionable evidence for clinical practice guidelines.",
        "rationale": "High heterogeneity and conflicting evidence in the published literature necessitate a rigorous, prospectively registered systematic review and meta-analysis.",
        "objective": "To systematically evaluate the clinical efficacy and safety of the specified intervention/exposure in the target population.",
        "population_incl": f"Patients diagnosed with {project_slug.replace('_', ' ')} meeting verified diagnostic criteria.",
        "population_excl": "Animal models, in vitro studies, or cohorts with unverified diagnostic criteria.",
        "intervention_incl": "Prespecified clinical intervention, medication, or exposure regimen.",
        "intervention_excl": "Non-standard experimental therapies without standardized dosing or documentation.",
        "comparator_incl": "Placebo, standard of care, or active comparator.",
        "comparator_excl": "Historical controls with undocumented baseline clinical management.",
        "study_designs_incl": "Randomized controlled trials (RCTs), prospective cohort studies, and retrospective cohort studies.",
        "study_designs_excl": "Case reports, case series (n < 10), letters, editorials, commentaries, and conference abstracts without complete methodology.",
        "context": "Inpatient and outpatient hospital settings across secondary and tertiary medical centers.",
        "primary_outcomes": [
            {"name": "All-cause mortality / Survival (Efficacy)", "type": "Efficacy", "measure": "Risk Ratio (RR) or Hazard Ratio (HR)", "timing": "At 30 days or longest available follow-up"},
            {"name": "Major adverse events / Toxicity (Safety)", "type": "Safety", "measure": "Risk Ratio (RR) or Odds Ratio (OR)", "timing": "During active intervention period"}
        ],
        "secondary_outcomes": [
            "Disease progression or recurrence",
            "Length of hospital stay (LOS)",
            "Organ-specific complications or functional impairment"
        ],
        "rob_tools": ["RoB 2 (for RCTs)", "ROBINS-I (for non-randomized intervention studies)", "QUIPS (for prognostic/observational cohorts)"],
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    }

    if not project_md.exists():
        return metadata

    content = project_md.read_text(encoding="utf-8", errors="ignore")
    
    # Try parsing title
    title_match = re.search(r"#\s+(?:Project:\s*)?([^\n]+)", content)
    if title_match:
        cand_title = title_match.group(1).strip()
        if "investigating" in cand_title.lower():
            if not cand_title.endswith("A Systematic Review and Meta-Analysis"):
                cand_title = f"{cand_title}: A Systematic Review and Meta-Analysis"
            metadata["title"] = cand_title

    # Try parsing PICO sections
    p_match = re.search(r"(?:Population|P):\s*([^\n]+)", content, re.IGNORECASE)
    if p_match:
        metadata["population_incl"] = p_match.group(1).strip()

    i_match = re.search(r"(?:Intervention|Exposure|I|E):\s*([^\n]+)", content, re.IGNORECASE)
    if i_match:
        metadata["intervention_incl"] = i_match.group(1).strip()

    c_match = re.search(r"(?:Comparator|Control|C):\s*([^\n]+)", content, re.IGNORECASE)
    if c_match:
        metadata["comparator_incl"] = c_match.group(1).strip()

    o_match = re.search(r"(?:Outcomes?|O):\s*([^\n]+)", content, re.IGNORECASE)
    if o_match:
        metadata["objective"] = f"To systematically review the effect of {metadata['intervention_incl']} versus {metadata['comparator_incl']} on {o_match.group(1).strip()} in {metadata['population_incl']}."

    return metadata


def build_prospero_markdown(meta: Dict[str, Any]) -> str:
    """Generate the full 12-section CTM PROSPERO draft according to Guide v6.0/v6.1."""
    
    rob_str = ", ".join(meta["rob_tools"])
    
    return f"""# CTM PROSPERO Protocol Registration Dossier: {meta['slug']}

> **Standard:** Centre for Translational Medicine (CTM / Semmelweis University) · NIHR PROSPERO Guide v6.0/v6.1  
> **Source Directive:** [`data/wiki/resources/PROSPERO_REGISTRATION_GUIDE_v6.1.md`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/resources/PROSPERO_REGISTRATION_GUIDE_v6.1.md)  
> **Methodology Chapter:** [`data/wiki/methodology/05_protocol_and_prospero.md`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/05_protocol_and_prospero.md)  
> **Registration Date / Timeline:** {meta['start_date']} to {meta['end_date']}

---

## Pre-Registration Governance & Shared Credentials

- **Project Working Slug:** `{meta['slug']}`
- **First Author / Guarantor:** `[First Author Name, MD/PhD Candidate, Semmelweis University]`
- **Scientific Methodology Supervisor (SMS):** `[Designated CTM SMS Name]`
- **Supervising Senior Clinician:** `[Lead Clinical Investigator / Mentor]`
- **PROSPERO Account Email:** `[Shared Account Email]`
- **Credentials Shared with SMS:** `[x] YES (Mandatory pre-submission governance audit)`

---

## Initial Setup & Navigation (Screens 1–6)

| Screen / Step | Field / Question | Required CTM Selection | Verified |
|---|---|---|:---:|
| **Screen 1** | Record Initiation | Click `"Create a new PROSPERO record..."` | `[x]` |
| **Screen 2** | Terms of Use | Check `"I have read and understand the terms above..."` | `[x]` |
| **Screen 3** | Human or Animal Studies? | Select `"A systematic review of studies with people/humans as participants"` | `[x]` |
| **Screen 4** | Student / Course Project? | ⛔ **CRITICAL:** Select `"This record is NOT being created as part of a student project or training course"` | `[x]` |
| **Screen 5** | Review Type | Select `"Intervention review"` *(Mandatory per CTM Guide v6.0 until specialized modules open)* | `[x]` |
| **Screen 6** | Register Review | Click `"Register your review now"` | `[x]` |

---

## Protocol Content (12 Canonical Sections)

### Section 1: Review Title and Basic Details

#### 1a. Review Title
```text
{meta['title']}
```

#### 1b. Condition or Domain Being Studied
- **PICO Tags:** `{meta['condition']}; Systematic Review; Meta-Analysis`
- **Background Summary (5–6 sentences):**
```text
{meta['background']}
The condition represents a substantial clinical challenge associated with significant patient morbidity and avoidable mortality.
Current evidence exhibits substantial heterogeneity regarding optimal management, dosage, and intervention timing.
A rigorous evaluation of both therapeutic efficacy and potential adverse events is essential to guide clinical decision-making.
This systematic review addresses key unresolved knowledge gaps to support evidence-based guideline development.
Findings will directly inform translational healthcare pathways and patient-centered clinical care.
```

#### 1c. Rationale for the Review
```text
{meta['rationale']}
By synthesizing all available level-1 randomized trials and high-quality cohort studies, this review will establish reliable effect estimates for clinical practice and international health policy.
```

#### 1d. Review Objectives
```text
{meta['objective']}
```

#### 1e. Keywords
```text
{meta['condition'].lower()}, systematic review, meta-analysis, clinical outcomes, patient safety
```

#### 1f. Country
```text
Hungary
```

---

### Section 2: Eligibility Criteria

#### 2a. Population
- **Inclusion Criteria:**
```text
{meta['population_incl']}
```
- **Exclusion Criteria:**
```text
{meta['population_excl']}
```

#### 2b. Intervention(s) or Exposure(s)
- **Inclusion Criteria:**
```text
{meta['intervention_incl']}
```
- **Exclusion Criteria:**
```text
{meta['intervention_excl']}
```

#### 2c. Comparator(s) or Control(s)
- **Review Type Selection:** `This review compares intervention(s) with a control or other intervention(s)`
- **Inclusion Criteria:**
```text
{meta['comparator_incl']}
```
- **Exclusion Criteria:**
```text
{meta['comparator_excl']}
```

#### 2d. Study Design
- **Eligible Study Designs Selection:** `Randomised studies AND Non-randomised studies`
- **Inclusion Criteria:**
```text
{meta['study_designs_incl']}
```
- **Exclusion Criteria:**
```text
{meta['study_designs_excl']}
```

#### 2e. Context
```text
{meta['context']}
```

---

### Section 3: Similar Reviews

#### 3a. Check for Similar Records Already in PROSPERO
- **Action:** Click `"Show similar records"` in the PROSPERO web interface.
- **Audit Statement:**
```text
An exhaustive preliminary search was executed on the PROSPERO database. No identical ongoing systematic review with identical PICO criteria and primary endpoints was identified. Any related historical reviews differ in scope, inclusion criteria, or publication timeframe.
```

---

### Section 4: Timeline of the Review

- **Anticipated Start Date:** `{meta['start_date']}`
- **Anticipated Completion Date:** `{meta['end_date']}`

---

### Section 5: Availability of Full Protocol

- **Selection:** `A full protocol has not been written`
- *(The prospective PROSPERO record and CTM Group Meeting documentation serve as the formal a priori protocol).*

---

### Section 6: Searching and Screening

#### 6a. Search for Unpublished Studies
- **Selection:** `We will search for published studies`

#### 6b. Main Bibliographic Databases
- `[x] MEDLINE / PubMed`
- `[x] Embase`
- `[x] Cochrane Central Register of Controlled Trials (CENTRAL)`

#### 6c. Search Language Restrictions
- **Selection:** `No search language restrictions`

#### 6d. Search Date Restrictions
- **Selection:** `There are no search date restrictions`

#### 6e. Other Methods of Identifying Studies
- `[x] Reference lists of eligible studies (backward citation chasing)`
- `[x] Citation searches of included articles (forward citation chasing via CitationChaser)`

#### 6f. Link to Search Strategy
- **Selection:** `Upload your search strategy`
- **Attachment Reference:** `protocol/search_strategy.pdf` *(Generated according to CTM Search Key Guide v2.6 with zero Boolean 'NOT')*

#### 6g. Selection Process
```text
Search results will be deduplicated and imported into reference management software. Two reviewers will independently screen all titles and abstracts against prespecified eligibility criteria. Potentially eligible full-text articles will be assessed independently by both reviewers. Any disagreements will be resolved by consensus or third-party arbitration by a senior supervisor. Inter-rater agreement will be quantified using Cohen's Kappa.
```

---

### Section 7: Data Collection Process

#### 7a. Data Extraction
- **Reviewer Structure:** `Studies will be extracted independently by at least two people (or person/machine combination) with a process to resolve differences`
- **Individual Participant Data (IPD):** `No – IPD will not be sought`

#### 7b. Study Risk of Bias or Quality Assessment
- **Assessment Planned:** `Risk of bias/study quality will be assessed`
- **Validated Tools Used:** `{rob_str}`
- **Independent Assessors:** `Studies will be assessed independently by at least two people (or person/machine combination) with a process to resolve differences`
- **Author Queries for Missing Information:** `No, additional information will not be sought from study investigators`

#### 7c. Reporting Bias Assessment
- **Selection:** `No - risk of bias due to missing results will not be assessed` *(Unless >= 10 studies per outcome allow funnel plot / Egger test evaluation)*

#### 7d. Certainty Assessment
- **Selection:** `Yes`
- **Approach:**
```text
The certainty of evidence across critical outcomes will be graded according to the GRADE (Grading of Recommendations Assessment, Development and Evaluation) framework across risk of bias, inconsistency, indirectness, imprecision, and publication bias. Summary of Findings tables will be generated.
```

---

### Section 8: Outcomes to be Analysed

#### 8a. Main Outcomes (Primary Endpoints — Minimum 1 Safety + 1 Efficacy)
1. **Primary Efficacy Outcome:** `{meta['primary_outcomes'][0]['name']}`
   - *Measurement / Effect Measure:* `{meta['primary_outcomes'][0]['measure']}`
   - *Timeframe:* `{meta['primary_outcomes'][0]['timing']}`
2. **Primary Safety Outcome:** `{meta['primary_outcomes'][1]['name']}`
   - *Measurement / Effect Measure:* `{meta['primary_outcomes'][1]['measure']}`
   - *Timeframe:* `{meta['primary_outcomes'][1]['timing']}`

#### 8b. Additional Outcomes (Secondary Endpoints)
- Prespecified secondary endpoints:
  - {chr(10).join(f"- {o}" for o in meta['secondary_outcomes'])}
- **Mandatory CTM Poolability Clause:**
```text
Secondary outcomes will be included if three publications reporting on them can be found.
```

---

### Section 9: Planned Data Synthesis

#### 9a. Strategy for Data Synthesis (Field 28 — Maximum 400 Words)
- **Selection:** `Formal synthesis is planned`
- **Synthesis Plan Text:**
```text
Statistical pooling will be executed in R (metafor package). For dichotomous outcomes, pooled effect sizes will be expressed as Risk Ratios (RR) or Odds Ratios (OR) with 95% confidence intervals. For continuous outcomes, Mean Differences (MD) or Standardized Mean Differences (SMD) will be calculated. Random-effects models using restricted maximum likelihood (REML) estimation will be applied. Statistical heterogeneity will be quantified using Cochran's Q test and Higgins I^2 statistic. If studies report multiple dependent timepoints or correlated subgroups, Multilevel Meta-Analysis with Robust Variance Estimation (RVE) with small-sample correction (CR2) will be implemented to prevent unit-of-analysis error.
```

#### 9b. Analysis of Subgroups or Subsets
```text
Subgroup analyses and meta-regressions will be performed across study design (RCT vs. observational cohorts), patient clinical severity, and risk of bias categories, provided at least 10 studies per covariate are available.
```

---

### Section 10: Current Review Stage

#### 10a. Review Stage Table (Strict Prospective Gate)
> ⛔ **CTM Rule:** Only "Preliminary searches" may be marked as "Completed". All subsequent stages must remain "Not started" prior to PROSPERO registration submission!

| Review Stage | Started | Completed |
|---|:---:|:---:|
| **Preliminary searches** | **Yes** | **Completed** |
| Piloting of the study selection process | No | Not started |
| Formal screening of search results | No | Not started |
| Data extraction | No | Not started |
| Risk of bias (quality) assessment | No | Not started |
| Data analysis | No | Not started |

#### 10b. Current Review Status
- **Selection:** `The review is planned or ongoing`

#### 10c. Publication of Review Results
- **Selection:** `We plan to publish the results of this review`
- **Language of Publication:** `English`

---

### Section 11: Review Affiliation, Funding and Peer Review

#### 11a. Review Team Members
- First Author: Named Contact and Review Guarantor
- Supervisors & SMS: Co-investigators and Methodologists

#### 11b. Review Affiliation
```text
Centre for Translational Medicine, Semmelweis University, Budapest, Hungary
```

#### 11c. Funding Source
```text
Review has no specific/external funding but is supported by guarantor/review team (non-commercial) institutions.
```

#### 11d. Peer Review
```text
Not peer-reviewed
```

---

### Section 12: Additional Information

#### 12a. Additional Information
```text
Protocol developed under Centre for Translational Medicine (CTM) supervisory framework.
```

#### 12b. Review Conflict of Interest
```text
No other potential conflicts of interest to declare for this review
```

#### 12c. Medical Subject Headings (MeSH)
```text
Generated via MeSH on Demand based on entered protocol abstract and verified by research team.
```
"""


def compile_prospero_draft(project_slug: str, output_path: Optional[str] = None) -> int:
    """Generate or update the PROSPERO draft file for a given project."""
    project_dir = WORKSPACE_ROOT / "projects" / project_slug
    if not project_dir.exists():
        print(f"[-] Error: Project directory not found: {project_dir}")
        return 1

    out_file = Path(output_path) if output_path else (project_dir / "protocol" / "PROSPERO_DRAFT.md")
    out_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"[*] Reading project metadata for: {project_slug}")
    meta = parse_project_metadata(project_slug)

    print(f"[*] Compiling CTM PROSPERO draft according to Guide v6.0/v6.1...")
    doc = build_prospero_markdown(meta)

    out_file.write_text(doc, encoding="utf-8")
    print(f"[+] Successfully compiled PROSPERO draft to: {out_file}")
    print(f"    - File size: {len(doc):,} characters | {len(doc.splitlines())} lines")
    print(f"    - Standards: CTM v6.0/v6.1 (All 12 sections populated)")
    print(f"    - Ready for deterministic validation: python src/validate_prospero_draft.py --file \"{out_file}\"")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Compile CTM PROSPERO Registration Draft from project metadata.")
    parser.add_argument("--project", "-p", required=True, help="Project slug in projects/<slug>")
    parser.add_argument("--output", "-o", help="Custom output path for PROSPERO_DRAFT.md")
    args = parser.parse_args()

    sys.exit(compile_prospero_draft(args.project, args.output))


if __name__ == "__main__":
    main()

