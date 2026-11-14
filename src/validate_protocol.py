#!/usr/bin/env python3
"""
Medical Research Protocol Compliance Linter (GP3 / CTM Standards)
================================================================
Deterministic CLI tool to audit academic research protocols and plan files against
the Centre for Translational Medicine (CTM) standards and GP3 mentor requirements.

Usage:
    python .agent/scripts/validate_protocol.py <path_to_markdown_file> [--strict]

Gates Evaluated:
    1. PICO Title Formula ("Investigating the effect of [E/I] on [O] in [P]")
    2. The Suffering Narrative (Child suffering, Parent burden, Clinical hope)
    3. 6-Point Quantitative Background Completeness (Incidence per 1000, untreated %, etc.)
    4. Search Key Syntax & Domain Structure (Forbidden NOT check, 3-domain structure)
    5. Feasibility Poolability Gate (>= 3 primary studies with identical outcome)
    6. Methodological Quality & Confounder Matrix (QUIPS / RoB 2, pre-specified covariates, RVE)
    7. Translational Pipeline & Avoidable Mortality (T1-T4 stage, preventable mortality)
"""

import sys
import os
import re
import argparse

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from src.utils.console import configure_utf8_console
configure_utf8_console()

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def check_title_formula(content: str) -> tuple[str, str, int]:
    pattern = r"investigating\s+the\s+effect\s+of\s+.+\s+on\s+.+\s+in\s+.+"
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        return "PASS", f"Found valid PICO title: '{match.group(0).strip()[:80]}...'", 15
    
    # Check if there is any title mentioning effect of ... on ...
    alt_pattern = r"effect\s+of\s+.+\s+on\s+.+"
    if re.search(alt_pattern, content, re.IGNORECASE):
        return "WARN", "Title contains 'effect of... on...' but lacks standard 'Investigating the effect of [E] on [O] in [P]' formula", 8
    
    return "FAIL", "Missing mandatory PICO title formula: 'Investigating the effect of [Exposure/Intervention] on [Outcome] in [Population]'", 0

def check_suffering_narrative(content: str) -> tuple[str, str, int]:
    content_lower = content.lower()
    
    # 1. Patient / Child Suffering
    patient_terms = ["suffering", "morbidity", "impairment", "disability", "cerebral palsy", 
                     "cognitive", "motor", "sensory", "blindness", "hearing loss", "organ failure", "death", "mortality"]
    patient_found = sum(1 for t in patient_terms if t in content_lower)
    
    # 2. Parent / Family Burden
    parent_terms = ["parent", "family", "caregiver", "emotional", "financial", "burden", "strain", "daily care"]
    parent_found = sum(1 for t in parent_terms if t in content_lower)
    
    # 3. Clinical Hope
    hope_terms = ["hope", "relief", "lives saved", "improve survival", "clinical impact", "relieved", "benefit", "preventable"]
    hope_found = sum(1 for t in hope_terms if t in content_lower)
    
    if patient_found >= 2 and parent_found >= 1 and hope_found >= 1:
        return "PASS", f"Complete Suffering Narrative detected (Patient: {patient_found} refs, Family: {parent_found} refs, Hope: {hope_found} refs)", 15
    elif patient_found >= 1 and (parent_found >= 1 or hope_found >= 1):
        missing = []
        if parent_found == 0: missing.append("Parent/Family Burden")
        if hope_found == 0: missing.append("Clinical Hope")
        return "WARN", f"Partial Suffering Narrative. Missing emphasis on: {', '.join(missing)}", 8
    else:
        return "FAIL", "Missing the Suffering Narrative (Must articulate patient morbidities, parental burden, and clinical hope)", 0

