#!/usr/bin/env python3
"""
template_prompt_generator.py — GP3 CTM BoostR Template-Based Prompt Generator
=============================================================================
Kanonikus Módszertani Alapok:
- CTM Data Extraction Template v9 (14 standardizált munkalap)
- AGENTS.md §3.4 Rule 6: Full-Text AI Extraction Mandate & Blind Automation Ban
- AGENTS.md §5.9: Slow & Steady metodika
- GEMINI.md Rule 10: Verbatim Sourcing Mandate (P0) & Zero-Flattery Skepticism
- CTM BoostR Adattisztítási Standard (Numeric-only, Wan/Higgins konverzió)

Funkciók:
1. ExtractionTemplateParser:
   - Beolvassa a Data_extraction_template_v9.xlsx munkalapjait.
   - Feltérképezi a hierarchikus fejléceket (Domain -> Group -> Variable -> Sub-measure).
   - Típus- és kategóriabesorolást végez a CTM BoostR 6+1 szemantikai színrendszer szerint:
       POPULATION_DEMO, INTERVENTION_EXPOSURE, COMPARATOR_CONTROL,
       OUTCOME_EVENTS, STAT_EFFECT_ESTIMATE, ROB_ATTRITION, AMBIGUOUS_UNCONFIRMED.
2. PlausibilityManager:
   - Betölti a data/wiki/<project>/plausibility_ranges.json fájlt.
   - Hozzárendeli a fiziológiai határértékeket (min, max, unit) a mezőkhöz.
3. TemplatePromptGenerator:
   - Determinisztikusan legenerálja a strukturált Gemini / LLM promptot.
   - Kikényszeríti a Verbatim Sourcing mandátumot és a szigorú JSON sémát.
   - Beépíti a Wan/Higgins medián-szabályt és a numerikus integritást.
4. ExtractionResponseValidator:
   - Validálja a modell által adott JSON választ.
   - Kiszűri a tiltott szöveges értékeket numerikus mezőkben (BoostR Gate 1).
   - Ellenőrzi a fiziológiai határokat és a matematikai konzisztenciát (2x2 tábla).
   - Előállítja az extraction_assistant.py kompatibilis `highlights` listát
     és a Markdown dosszié Section 8: Provenance Log táblázatát.
"""

import os
import sys
import json
import re
import argparse
from typing import Dict, List, Any, Optional, Tuple, Set

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from src.utils.console import configure_utf8_console
configure_utf8_console()

# 6+1 CTM BoostR Szemantikai Színpaletta és kategóriák
COLOR_CATEGORIES = {
    "POPULATION_DEMO": {
        "hex": "#FFF275",
        "name": "Sárga (Populáció & Demográfia)",
        "badge": "🟡 POPULATION (P)"
    },
    "INTERVENTION_EXPOSURE": {
        "hex": "#70E496",
        "name": "Zöld (Expozíció / Intervenció)",
        "badge": "🟢 INTERVENTION (I/E)"
    },
    "COMPARATOR_CONTROL": {
        "hex": "#D4B2D8",
        "name": "Lila (Komparátor / Kontroll)",
        "badge": "🟣 COMPARATOR (C)"
    },
    "OUTCOME_EVENTS": {
        "hex": "#7BDFF2",
        "name": "Kék (Kimenetelek: n/N/%)",
        "badge": "🔵 OUTCOME (O)"
    },
    "STAT_EFFECT_ESTIMATE": {
        "hex": "#FFB085",
        "name": "Narancs (Statisztikai Hatásbecslés)",
        "badge": "🟠 STATISTIC (aOR/CI)"
    },
    "ROB_ATTRITION": {
        "hex": "#FF7B7B",
        "name": "Piros (RoB & Lemorzsolódás)",
        "badge": "🔴 ROB / ATTRITION"
    },
    "AMBIGUOUS_UNCONFIRMED": {
        "hex": "#B0BEC5",
        "name": "Szürke (Bizonytalan / Kétértelmű)",
        "badge": "⚪ AMBIGUOUS / CONFLICT ⚠️"
    }
}

# Forbidden text placeholders in BoostR numeric fields
FORBIDDEN_NUMERIC_STRINGS = {
    "n/a", "na", "-", "--", "nil", "missing", "nr", "not reported",
    "none", "unknown", "nem ismert", "tbd", "nd", "not done", "null"
}


# ==============================================================================
# 1. TEMPLATE PARSER (Data_extraction_template_v9.xlsx)
# ==============================================================================

