#!/usr/bin/env python3
"""
test_template_prompt_generator.py — Unit and Integration Tests for GP3 Template Prompt Generator
================================================================================================
Kanonikus szempontok:
- ExtractionTemplateParser struktúra validáció
- PlausibilityManager határérték ellenőrzés
- TemplatePromptGenerator prompt építés és séma integritás
- ExtractionResponseValidator: BoostR Gate 1 (numeric-only) és plauzitási határok
- Extraction Assistant integráció (--generate-prompt és --ingest-extraction)
"""

import os
import sys
import json
import unittest
import tempfile
import shutil

# Add project root and src to PATH
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)
src_dir = os.path.join(WORKSPACE_DIR, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from template_prompt_generator import (
    ExtractionTemplateParser,
    PlausibilityManager,
    TemplatePromptGenerator,
    ExtractionResponseValidator,
    COLOR_CATEGORIES
)
import extraction_assistant


class TestTemplateParser(unittest.TestCase):
    """Excel template olvasásának és mező-feltérképezésének tesztjei."""

    @classmethod
    def setUpClass(cls):
        cls.template_path = os.path.join(WORKSPACE_DIR, "data", "wiki", "templates", "Data_extraction_template_v9.xlsx")
        cls.parser = ExtractionTemplateParser(cls.template_path)
        cls.parsed = cls.parser.parse(["Basic layout", "ORs - RRs", "Regression coefficient", "QUIPS"])

    def test_sheets_loaded(self):
        self.assertIn("Basic layout", self.parsed)
        self.assertIn("ORs - RRs", self.parsed)
        self.assertIn("Regression coefficient", self.parsed)
        self.assertIn("QUIPS", self.parsed)

    def test_basic_layout_fields(self):
        fields = self.parsed["Basic layout"]
        self.assertGreater(len(fields), 20)
        labels = [f["label"] for f in fields]
        self.assertIn("First Author", labels)
        self.assertIn("Year of publication", labels)
        self.assertIn("Mean", labels)
        self.assertIn("SD", labels)

    def test_ors_rrs_fields(self):
        fields = self.parsed["ORs - RRs"]
        self.assertGreater(len(fields), 10)
        categories = {f["category"] for f in fields}
        self.assertIn("OUTCOME_EVENTS", categories)
        self.assertIn("STAT_EFFECT_ESTIMATE", categories)

    def test_category_assignment(self):
        fields = self.parsed["Basic layout"]
        pop_fields = [f for f in fields if f["category"] == "POPULATION_DEMO"]
        int_fields = [f for f in fields if f["category"] == "INTERVENTION_EXPOSURE"]
        self.assertGreater(len(pop_fields), 0)
        self.assertGreater(len(int_fields), 0)


class TestPlausibilityManager(unittest.TestCase):
    """Fiziológiai határértékek ellenőrzése."""

    def setUp(self):
        self.pm = PlausibilityManager("meta_hyperglycaemia")

    def test_load_ranges(self):
        self.assertIn("gestational_age_weeks", self.pm.ranges)
        self.assertIn("birth_weight_g", self.pm.ranges)
        self.assertIn("blood_glucose_mg_dl", self.pm.ranges)

    def test_valid_gestational_age(self):
        is_valid, msg = self.pm.validate_value("gestational_age_weeks", 38.6)
        self.assertTrue(is_valid)
        self.assertIsNone(msg)

    def test_out_of_bounds_gestational_age(self):
        is_valid, msg = self.pm.validate_value("gestational_age_weeks", 15.0)
        self.assertFalse(is_valid)
        self.assertIn("fiziológiai határon kívül esik", msg)

    def test_valid_birth_weight(self):
        is_valid, msg = self.pm.validate_value("birth_weight_g", 3320.0)
        self.assertTrue(is_valid)

    def test_out_of_bounds_birth_weight(self):
        is_valid, msg = self.pm.validate_value("birth_weight_g", 150.0)  # absurdly low
        self.assertFalse(is_valid)


class TestPromptGenerator(unittest.TestCase):
    """Prompt összeállítás és séma generálás tesztjei."""

    def setUp(self):
        self.gen = TemplatePromptGenerator(
            project="meta_hyperglycaemia",
            study_id="Ali_2024",
            selected_sheets=["Basic layout", "ORs - RRs"]
        )

    def test_system_instruction_contains_core_directives(self):
        sys_inst = self.gen.generate_system_instruction()
        self.assertIn("ZERO-FLATTERY", sys_inst)
        self.assertIn("VERBATIM SOURCING", sys_inst)
        self.assertIn("CTM BOOSTR NUMERIC-ONLY", sys_inst)
        self.assertIn("WAN / HIGGINS", sys_inst)

    def test_user_prompt_contains_fields(self):
        user_prompt = self.gen.generate_user_prompt("Sample paper text for Ali 2024")
        self.assertIn("Ali_2024", user_prompt)
        self.assertIn("Basic layout", user_prompt)
        self.assertIn("ORs - RRs", user_prompt)
        self.assertIn("Strict JSON Output Schema", user_prompt)
        self.assertIn("Sample paper text for Ali 2024", user_prompt)

    def test_save_prompt_markdown(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_p = os.path.join(tmpdir, "test_prompt.md")
            saved = self.gen.save_prompt_markdown(out_p, "Article text...")
            self.assertTrue(os.path.exists(saved))
            with open(saved, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("GP3 Extraction Prompt: Ali_2024", content)
            self.assertIn("Article text...", content)


class TestExtractionResponseValidator(unittest.TestCase):
    """LLM válasz validálása és konverziója."""

    def setUp(self):
        self.validator = ExtractionResponseValidator("meta_hyperglycaemia")

    def test_valid_extraction_payload(self):
        payload = {
            "study_id": "Ali_2024",
            "project": "meta_hyperglycaemia",
            "extractions": [
                {
                    "field_key": "basic_layout.col_10_mean",
                    "variable_name": "Gestational age (weeks)",
                    "category": "POPULATION_DEMO",
                    "value": 38.6,
                    "unit": "weeks",
                    "is_numeric": True,
                    "verbatim_quote": "Gestational age (weeks), mean±SD  38.6 ± 1.4",
                    "location": "Page 1, Table 1 (Row 1)",
                    "page": 1,
                    "confidence": "HIGH"
                },
                {
                    "field_key": "ors_rrs.col_13_events_i",
                    "variable_name": "Unfavorable NDO at 24 Months",
                    "category": "OUTCOME_EVENTS",
                    "value": 22,
                    "unit": "patients",
                    "is_numeric": True,
                    "verbatim_quote": "Unfavorable NDO at 24 months     22 (39.3%)",
                    "location": "Page 2, Table 2 (Row 2)",
                    "page": 2,
                    "confidence": "HIGH"
                }
            ]
        }
        res = self.validator.validate(payload)
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["summary_stats"]["total_extracted"], 2)
        self.assertEqual(res["summary_stats"]["high_confidence"], 2)
        self.assertEqual(len(res["highlights"]), 2)

    def test_numeric_only_fatal_error(self):
        payload = {
            "study_id": "Ali_2024",
            "extractions": [
                {
                    "field_key": "basic_layout.col_10_mean",
                    "variable_name": "Gestational age",
                    "is_numeric": True,
                    "value": "approx 38.6 weeks",  # FORBIDDEN TEXT IN NUMERIC CELL
                    "verbatim_quote": "approx 38.6 weeks",
                    "confidence": "HIGH"
                }
            ]
        }
        res = self.validator.validate(payload)
        self.assertFalse(res["is_valid"])
        self.assertGreater(len(res["fatal_errors"]), 0)
        self.assertIn("BoostR Gate 1 hiba", res["fatal_errors"][0])

    def test_out_of_bounds_plausibility_warning_and_downgrade(self):
        payload = {
            "study_id": "Ali_2024",
            "extractions": [
                {
                    "field_key": "basic_layout.col_10_mean",
                    "variable_name": "Gestational age (weeks)",
                    "category": "POPULATION_DEMO",
                    "value": 15.0,  # Below minimum 22 weeks
                    "unit": "weeks",
                    "is_numeric": True,
                    "verbatim_quote": "Gestational age was 15.0 weeks",
                    "location": "Page 1, Table 1",
                    "confidence": "HIGH"
                }
            ]
        }
        res = self.validator.validate(payload)
        # Should be valid JSON, but downgraded to LOW confidence and flagged as ambiguous
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["summary_stats"]["low_confidence"], 1)
        h = res["highlights"][0]
        self.assertEqual(h["confidence"], "LOW")
        self.assertEqual(h["category"], "AMBIGUOUS_UNCONFIRMED")
        self.assertIn("fiziológiai határon kívül esik", h["notes"])

    def test_export_highlights_json(self):
        payload = {
            "study_id": "Ali_2024",
            "extractions": [
                {
                    "field_key": "basic_layout.col_10_mean",
                    "variable_name": "Gestational age (weeks)",
                    "value": 38.6,
                    "is_numeric": True,
                    "verbatim_quote": "38.6 ± 1.4",
                    "confidence": "HIGH"
                }
            ]
        }
        res = self.validator.validate(payload)
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "highlights.json")
            saved = self.validator.export_highlights_json(res, out_file)
            self.assertTrue(os.path.exists(saved))
            with open(saved, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["variable_name"], "Gestational age (weeks)")