def check_background_completeness(content: str) -> tuple[str, str, int]:
    content_lower = content.lower()
    score = 0
    details = []
    
    # Point 1: Definition & Mechanism
    if any(k in content_lower for k in ["definition", "pathophysiology", "mechanism", "pathomechanism", "biology", "etiology", "ischemia", "inflammation", "cascade", "pathway"]):
        score += 2
        details.append("Definition/Mechanism")
        
    # Point 2: Incidence with numbers (e.g., per 1,000 or %)
    if re.search(r"(\d+(\.\d+)?\s*(per|\/)\s*1,?000|\d+(\.\d+)?\s*%|\bincidence\b.*\d+)", content_lower):
        score += 3
        details.append("Numerical Incidence")
    else:
        details.append("MISSING: Numerical Incidence")
        
    # Point 3: Untreated prognosis numbers
    if re.search(r"(mortality|morbidity|untreated|death|adverse).*\b\d+(\.\d+)?\s*%", content_lower):
        score += 3
        details.append("Prognosis Mortality/Morbidity %")
    else:
        details.append("MISSING: Prognosis Numbers")
        
    # Point 4: Gold standard treatment
    if any(k in content_lower for k in ["gold standard", "standard of care", "current therapy", "first-line", "guideline", "clinical practice", "standard treatment"]):
        score += 2
        details.append("Gold Standard")
        
    # Point 5: Epidemiological link between exposure & population with numbers
    if re.search(r"(associated with|prevalence of|occurs in|risk of).*\b\d+(\.\d+)?\s*%", content_lower):
        score += 3
        details.append("Epidemiological Link %")
    else:
        details.append("MISSING: Epidemiological Link %")
        
    # Point 6: Unanswered research question
    if any(k in content_lower for k in ["knowledge gap", "unanswered", "remains unclear", "aim of this study", "white spot", "unresolved"]):
        score += 2
        details.append("Unanswered Question")
        
    if score >= 13:
        return "PASS", f"6-Point Background Verified ({score}/15 pts: {', '.join(details[:3])}...)", 15
    elif score >= 8:
        return "WARN", f"Partial Quantitative Background ({score}/15 pts). Missing exact numbers for some epidemiological points", 8
    else:
        return "FAIL", f"Insufficient Background Completeness ({score}/15 pts). Needs numerical incidence, mortality %, and epidemiological rates", 0

def check_search_syntax(content: str) -> tuple[str, str, int]:
    # Check for forbidden NOT operator in search blocks
    cochrane_animal_pattern = r"NOT\s*\(\s*(?:exp\s+)?animals?(?:\[\w+\])?\s+NOT\s+humans?(?:\[\w+\])?\s*\)"
    has_cochrane_animal_filter = bool(re.search(cochrane_animal_pattern, content, re.IGNORECASE))
    
    # Strip Cochrane animal filter before scanning for unauthorized NOT
    content_clean = re.sub(cochrane_animal_pattern, "", content, flags=re.IGNORECASE)
    
    unauthorized_not_lines = []
    for line in content_clean.splitlines():
        if "AND" in line and "OR" in line:
            if re.search(r"\bNOT\b", line):
                unauthorized_not_lines.append(line.strip())
                
    if unauthorized_not_lines:
        bad_sample = unauthorized_not_lines[0][:60]
        return "FAIL", f"CRITICAL VIOLATION: Arbitrary Boolean 'NOT' found ('{bad_sample}...'). Only Cochrane animal filter ('NOT (animals NOT humans)') is permitted!", 0
        
    # Check for 3-domain structure
    has_population = any(k in content.lower() for k in ["population", "participant", "patient", "cohort", "subject", "mesh", "infant", "neonate", "pediatric", "child", "adult"])
    has_exposure = any(k in content.lower() for k in ["exposure", "intervention", "treatment", "therapy", "drug", "agent", "regimen", "procedure", "biomarker", "dose", "duration"])
    has_and = " AND " in content or "AND" in content
    
    if has_cochrane_animal_filter and has_population and has_exposure:
        return "PASS", "Search syntax follows 3-domain ordering with standard Cochrane animal exclusion filter (documented exception)", 15
    elif has_population and has_exposure and has_and:
        return "PASS", "Search syntax follows domain ordering without forbidden 'NOT' operator", 15
    else:
        return "WARN", "Search strategy present but missing explicit 3-domain structure (Population AND Exposure AND Therapy)", 8

def check_poolability_rule(content: str) -> tuple[str, str, int]:
    content_lower = content.lower()
    
    # Check for mention of poolability or key articles
    has_poolability_keyword = any(k in content_lower for k in ["poolab", "poolability", "identical outcome", "exact same outcome"])
    
    # Count references without double counting author and PMID on the same line
    pmids = set(re.findall(r"PMID:\s*(\d+)", content))
    study_lines = [line.strip() for line in content.splitlines() if re.search(r"\b(?:[A-Z][a-z]+(?:\s+et\s+al\.?|\s+and\s+[A-Z][a-z]+)?,\s+(?:19|20)\d{2}|PMID:\s*\d+)\b", line)]
    
    if len(pmids) > 0:
        k_studies = len(pmids)
    elif len(study_lines) > 0:
        k_studies = len(study_lines)
    else:
        author_years = set(re.findall(r"\b([A-Z][a-z]+(?:\s+et\s+al\.?|\s+and\s+[A-Z][a-z]+)?,\s+(?:19|20)\d{2})\b", content))
        k_studies = len(author_years)
    
    if k_studies >= 3:
        if has_poolability_keyword:
            return "PASS", f"Poolability Rule satisfied: {k_studies} key studies identified with shared outcome endpoints", 15
        else:
            return "WARN", f"Found {k_studies} primary study citations, but verify that at least 3 report THE EXACT SAME primary outcome", 12
    elif k_studies == 2:
        return "WARN", f"Found exactly 2 primary studies. Matematikailag poolozható (RevMan fixed/random effects), de a CTM/GP3 heurisztika legalább 3 vizsgálatot követel a megbízható heterogenitás- és alcsoport-becsléshez!", 8
    elif k_studies == 1:
        return "FAIL", f"Only 1 primary study identified. Kvantitatív metaanalízis lehetetlen (minimum 2 vizsgálat kell a szintézishez, 3 a GP3 poolozhatósághoz)!", 3
    else:
        return "FAIL", "No key primary studies identified. Poolability Rule requires at least 3 studies reporting identical outcomes", 0