class ExtractionTemplateParser:
    """CTM Data Extraction Template v9 Excel munkalapjait és oszlopszerkezetét feldolgozó modul."""

    def __init__(self, template_path: Optional[str] = None):
        if not template_path:
            template_path = os.path.join(WORKSPACE_DIR, "data", "wiki", "templates", "Data_extraction_template_v9.xlsx")
        self.template_path = template_path
        self._parsed_sheets: Dict[str, List[Dict[str, Any]]] = {}

    def parse(self, selected_sheets: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Beolvassa az Excel sablont és kinyeri az oszlopdefiníciókat."""
        try:
            import openpyxl
        except ImportError:
            raise RuntimeError("openpyxl csomag szükséges az Excel sablon olvasásához!")

        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"Extraction template nem található: {self.template_path}")

        wb = openpyxl.load_workbook(self.template_path, data_only=True)
        sheets_to_process = selected_sheets or [
            "Basic layout",
            "ORs - RRs",
            "Mean Difference",
            "Regression coefficient",
            "QUIPS",
            "RoB2",
            "ROBINS"
        ]

        result = {}
        for sname in sheets_to_process:
            if sname in wb.sheetnames:
                ws = wb[sname]
                fields = self._parse_sheet_structure(sname, ws)
                if fields:
                    result[sname] = fields

        wb.close()
        self._parsed_sheets = result
        return result

    def _parse_sheet_structure(self, sheet_name: str, ws) -> List[Dict[str, Any]]:
        fields = []

        if sheet_name == "Basic layout":
            fields.extend(self._parse_basic_layout(ws))
        elif sheet_name == "ORs - RRs":
            fields.extend(self._parse_ors_rrs(ws))
        elif sheet_name == "Mean Difference":
            fields.extend(self._parse_mean_difference(ws))
        elif sheet_name == "Regression coefficient":
            fields.extend(self._parse_regression_coeff(ws))
        elif sheet_name in ("RoB2", "QUIPS", "ROBINS", "Joanna-Briggs", "QUADAS"):
            fields.extend(self._parse_rob_sheet(sheet_name, ws))
        else:
            fields.extend(self._parse_generic_sheet(sheet_name, ws))

        return fields

    def _parse_basic_layout(self, ws) -> List[Dict[str, Any]]:
        fields = []
        curr_r1 = ""
        curr_r2 = ""
        for c in range(1, ws.max_column + 1):
            v1 = ws.cell(1, c).value
            if v1:
                curr_r1 = str(v1).strip()
            v2 = ws.cell(2, c).value
            if v2:
                curr_r2 = str(v2).strip()
            v3 = ws.cell(3, c).value
            leaf = str(v3).strip() if v3 else ""
            if not leaf or leaf.startswith("<") or leaf == "etc":
                continue

            # Determine category and data type
            full_header = f"{curr_r1} - {curr_r2} - {leaf}".strip(" -")
            category = "POPULATION_DEMO"
            if "Intervention" in curr_r1 or "Intervention" in curr_r2:
                category = "INTERVENTION_EXPOSURE"
            elif "Comparator" in curr_r1 or "Control" in curr_r1 or "Comparator" in curr_r2:
                category = "COMPARATOR_CONTROL"

            is_numeric = any(k in leaf.lower() for k in [
                "mean", "sd", "median", "iqr", "range", "number", "n0", "total", "centers", "year", "%"
            ])
            data_type = "numeric" if is_numeric else "string"

            # Match plausibility key
            plaus_key = None
            leaf_lower = leaf.lower()
            if "age" in curr_r2.lower() or "age" in leaf_lower:
                plaus_key = "gestational_age_weeks"
            elif "weight" in leaf_lower:
                plaus_key = "birth_weight_g"
            elif "sex" in leaf_lower or "female" in leaf_lower or "male" in leaf_lower:
                plaus_key = "male_percentage"

            fields.append({
                "field_key": f"basic_layout.col_{c}_{self._slugify(leaf)}",
                "sheet": "Basic layout",
                "col_idx": c,
                "group": curr_r1,
                "subgroup": curr_r2,
                "label": leaf,
                "full_path": full_header,
                "category": category,
                "data_type": data_type,
                "plausibility_key": plaus_key,
                "description": f"Baseline demográfiai vagy beavatkozási mező: {full_header}"
            })
        return fields

    def _parse_ors_rrs(self, ws) -> List[Dict[str, Any]]:
        fields = []
        curr_r2 = ""
        for c in range(1, ws.max_column + 1):
            v2 = ws.cell(2, c).value
            if v2:
                curr_r2 = str(v2).strip()
            v3 = ws.cell(3, c).value
            leaf = str(v3).strip() if v3 else ""
            if not leaf or "<insert" in leaf:
                continue

            full_header = f"{curr_r2} - {leaf}".strip(" -")
            category = "OUTCOME_EVENTS"
            if "Precalculated" in curr_r2 or "adjusted" in curr_r2.lower():
                category = "STAT_EFFECT_ESTIMATE"
            elif "Intervention" in curr_r2:
                category = "INTERVENTION_EXPOSURE"
            elif "Comparator" in curr_r2:
                category = "COMPARATOR_CONTROL"

            is_num = any(k in leaf.lower() for k in [
                "n0", "total", "percentage", "point", "error", "ci", "or", "se", "mean", "median", "sd"
            ])

            plaus_key = None
            if "percentage" in leaf.lower():
                plaus_key = "mortality_percentage"

            fields.append({
                "field_key": f"ors_rrs.col_{c}_{self._slugify(leaf)}",
                "sheet": "ORs - RRs",
                "col_idx": c,
                "group": curr_r2 or "Outcome Details",
                "subgroup": "",
                "label": leaf,
                "full_path": full_header,
                "category": category,
                "data_type": "numeric" if is_num else "string",
                "plausibility_key": plaus_key,
                "description": f"Dichotomous outcome mező: {full_header}"
            })
        return fields

    def _parse_mean_difference(self, ws) -> List[Dict[str, Any]]:
        fields = []
        curr_r2 = ""
        for c in range(1, ws.max_column + 1):
            v2 = ws.cell(2, c).value
            if v2:
                curr_r2 = str(v2).strip()
            v3 = ws.cell(3, c).value
            leaf = str(v3).strip() if v3 else ""
            if not leaf or "<insert" in leaf:
                continue

            full_header = f"{curr_r2} - {leaf}".strip(" -")
            category = "OUTCOME_EVENTS"
            if "Precalculated" in curr_r2 or "Difference" in curr_r2:
                category = "STAT_EFFECT_ESTIMATE"
            elif "Intervention" in curr_r2:
                category = "INTERVENTION_EXPOSURE"
            elif "Control" in curr_r2:
                category = "COMPARATOR_CONTROL"

            is_num = any(k in leaf.lower() for k in [
                "n0", "mean", "deviation", "error", "interval", "median", "iqr", "range", "value"
            ])

            fields.append({
                "field_key": f"mean_difference.col_{c}_{self._slugify(leaf)}",
                "sheet": "Mean Difference",
                "col_idx": c,
                "group": curr_r2 or "Continuous Outcome",
                "subgroup": "",
                "label": leaf,
                "full_path": full_header,
                "category": category,
                "data_type": "numeric" if is_num else "string",
                "plausibility_key": None,
                "description": f"Continuous endpoint mező: {full_header}"
            })
        return fields

    def _parse_regression_coeff(self, ws) -> List[Dict[str, Any]]:
        fields = []
        for c in range(1, ws.max_column + 1):
            v2 = ws.cell(2, c).value
            leaf = str(v2).strip() if v2 else ""
            if not leaf:
                continue

            is_num = any(k in leaf.lower() for k in ["coefficient", "deviation", "error", "min", "max"])
            fields.append({
                "field_key": f"regression.col_{c}_{self._slugify(leaf)}",
                "sheet": "Regression coefficient",
                "col_idx": c,
                "group": "Regression coefficient",
                "subgroup": "",
                "label": leaf,
                "full_path": leaf,
                "category": "STAT_EFFECT_ESTIMATE",
                "data_type": "numeric" if is_num else "string",
                "plausibility_key": None,
                "description": f"Multivariábilis regressziós becslés: {leaf}"
            })
        return fields

    def _parse_rob_sheet(self, sheet_name: str, ws) -> List[Dict[str, Any]]:
        fields = []
        for c in range(1, ws.max_column + 1):
            v1 = ws.cell(1, c).value
            leaf = str(v1).strip() if v1 else ""
            if not leaf or "Study ID" in leaf:
                continue

            fields.append({
                "field_key": f"{self._slugify(sheet_name)}.col_{c}_{self._slugify(leaf[:30])}",
                "sheet": sheet_name,
                "col_idx": c,
                "group": sheet_name,
                "subgroup": "Critical Appraisal Domain",
                "label": leaf,
                "full_path": f"{sheet_name} - {leaf}",
                "category": "ROB_ATTRITION",
                "data_type": "rob_judgment",
                "plausibility_key": None,
                "description": f"Risk of Bias domén ({sheet_name}): {leaf}"
            })
        return fields

    def _parse_generic_sheet(self, sheet_name: str, ws) -> List[Dict[str, Any]]:
        fields = []
        for c in range(1, min(ws.max_column + 1, 20)):
            v = ws.cell(1, c).value or ws.cell(2, c).value or ws.cell(3, c).value
            if v:
                leaf = str(v).strip()
                fields.append({
                    "field_key": f"{self._slugify(sheet_name)}.col_{c}_{self._slugify(leaf[:25])}",
                    "sheet": sheet_name,
                    "col_idx": c,
                    "group": sheet_name,
                    "subgroup": "",
                    "label": leaf,
                    "full_path": f"{sheet_name} - {leaf}",
                    "category": "POPULATION_DEMO",
                    "data_type": "string",
                    "plausibility_key": None,
                    "description": f"{sheet_name}: {leaf}"
                })
        return fields

    @staticmethod
    def _slugify(text: str) -> str:
        s = re.sub(r"[^\w\s-]", "", text).strip().lower()
        return re.sub(r"[-\s]+", "_", s)


# ==============================================================================
# 2. PLAUSIBILITY MANAGER
# ==============================================================================

class PlausibilityManager:
    """Fiziológiai és klinikai határértékek betöltése és validációja."""

    def __init__(self, project: str = "meta_hyperglycaemia"):
        self.project = project
        self.ranges = self._load_ranges()

    def _load_ranges(self) -> Dict[str, Dict[str, Any]]:
        project_file = os.path.join(WORKSPACE_DIR, "data", "wiki", self.project, "plausibility_ranges.json")
        template_file = os.path.join(WORKSPACE_DIR, "data", "wiki", "templates", "plausibility_ranges.template.json")

        if os.path.exists(project_file):
            try:
                with open(project_file, "r", encoding="utf-8") as f:
                    return json.load(f).get("ranges", {})
            except Exception as e:
                print(f"⚠️ Hiba a projekt plauzitási fájl olvasásakor: {e}", file=sys.stderr)

        if os.path.exists(template_file):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    return json.load(f).get("ranges", {})
            except (OSError, json.JSONDecodeError):
                pass

        return {}

    def get_range(self, key: Optional[str]) -> Optional[Dict[str, Any]]:
        if not key:
            return None
        return self.ranges.get(key)

    def validate_value(self, key: str, value: float) -> Tuple[bool, Optional[str]]:
        """Ellenőrzi, hogy egy számérték a fiziológiai határokon belül van-e."""
        cfg = self.ranges.get(key)
        if not cfg:
            return True, None

        min_val = cfg.get("min", float("-inf"))
        max_val = cfg.get("max", float("inf"))
        unit = cfg.get("unit", "")
        label = cfg.get("label", key)

        if value < min_val or value > max_val:
            return False, f"[{label}] Érték ({value} {unit}) fiziológiai határon kívül esik: [{min_val} - {max_val} {unit}]"
        return True, None


# ==============================================================================
# 3. TEMPLATE PROMPT GENERATOR
# ==============================================================================

class TemplatePromptGenerator:
    """
    Template-alapú Gemini / LLM Prompt Generátor.
    Összekapcsolja a CTM Excel sablont, a plauzitási határokat és a cikk szövegét.
    """

    def __init__(
        self,
        project: str,
        study_id: str,
        template_path: Optional[str] = None,
        selected_sheets: Optional[List[str]] = None
    ):
        self.project = project
        self.study_id = study_id
        self.parser = ExtractionTemplateParser(template_path)
        self.plausibility = PlausibilityManager(project)
        self.selected_sheets = selected_sheets or ["Basic layout", "ORs - RRs", "Regression coefficient", "QUIPS"]
        self.parsed_template = self.parser.parse(self.selected_sheets)

    def generate_system_instruction(self) -> str:
        """Kanonikus orvosi szisztematikus áttekintő és biostatisztikus instrukció."""
        return """\
You are the **GP3 Canonical Extraction Engine** — an uncompromising Senior Clinical Trialist, Methodologist, and Biostatistician operating strictly under:
- **Centre for Translational Medicine (CTM) Standard Guidelines**
- **Cochrane Handbook for Systematic Reviews of Interventions (v6.5)**
- **PRISMA 2020 & PRISMA-trAIce Reporting Standards**
- **AGENTS.md §3.4 Rule 6 (Verbatim Sourcing Mandate & Blind Automation Ban)**
- **GEMINI.md Rule 10 (Full-Text AI Extraction Protocol)**

### NON-NEGOTIABLE CORE DIRECTIVES:

1. ⛔ **ZERO-FLATTERY & ADVERSARIAL SKEPTICISM (P0 Mandate):**
   - You must never flatter, praise, or accept ambiguous figures uncritically.
   - Your primary duty is to protect patient safety and meta-analytic validity by finding every discrepancy, reporting error, unit ambiguity, or missing denominator in primary articles.

2. 📜 **VERBATIM SOURCING & PROVENANCE MANDATE (P0 Mandate):**
   - For **EVERY SINGLE EXTRACTED VALUE** (numeric or categorical), you MUST provide:
     * `verbatim_quote`: The exact, word-for-word string as it appears in the primary text or table.
     * `location`: Precise location (Page number, Section, Table/Figure number, Row, Column, Footnote).
     * `confidence`: "HIGH" or "LOW".
     * If confidence is "LOW", you must declare the exact ambiguity type and formulate the Socratic resolution question.
   - Any extracted number without verbatim evidence is considered an unverified hallucination and will be rejected.

3. 🔢 **CTM BOOSTR NUMERIC-ONLY MANDATE (BoostR Gate 1):**
   - Numerical columns (n, N, mean, SD, median, IQR, OR, CI) must contain **ONLY real numbers** (float or int).
   - NEVER return strings, text placeholders, ranges, or combined numbers in numerical fields.
   - FORBIDDEN in numeric fields: "N/A", "NR", "not reported", "approx 12", "p<0.05", "10-15", "38.6 (1.4)".
   - If a numeric value was not reported in the article, set `value` to `null` and state "Not reported" in `notes`.
   - Separate range/bounds into distinct min/max fields.

4. 📊 **WAN / HIGGINS MEDIAN VS. MEAN RULE:**
   - Observational and neonatal cohorts frequently report skewed data as Median (IQR / Range).
   - Szigorúan TILOS mediánt átlagként (Mean) vagy IQR-t SD-ként elmenteni Wan/Higgins konverzió nélkül!
   - If the study reports Median and IQR, you must populate the `Median`, `IQR min`, `IQR max` fields, and leave `Mean` and `SD` as `null` (with note: "Requires Wan 2014 conversion").

5. ⚖️ **CRUDE VS. ADJUSTED EFFECT SIZES ISOLATION:**
   - NEVER mix crude 2x2 contingency estimates with multivariable adjusted estimates (aOR / aHR).
   - If multivariable regression is reported, extract the exact point estimate, 95% CI, and explicitly itemize EVERY covariate adjusted for.

6. 🔍 **DISCREPANCY DETECTION & AMBIGUITY QUARANTINE:**
   - If the article exhibits internal contradictions (e.g. Abstract states N=153, Table 1 sums to 150, or Table 2 mortality count differs from narrative text):
     * Do NOT arbitrarily pick one!
     * Flag as `AMBIGUOUS_UNCONFIRMED`.
     * Report both values, formulate a clarification question, and list the concrete options for the human reviewer.
"""

    def generate_user_prompt(
        self,
        full_text: str,
        study_metadata: Optional[Dict[str, Any]] = None,
        custom_instructions: Optional[str] = None
    ) -> str:
        """Legenerálja a tanulmány-specifikus felhasználói promptot a template mezői alapján."""
        meta = study_metadata or {}
        first_author = meta.get("first_author", self.study_id.split("_")[0])
        year = meta.get("year", self.study_id.split("_")[-1] if "_" in self.study_id else "")
        doi = meta.get("doi", "N/A")
        pmid = meta.get("pmid", "N/A")
        design = meta.get("study_design", "Clinical study")

        sections = []
        sections.append(f"# CTM Data Extraction Task for Study: {self.study_id}")
        sections.append(f"> **Project:** `{self.project}`  ")
        sections.append(f"> **Target Article:** {first_author} et al. ({year}) · DOI: `{doi}` · PMID: `{pmid}`  ")
        sections.append(f"> **Reported Design:** `{design}`  ")
        sections.append("")

        if custom_instructions:
            sections.append(f"### Specific Project Focus:\n{custom_instructions}\n")

        # 1. Field specifications derived from Excel template
        sections.append("## 📋 Extraction Schema & Field Specifications (from CTM Template v9)")
        sections.append("Carefully extract each of the following required variables from the full text provided below.\n")

        total_fields = 0
        for sheet_name, fields in self.parsed_template.items():
            sections.append(f"### Sheet: `{sheet_name}` ({len(fields)} fields)")
            sections.append("| Field Key | Group / Subgroup | Variable Label | Type | Category | Plausibility Range |")
            sections.append("|---|---|---|---|---|---|")

            for f in fields:
                total_fields += 1
                plaus_info = "—"
                plaus_cfg = self.plausibility.get_range(f.get("plausibility_key"))
                if plaus_cfg:
                    plaus_info = f"[{plaus_cfg.get('min')} - {plaus_cfg.get('max')} {plaus_cfg.get('unit')}]"

                f_type = f.get("data_type", "string")
                f_cat = f.get("category", "POPULATION_DEMO")
                badge = COLOR_CATEGORIES.get(f_cat, {}).get("badge", f_cat)

                sections.append(
                    f"| `{f['field_key']}` | {f.get('group', '')} {f.get('subgroup', '')} | "
                    f"**{f['label']}** | `{f_type}` | {badge} | {plaus_info} |"
                )
            sections.append("")

        # 2. JSON Response Format Specification
        sections.append("## 📤 Strict JSON Output Schema")
        sections.append("You MUST return ONLY valid JSON matching this exact structure. Do not wrap in conversational filler.\n")

        schema_example = {
            "study_id": self.study_id,
            "project": self.project,
            "metadata_extracted": {
                "first_author": first_author,
                "year": year,
                "doi": doi,
                "pmid": pmid,
                "study_design_identified": "...",
                "country": "...",
                "total_cohort_n": 0
            },
            "extractions": [
                {
                    "field_key": "basic_layout.col_10_mean",
                    "sheet": "Basic layout",
                    "variable_name": "Age / Gestational Age (Mean)",
                    "category": "POPULATION_DEMO",
                    "value": 38.6,
                    "unit": "weeks",
                    "is_numeric": True,
                    "verbatim_quote": "Gestational age (weeks), mean±SD  38.6 ± 1.4",
                    "location": "Page 1, Table 1 (Row 1, Column 'Total')",
                    "page": 1,
                    "confidence": "HIGH",
                    "ambiguity_type": None,
                    "ambiguity_details": None,
                    "notes": ""
                },
                {
                    "field_key": "ors_rrs.col_13_n0_of_patients_with_event_in_i",
                    "sheet": "ORs - RRs",
                    "variable_name": "Mortality in Intervention (Events count)",
                    "category": "OUTCOME_EVENTS",
                    "value": 12,
                    "unit": "patients",
                    "is_numeric": True,
                    "verbatim_quote": "Death before hospital discharge: 12 (21.4%)",
                    "location": "Page 2, Table 2 (Row 1)",
                    "page": 2,
                    "confidence": "LOW",
                    "ambiguity_type": "DISCREPANCY_CONFLICT",
                    "ambiguity_details": {
                        "question": "Table 2 lists 12 deaths in group I, but abstract narrative mentions 14 total deaths. Which count corresponds to primary endpoint?",
                        "options": ["12 (Per-protocol group I)", "14 (Overall reported deaths)"],
                        "default_option": "12"
                    },
                    "notes": "Internal contradiction between Table 2 and narrative text"
                }
            ],
            "discrepancies_and_ambiguities": [
                {
                    "variable_name": "...",
                    "conflict_description": "...",
                    "source_a": "...",
                    "source_b": "...",
                    "suggested_resolution": "..."
                }
            ],
            "risk_of_bias_summary": {
                "tool": "QUIPS / RoB2 / ROBINS",
                "overall_judgment": "Low / Moderate / High",
                "domains": [
                    {
                        "domain_name": "Study Participation",
                        "judgment": "Low",
                        "verbatim_evidence": "All consecutive infants meeting eligibility criteria were enrolled."
                    }
                ]
            }
        }
        sections.append("```json\n" + json.dumps(schema_example, indent=2, ensure_ascii=False) + "\n```\n")

        # 3. Source text
        sections.append("## 📄 Full-Text Article Content for Extraction")
        sections.append("```text\n" + full_text.strip() + "\n```")

        return "\n".join(sections)

    def generate_full_prompt(
        self,
        full_text: str,
        study_metadata: Optional[Dict[str, Any]] = None,
        custom_instructions: Optional[str] = None
    ) -> Dict[str, str]:
        """Előállítja mind a System Instruction-t, mind a User Prompt-ot."""
        return {
            "system_instruction": self.generate_system_instruction(),
            "user_prompt": self.generate_user_prompt(full_text, study_metadata, custom_instructions)
        }

    def save_prompt_markdown(
        self,
        output_path: str,
        full_text: str,
        study_metadata: Optional[Dict[str, Any]] = None,
        custom_instructions: Optional[str] = None
    ) -> str:
        """Elmenti a teljes promptot egy Markdown fájlba."""
        prompts = self.generate_full_prompt(full_text, study_metadata, custom_instructions)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        content = (
            f"# GP3 Extraction Prompt: {self.study_id}\n\n"
            f"## System Instruction\n\n{prompts['system_instruction']}\n\n"
            f"---\n\n## User Prompt\n\n{prompts['user_prompt']}\n"
        )
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path


# ==============================================================================
# 4. EXTRACTION RESPONSE VALIDATOR & ADAPTER
# ==============================================================================

class ExtractionResponseValidator:
    """
    Validálja a Gemini / LLM által visszaadott JSON kinyerési választ:
    1. CTM BoostR Gate 1 (Numeric-Only ellenőrzés)
    2. Plauzibilitási határok vizsgálata
    3. Verbatim sourcing és idézet-integritás auditja
    4. Átalakítás extraction_assistant.py `highlights` struktúrára
    """

    def __init__(self, project: str = "meta_hyperglycaemia"):
        self.project = project
        self.plausibility = PlausibilityManager(project)
        self.parser = ExtractionTemplateParser()

    def validate(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validálja a választ.
        Visszatér:
        {
            "is_valid": bool,
            "fatal_errors": List[str],
            "warnings": List[str],
            "highlights": List[Dict[str, Any]],
            "ambiguities": List[Dict[str, Any]],
            "summary_stats": Dict[str, int]
        }
        """
        fatal_errors = []
        warnings = []
        highlights = []
        ambiguities = []

        if not isinstance(response_data, dict):
            return {
                "is_valid": False,
                "fatal_errors": ["A modell válasza nem érvényes JSON dictionary!"],
                "warnings": [],
                "highlights": [],
                "ambiguities": [],
                "summary_stats": {}
            }

        extractions = response_data.get("extractions", [])
        if not extractions:
            warnings.append("Az 'extractions' lista üres a modell válaszában.")

        for idx, item in enumerate(extractions, 1):
            var_name = item.get("variable_name", f"Var_{idx}")
            val = item.get("value")
            is_num = item.get("is_numeric", False)
            quote = item.get("verbatim_quote", "")
            location = item.get("location", "")
            page = item.get("page", 1)
            cat = item.get("category", "POPULATION_DEMO")
            if cat not in COLOR_CATEGORIES:
                cat = "AMBIGUOUS_UNCONFIRMED"
            conf = item.get("confidence", "HIGH")

            # 1. Verbatim sourcing check
            if not quote or not str(quote).strip():
                warnings.append(f"[{var_name}] Hiányzik a szó szerinti idézet (verbatim quote)!")
                conf = "LOW"
                cat = "AMBIGUOUS_UNCONFIRMED"

            # 2. BoostR Numeric-Only Audit (Gate 1)
            num_val = None
            if is_num and val is not None:
                if isinstance(val, (int, float)):
                    num_val = float(val)
                elif isinstance(val, str):
                    val_clean = val.strip().lower()
                    if val_clean in FORBIDDEN_NUMERIC_STRINGS:
                        warnings.append(f"[{var_name}] Szöveges placeholder '{val}' numerikus mezőben (BoostR szerint null-nak kell lennie).")
                        item["value"] = None
                    else:
                        # Try parsing pure float
                        try:
                            # Handle comma decimal
                            parsed = float(val.replace(",", ".").replace(" ", ""))
                            num_val = parsed
                            item["value"] = parsed
                            warnings.append(f"[{var_name}] Stringként kapott számérték '{val}' konvertálva float-ra: {parsed}")
                        except ValueError:
                            fatal_errors.append(f"[{var_name}] BoostR Gate 1 hiba: Szöveg numerikus mezőben: '{val}'")
                            conf = "LOW"
                            cat = "AMBIGUOUS_UNCONFIRMED"

            # 3. Plausibility validation
            plaus_key = item.get("plausibility_key")
            # If not explicitly provided, try to infer from var_name (excluding dispersion metrics)
            v_lower = var_name.lower()
            is_dispersion = any(d in v_lower for d in [" sd", "sd ", "_sd", "(sd)", "standard deviation", " se", "se ", "standard error", "iqr", "diff"])
            if not plaus_key and not is_dispersion:
                if "gestational" in v_lower or "ga" in v_lower:
                    plaus_key = "gestational_age_weeks"
                elif "birth weight" in v_lower or "bw" in v_lower:
                    plaus_key = "birth_weight_g"
                elif "glucose" in v_lower:
                    plaus_key = "blood_glucose_mg_dl" if "mg" in v_lower else "blood_glucose_mmol_l"
                elif "temperature" in v_lower or "cooling" in v_lower:
                    plaus_key = "target_temperature_c"
                elif "mortality" in v_lower and "%" in v_lower:
                    plaus_key = "mortality_percentage"
                elif "male" in v_lower or "sex" in v_lower:
                    plaus_key = "male_percentage"

            if num_val is not None and plaus_key:
                is_p_valid, p_msg = self.plausibility.validate_value(plaus_key, num_val)
                if not is_p_valid:
                    warnings.append(p_msg)
                    conf = "LOW"
                    cat = "AMBIGUOUS_UNCONFIRMED"
                    item["notes"] = (item.get("notes", "") + " " + (p_msg or "")).strip()

            # 4. Construct highlight record for extraction_assistant.py
            h_record = {
                "variable_name": var_name,
                "category": cat,
                "search_span": quote or var_name,
                "extracted_value": str(val) if val is not None else "Not reported",
                "num_val": num_val,
                "ctm_field": item.get("field_key", f"col_{idx}"),
                "page": page,
                "location": location,
                "confidence": conf,
                "status": "AUTO_ACCEPTED" if conf == "HIGH" else "REQUIRES_VERIFICATION",
                "notes": item.get("notes", "")
            }

            # If ambiguous, extract question & options
            amb_details = item.get("ambiguity_details")
            if conf == "LOW" or cat == "AMBIGUOUS_UNCONFIRMED" or amb_details:
                h_record["confidence"] = "LOW"
                h_record["category"] = "AMBIGUOUS_UNCONFIRMED"
                h_record["status"] = "REQUIRES_VERIFICATION"
                h_record["ambiguity_type"] = item.get("ambiguity_type", "DATA_AMBIGUITY")
                if amb_details and isinstance(amb_details, dict):
                    h_record["question"] = amb_details.get("question", f"Megerősítendő érték: {var_name}")
                    h_record["options"] = amb_details.get("options", [str(val), "Kihagyás / Not reported"])
                    h_record["default_option"] = amb_details.get("default_option", str(val))
                    h_record["res_key"] = self.parser._slugify(var_name)
                else:
                    h_record["question"] = f"A(z) '{var_name}' kinyert értéke ({val}) ellenőrzést igényel. Elfogadod?"
                    h_record["options"] = [str(val), "Egyéni érték megadása", "Nem riportált"]
                    h_record["default_option"] = str(val)
                    h_record["res_key"] = self.parser._slugify(var_name)
                ambiguities.append(h_record)

            highlights.append(h_record)

        summary_stats = {
            "total_extracted": len(highlights),
            "high_confidence": sum(1 for h in highlights if h["confidence"] == "HIGH"),
            "low_confidence": sum(1 for h in highlights if h["confidence"] == "LOW"),
            "fatal_errors_count": len(fatal_errors),
            "warnings_count": len(warnings)
        }

        return {
            "is_valid": len(fatal_errors) == 0,
            "fatal_errors": fatal_errors,
            "warnings": warnings,
            "highlights": highlights,
            "ambiguities": ambiguities,
            "summary_stats": summary_stats
        }

    def export_highlights_json(self, validated_result: Dict[str, Any], output_path: str) -> str:
        """Elmenti a validált highlights struktúrát JSON fájlba."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(validated_result.get("highlights", []), f, indent=2, ensure_ascii=False)
        return output_path


# ==============================================================================
# 5. CLI INTERFACE
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="GP3 CTM BoostR Template-Based Extraction Prompt Generator & Validator"
    )
    parser.add_argument("--project", required=True, help="Projekt slug (pl. meta_hyperglycaemia)")
    parser.add_argument("--study", required=True, help="Tanulmány azonosító (pl. Ali_2024)")
    parser.add_argument("--template", default=None, help="CTM Excel sablon elérési útja")
    parser.add_argument("--sheets", default=None, help="Vesszővel elválasztott munkalap-nevek")
    parser.add_argument("--text-file", default=None, help="Cikk teljes szövegét tartalmazó fájl (.txt, .md)")
    parser.add_argument("--pdf-file", default=None, help="Cikk PDF fájlja szöveg kinyeréshez")
    parser.add_argument("--output-prompt", default=None, help="Mentési útvonal a generált prompthoz (.md)")
    parser.add_argument("--validate-response", default=None, help="Modell JSON válaszának validálása")
    parser.add_argument("--output-highlights", default=None, help="Validált highlights JSON mentési útvonala")
    args = parser.parse_args()

    selected_sheets = [s.strip() for s in args.sheets.split(",")] if args.sheets else None

    # MÓD 1: LLM válasz validálása
    if args.validate_response:
        print(f"\n🔍 LLM Válasz Validálása: {args.validate_response}")
        with open(args.validate_response, "r", encoding="utf-8") as f:
            data = json.load(f)
        validator = ExtractionResponseValidator(args.project)
        res = validator.validate(data)

        print("\n" + "═" * 60)
        print("  CTM BOOSTR EXTRACTION VALIDATION REPORT")
        print("═" * 60)
        print(f"  Státusz:           {'✅ SIKERES' if res['is_valid'] else '❌ VÉGZETES HIBÁK'}")
        print(f"  Kinyert tételek:   {res['summary_stats']['total_extracted']} db")
        print(f"  Magas konfidencia: {res['summary_stats']['high_confidence']} db")
        print(f"  Bizonytalan (LOW): {res['summary_stats']['low_confidence']} db")
        print(f"  Figyelmeztetések:  {res['summary_stats']['warnings_count']} db")
        print(f"  Végzetes hibák:    {res['summary_stats']['fatal_errors_count']} db")

        if res["fatal_errors"]:
            print("\n  ❌ Végzetes Hibák (BoostR megsértése):")
            for fe in res["fatal_errors"]:
                print(f"     • {fe}")

        if res["warnings"]:
            print("\n  ⚠️ Figyelmeztetések & Plauzitási Jelzések:")
            for w in res["warnings"][:10]:
                print(f"     • {w}")
            if len(res["warnings"]) > 10:
                print(f"     ... és további {len(res['warnings']) - 10} figyelmeztetés.")

        if args.output_highlights:
            out_p = validator.export_highlights_json(res, args.output_highlights)
            print(f"\n  💾 Highlights JSON elmentve: {out_p}")
        return

    # MÓD 2: Prompt generálás az Excel sablonból
    print(f"\n⚙️ CTM BoostR Template-Alapú Prompt Generálása...")
    print(f"   Projekt:   {args.project}")
    print(f"   Tanulmány: {args.study}")

    # Szövegforrás beolvasása
    full_text = ""
    if args.text_file and os.path.exists(args.text_file):
        with open(args.text_file, "r", encoding="utf-8", errors="replace") as f:
            full_text = f.read()
    elif args.pdf_file and os.path.exists(args.pdf_file):
        try:
            import pypdf
            reader = pypdf.PdfReader(args.pdf_file)
            pages_text = [p.extract_text() or "" for p in reader.pages]
            full_text = "\n\n--- PAGE BREAK ---\n\n".join(pages_text)
            print(f"   PDF beolvasva: {len(reader.pages)} oldal ({len(full_text)} karakter)")
        except Exception as e:
            print(f"   ⚠️ Hiba a PDF olvasásakor: {e}")

    if not full_text:
        full_text = f"[FULL-TEXT PLACEHOLDER FOR {args.study}: Illeszd be a cikk teljes szövegét vagy táblázatait ide]"

    generator = TemplatePromptGenerator(
        project=args.project,
        study_id=args.study,
        template_path=args.template,
        selected_sheets=selected_sheets
    )

    study_meta = {
        "first_author": args.study.split("_")[0],
        "year": args.study.split("_")[-1] if "_" in args.study else ""
    }

    if args.output_prompt:
        out_p = generator.save_prompt_markdown(args.output_prompt, full_text, study_meta)
        print(f"\n  ✅ Generált Prompt Sikeresen Elmentve:")
        print(f"     Elérési út: {out_p}")
    else:
        prompts = generator.generate_full_prompt(full_text, study_meta)
        print("\n" + "═" * 70)
        print("SYSTEM INSTRUCTION:")
        print("═" * 70)
        print(prompts["system_instruction"][:500] + "\n... [truncated] ...\n")
        print("═" * 70)
        print("USER PROMPT (részlet):")
        print("═" * 70)
        print(prompts["user_prompt"][:1200] + "\n... [truncated] ...\n")
        print("═" * 70)
        print(f"💡 Tipp: Használd a --output-prompt <path.md> kapcsolót a teljes prompt fájlba mentéséhez!")


if __name__ == "__main__":
    main()