class TestAssistantIntegration(unittest.TestCase):
    """Extraction Assistant parancssori és modulintegrációs tesztek."""

    def test_generate_prompt_cli_integration(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_file = os.path.join(tmpdir, "cli_prompt.md")
            gen = TemplatePromptGenerator("meta_hyperglycaemia", "Ali_2024")
            gen.save_prompt_markdown(prompt_file, "Test content")
            self.assertTrue(os.path.exists(prompt_file))

    def test_ingest_extraction_highlight_run(self):
        # Create a valid extraction JSON and ingest it into extraction_assistant pipeline
        with tempfile.TemporaryDirectory() as tmpdir:
            ingest_json = os.path.join(tmpdir, "Ali_2024_extraction.json")
            valid_payload = {
                "study_id": "Ali_2024",
                "project": "meta_hyperglycaemia",
                "extractions": [
                    {
                        "field_key": "basic_layout.col_10_mean",
                        "variable_name": "Gestational age (weeks)",
                        "category": "POPULATION_DEMO",
                        "value": 38.6,
                        "unit": "weeks",
                        "is_numeric": True,
                        "verbatim_quote": "Gestational age (weeks), mean±SD  38.6 ± 1.4",
                        "location": "Page 1, Table 1 (Row 1)",
                        "page": 1,
                        "confidence": "HIGH"
                    },
                    {
                        "field_key": "basic_layout.col_18_n0_of_patients",
                        "variable_name": "Total Cohort Sample Size (N)",
                        "category": "POPULATION_DEMO",
                        "value": 153,
                        "unit": "patients",
                        "is_numeric": True,
                        "verbatim_quote": "Characteristic                   Total (N=153)",
                        "location": "Page 1, Table 1 Header",
                        "page": 1,
                        "confidence": "HIGH"
                    }
                ]
            }
            with open(ingest_json, "w", encoding="utf-8") as f:
                json.dump(valid_payload, f, indent=2)

            # Test run_highlight_pipeline with auto_resolve=True and ingest_file
            # In test environment, let's ensure it runs without throwing exception
            try:
                extraction_assistant.run_highlight_pipeline(
                    study_id="Ali_2024",
                    project="meta_hyperglycaemia",
                    interactive=False,
                    auto_resolve=True,
                    ingest_file=ingest_json
                )
                success = True
            except Exception as e:
                success = False
                print(f"Exception during run_highlight_pipeline: {e}")
            self.assertTrue(success)


if __name__ == "__main__":
    unittest.main()