def check_methodological_rigor(content: str) -> tuple[str, str, int]:
    content_lower = content.lower()
    score = 0
    details = []
    warnings = []
    
    # Check for Risk of Bias tools
    rob_tools = ["rob 2", "rob2", "quips", "robins-i", "robins", "quadas", "newcastle-ottawa", "nos"]
    found_tools = [t.upper() for t in rob_tools if t in content_lower]
    if found_tools:
        score += 5
        details.append(f"RoB Tool ({', '.join(set(found_tools))})")
    else:
        details.append("MISSING: Validated RoB Tool")
        
    # Check for Confounder Matrix or adjusted variables
    if any(k in content_lower for k in ["confounder matrix", "confounder", "adjusted odds", "multivariable", "covariate"]):
        score += 5
        details.append("Confounder Matrix / Covariates")
    else:
        details.append("MISSING: Confounder Matrix")
        
    # Check for Multilevel / RVE / Heterogeneity
    has_rve = any(k in content_lower for k in ["robust variance estimation", "rve"])
    has_meta = any(k in content_lower for k in ["multilevel", "heterogeneity", "random-effects", "i2", "i^2"])
    if has_rve or has_meta:
        score += 5
        details.append("Synthesis/RVE Strategy")
    else:
        details.append("MISSING: Heterogeneity/RVE")
        
    # Cochrane Handbook 10.11.4: Meta-regression sample size audit (>= 10 studies per covariate)
    if "meta-regression" in content_lower or "meta-regresszi" in content_lower:
        # Check bidirectional pattern for small study counts (e.g. meta-regression of 5 studies OR 5 studies meta-regression)
        small_study_match = re.search(r"(?:meta-regress\w*\s+(?:of|with|on)?\s*(\b[1-9]\b)\s+(?:tanulmány|studies|trials)|(\b[1-9]\b)\s+(?:tanulmány|studies|trials)\b[^\n]*(?:meta-regress))", content_lower)
        if small_study_match:
            k_val = small_study_match.group(1) or small_study_match.group(2)
            score = max(0, score - 3)
            warnings.append(f"Alulmintázott meta-regresszió ({k_val} tanulmány < 10/kovariáns szabály, Cochrane 10.11.4)")
        
    # Ecological Fallacy check: study-level average inferring patient-level causal effect
    if ("ökológiai" in content_lower or "ecological" in content_lower) and any(w in content_lower for w in ["egyéni", "patient-level", "közvetlen okoz", "csökkenti a beteg"]):
        if not any(ipd in content_lower for ipd in ["ipd", "individual participant", "korlát", "fallacy", "csapda", "óvatossággal"]):
            score = max(0, score - 3)
            warnings.append("Ökológiai torzítás: tanulmányszintű átlagból nem vonható le egyéni szintű kauzális következtetés IPD nélkül!")

    # RVE small-sample correction check (Tipton / Pustejovsky CR2 / Satterthwaite)
    if has_rve:
        if not any(k in content_lower for k in ["cr2", "satterthwaite", "tipton", "pustejovsky", "small-sample", "kis mintás"]):
            warnings.append("RVE kis mintás korrekció (CR2 / Satterthwaite) nincs specifikálva (<40 tanulmány esetén I. fajú hiba infláció)")
            score = max(0, score - 2)

    if score >= 12 and not warnings:
        return "PASS", f"Methodological Rigor Verified ({score}/15 pts: {', '.join(details)})", 15
    elif score >= 8:
        warn_str = f" | Figyelmeztetések: {'; '.join(warnings)}" if warnings else ""
        return "WARN", f"Partial Methodological Spec ({score}/15 pts: {', '.join(details)}{warn_str})", score
    else:
        warn_str = f" | Hibák: {'; '.join(warnings)}" if warnings else ""
        return "FAIL", f"Methodological rigor insufficient ({score}/15 pts: {', '.join(details)}{warn_str})", score

def check_translational_stage(content: str) -> tuple[str, str, int]:
    content_lower = content.lower()
    
    has_stage = bool(re.search(r"\bt[0-4]\b|translational\s+stage|t1|t2|t3|t4", content_lower))
    has_avoidable_mortality = any(k in content_lower for k in ["avoidable mortality", "kerülhető mortalitás", "lives saved", "daly", "preventable", "clinical practice guideline"])
    
    if has_stage and has_avoidable_mortality:
        return "PASS", "Translational Stage (T0-T4) and Avoidable Mortality goals explicitly declared", 10
    elif has_stage or has_avoidable_mortality:
        return "WARN", "Translational relevance mentioned, but should explicitly declare T1-T4 stage and targeted avoidable mortality", 6
    else:
        return "WARN", "Recommended to add explicit T1-T4 translational stage and avoidable mortality impact", 4

def run_protocol_validation(filepath: str, strict: bool = False) -> int:
    if not os.path.exists(filepath):
        print(f"{Colors.RED}Error: File not found: {filepath}{Colors.RESET}")
        return 1
        
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    print(f"\n{Colors.BOLD}{Colors.BLUE}========================================================================{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}   GP3 / CTM MEDICAL PROTOCOL COMPLIANCE LINTER   {Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}========================================================================{Colors.RESET}")
    print(f"Target File: {Colors.BOLD}{filepath}{Colors.RESET}")
    print(f"File Size:   {len(content):,} characters | {len(content.splitlines())} lines\n")
    
    gates = [
        ("Gate 1: PICO Title Formula", check_title_formula(content), True),
        ("Gate 2: The Suffering Narrative", check_suffering_narrative(content), True),
        ("Gate 3: 6-Point Quantitative Background", check_background_completeness(content), False),
        ("Gate 4: Search Key Syntax (No NOT)", check_search_syntax(content), True),
        ("Gate 5: Feasibility Poolability Gate", check_poolability_rule(content), True),
        ("Gate 6: Methodological Quality & RoB", check_methodological_rigor(content), False),
        ("Gate 7: Translational Pipeline & Impact", check_translational_stage(content), False),
    ]
    
    total_score = 0
    max_score = 100  # 15*6 + 10 = 100
    critical_failure = False
    
    print(f"{Colors.BOLD}{'Gate':<42} | {'Status':<6} | {'Details'}{Colors.RESET}")
    print("-" * 85)
    
    for name, (status, details, pts), is_critical in gates:
        score_val = pts
        if status == "PASS":
            status_color = f"{Colors.GREEN}PASS{Colors.RESET}"
        elif status == "WARN":
            status_color = f"{Colors.YELLOW}WARN{Colors.RESET}"
        else:
            status_color = f"{Colors.RED}FAIL{Colors.RESET}"
            if is_critical:
                critical_failure = True
                
        total_score += score_val
        print(f"{name:<42} | {status_color:<15} | {details}")
        
    print("-" * 85)
    
    # Score Summary
    score_color = Colors.GREEN if total_score >= 80 else (Colors.YELLOW if total_score >= 60 else Colors.RED)
    print(f"\n{Colors.BOLD}Overall Compliance Score: {score_color}{total_score} / {max_score} ({total_score}%){Colors.RESET}")
    
    if critical_failure:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ PROTOCOL VERDICT: REJECTED BY MENTOR GATES{Colors.RESET}")
        print(f"{Colors.RED}One or more CRITICAL GP3 gates failed. You must address the red gates before committee review.{Colors.RESET}")
        return 1
    elif strict and total_score < 90:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ PROTOCOL VERDICT: STRICT MODE REVISION NEEDED (<90%){Colors.RESET}")
        return 1
    elif total_score >= 75:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ PROTOCOL VERDICT: APPROVED FOR DEFENSE / REGISTRATION{Colors.RESET}")
        print(f"{Colors.GREEN}Meets Translational Medicine rigor and mentor poolability criteria.{Colors.RESET}")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ PROTOCOL VERDICT: REVISION RECOMMENDED (<75%){Colors.RESET}")
        return 1

def main():
    parser = argparse.ArgumentParser(description="Audit research protocols against GP3 / CTM standards.")
    parser.add_argument("file", help="Path to markdown protocol file (e.g. PROTOCOL.md)")
    parser.add_argument("--strict", action="store_true", help="Enforce strict 90%%+ score threshold")
    args = parser.parse_args()
    
    sys.exit(run_protocol_validation(args.file, strict=args.strict))

if __name__ == "__main__":
    main()
