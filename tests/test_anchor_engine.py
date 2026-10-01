#!/usr/bin/env python3
"""
test_anchor_engine.py
=====================
Comprehensive Test Suite for GP3 Anchor Engine (Pillars 1 & 2).
Enforces:
  1. Positive Test: Perez Death -> Page 6, 29 (26.1), Precision Checksum PASS.
  2. Negative Test (Row Label): Parity query on Page 6 must fail loudly on Row Label.
  3. Neighbor Column Isolation: Euglycemia (18 [6.4]) vs Hyperglycemia (29 [26.1]).
  4. Mutation Tests:
     - Wrong N (e.g. 98 instead of 111) -> MathChecksumError
     - Typo in percent (21.6 instead of 26.1) -> MathChecksumError
     - Within derived precision tolerance -> PASS
  5. Fail-Loud Policy Tests:
     - Nonexistent column -> ColumnChannelNotFoundError
     - Nonexistent row -> RowNotFoundError
     - Empty clip -> EmptyCellError
  6. Regression Tests:
     - Perez 2023, Basu 2017, Parmentier 2022 match verified Excel values.
  7. Tamper-Evidence & Visual Verification Crop
  8. Large N Precision & Discriminative Window Tests (Section 1b & 1c):
     - N=1000 whole percent (d=0) discriminates=False, window=[495, 505]
     - Mutation inside window passes but discriminates=False
     - Mutation outside window raises MathChecksumError
  9. Boundary (Határeset) Precision Tests:
     - d=1 (tol=0.05%): delta=+0.049% PASS, delta=+0.051% MathChecksumError
     - d=0 (tol=0.5%):  delta=+0.499% PASS, delta=+0.501% MathChecksumError
  10. Synthetic Perez Parity Bug Isolation Test:
     - Identical 29 (26.1) values in Maternal parity and Death rows on same page
     - Death query isolates Death row bbox (y ~ 250)
     - Parity query isolates Parity row bbox (y ~ 150)
     - Duplicate identical row labels raise AmbiguousRowError
  11. Adjacent Column Identical Value Test:
     - Adjacent columns Euglycemia and Hyperglycemia have identical value 29 (26.1)
     - Channel bounds strictly isolate the correct column
  12. Human Confirmation Gate (Section 1d & Cochrane Chapter 5):
     - Newly extracted record defaults to PENDING
     - check_human_confirmation_gate raises HumanConfirmationPendingError
     - confirm_human_verification explicitly sets CONFIRMED
     - Confirmed record passes the gate
"""

import os
import sys
import unittest
import fitz

# Ensure src is on path
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORKSPACE_DIR, "src"))

from anchor_engine import (
    ColumnChannel,
    RowBand,
    detect_column_channel,
    find_row_band,
    extract_cell_at_intersection,
    validate_math_checksum,
    extract_tabular_datapoint,
    check_human_confirmation_gate,
    confirm_human_verification,
    render_verification_crop,
    EmptyCellError,
    RowNotFoundError,
    ColumnChannelNotFoundError,
    MathChecksumError,
    AmbiguousRowError,
    HumanConfirmationPendingError
)


class TestAnchorEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.perez_pdf = os.path.join(WORKSPACE_DIR, "projects", "meta_hyperglycaemia", "pdfs", "peds.2022-060965.pdf")
        cls.basu_pdf = os.path.join(WORKSPACE_DIR, "projects", "meta_hyperglycaemia", "pdfs", "F299.full.pdf")
        cls.parm_pdf = os.path.join(WORKSPACE_DIR, "projects", "meta_hyperglycaemia", "pdfs", "1-s2.0-S0022347622000828-main.pdf")

        assert os.path.exists(cls.perez_pdf), f"Missing {cls.perez_pdf}"
        assert os.path.exists(cls.basu_pdf), f"Missing {cls.basu_pdf}"
        assert os.path.exists(cls.parm_pdf), f"Missing {cls.parm_pdf}"

        cls.perez_doc = fitz.open(cls.perez_pdf)
        cls.basu_doc = fitz.open(cls.basu_pdf)
        cls.parm_doc = fitz.open(cls.parm_pdf)

        # Generate synthetic PDF for Perez Bug isolation and adjacent column tests
        cls.synthetic_pdf_path = os.path.join(WORKSPACE_DIR, "scratch", "synthetic_perez_isolation.pdf")
        os.makedirs(os.path.dirname(cls.synthetic_pdf_path), exist_ok=True)
        syn_doc = fitz.open()
        p = syn_doc.new_page(width=600, height=800)

        # Headers at y = 80
        p.insert_text(fitz.Point(60, 80), "Characteristics", fontsize=10)
        p.insert_text(fitz.Point(200, 80), "Euglycemia", fontsize=10)
        p.insert_text(fitz.Point(360, 80), "Hyperglycemia", fontsize=10)

        # Section parent header at y = 110
        p.insert_text(fitz.Point(60, 110), "Outcomes Table", fontsize=10)

        # Row 1: Maternal parity = 2 at y = 150
        p.insert_text(fitz.Point(60, 150), "Maternal parity = 2", fontsize=9)
        p.insert_text(fitz.Point(200, 150), "18 (6.4)", fontsize=9)
        p.insert_text(fitz.Point(360, 150), "29 (26.1)", fontsize=9)

        # Row 2: Death at y = 250 (Homonym value 29 (26.1) in BOTH Euglycemia and Hyperglycemia!)
        p.insert_text(fitz.Point(60, 250), "Death", fontsize=9)
        p.insert_text(fitz.Point(200, 250), "29 (26.1)", fontsize=9)
        p.insert_text(fitz.Point(360, 250), "29 (26.1)", fontsize=9)

        syn_doc.save(cls.synthetic_pdf_path)
        syn_doc.close()
        cls.synthetic_doc = fitz.open(cls.synthetic_pdf_path)

        # Generate synthetic duplicate row PDF for AmbiguousRowError test
        cls.duplicate_row_pdf_path = os.path.join(WORKSPACE_DIR, "scratch", "synthetic_duplicate_rows.pdf")
        dup_doc = fitz.open()
        p_dup = dup_doc.new_page(width=600, height=800)
        p_dup.insert_text(fitz.Point(60, 80), "Header", fontsize=10)
        p_dup.insert_text(fitz.Point(360, 80), "Hyperglycemia", fontsize=10)
        # Two identical 'Death' rows without parent headers
        p_dup.insert_text(fitz.Point(60, 200), "Death", fontsize=9)
        p_dup.insert_text(fitz.Point(360, 200), "29 (26.1)", fontsize=9)
        p_dup.insert_text(fitz.Point(60, 350), "Death", fontsize=9)
        p_dup.insert_text(fitz.Point(360, 350), "10 (9.0)", fontsize=9)
        dup_doc.save(cls.duplicate_row_pdf_path)
        dup_doc.close()
        cls.duplicate_row_doc = fitz.open(cls.duplicate_row_pdf_path)

    @classmethod
    def tearDownClass(cls):
        cls.perez_doc.close()
        cls.basu_doc.close()
        cls.parm_doc.close()
        cls.synthetic_doc.close()
        cls.duplicate_row_doc.close()

    # --------------------------------------------------------------------------
    # 1. POZITÍV TESZT: Perez Halálozás
    # --------------------------------------------------------------------------
    def test_01_positive_perez_death(self):
        """Positive Test: Perez Death -> Page 6, 29 (26.1), N=111, Checksum PASS."""
        spec = {
            "header_page": 5,
            "target_page": 6,
            "col_query": "Hyperglycemia",
            "row_query": "Death",
            "parent_context": "Death or NDI",
            "group_N": 111
        }
        res = extract_tabular_datapoint(self.perez_doc, spec)

        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["value"], 29)
        self.assertEqual(res["pct"], 26.1)
        self.assertEqual(res["checksum"]["status"], "PASS")
        self.assertAlmostEqual(res["checksum"]["expected_pct"], 26.126, places=2)
        # Precision tolerance for 1 decimal (d=1) is 0.05
        self.assertLessEqual(res["checksum"]["delta"], 0.05)
        self.assertEqual(res["checksum"]["decimals"], 1)
        self.assertAlmostEqual(res["checksum"]["tolerance"], 0.05, places=3)
        self.assertTrue(res["checksum"]["checksum_discriminates"])
        self.assertEqual(res["checksum"]["n_tolerance_window"], [29, 29])
        self.assertEqual(res["human_confirmation"]["status"], "PENDING")
        # Verify bounding box is on page 6 in Death row (y ~ 413-422)
        self.assertAlmostEqual(res["bbox"][1], 413.8, delta=5.0)

    # --------------------------------------------------------------------------
    # 2. NEGATÍV TESZT (A LÉNYEG): Paritássor lekérdezése a 6. oldalon
    # --------------------------------------------------------------------------
    def test_02_negative_parity_row_fails_on_label(self):
        """Negative Test: Same query but looking for 'Maternal parity' on Page 6 MUST fail on row label."""
        spec = {
            "header_page": 5,
            "target_page": 6,
            "col_query": "Hyperglycemia",
            "row_query": "Maternal parity",
            "group_N": 111
        }
        with self.assertRaises(RowNotFoundError):
            extract_tabular_datapoint(self.perez_doc, spec)

    def test_02b_negative_death_row_fails_on_page5(self):
        """Negative Test: Death query on Page 5 MUST fail on row label."""
        spec = {
            "header_page": 5,
            "target_page": 5,
            "col_query": "Hyperglycemia",
            "row_query": "Death",
            "group_N": 111
        }
        with self.assertRaises(RowNotFoundError):
            extract_tabular_datapoint(self.perez_doc, spec)

    # --------------------------------------------------------------------------
    # 3. SZOMSZÉDOS OSZLOP IZOLÁCIÓ
    # --------------------------------------------------------------------------
    def test_03_neighbor_column_isolation(self):
        """Neighbor Column Test: Euglycemia (18 [6.4]) vs Hyperglycemia (29 [26.1])."""
        spec_eugly = {
            "header_page": 5,
            "target_page": 6,
            "col_query": "Euglycemia",
            "row_query": "Death",
            "parent_context": "Death or NDI",
            "group_N": 282
        }
        res_eugly = extract_tabular_datapoint(self.perez_doc, spec_eugly)
        self.assertEqual(res_eugly["value"], 18)
        self.assertEqual(res_eugly["pct"], 6.4)
        self.assertEqual(res_eugly["checksum"]["status"], "PASS")

        spec_hyper = {
            "header_page": 5,
            "target_page": 6,
            "col_query": "Hyperglycemia",
            "row_query": "Death",
            "parent_context": "Death or NDI",
            "group_N": 111
        }
        res_hyper = extract_tabular_datapoint(self.perez_doc, spec_hyper)
        self.assertEqual(res_hyper["value"], 29)
        self.assertEqual(res_hyper["pct"], 26.1)

        # Absolute geometric separation: x-channels must not overlap
        self.assertLess(res_eugly["col_channel"].x1, res_hyper["col_channel"].x0)

    # --------------------------------------------------------------------------
    # 4. MUTÁCIÓS TESZTEK (CHECKSUM VÉDELEM)
    # --------------------------------------------------------------------------
    def test_04a_mutation_wrong_denominator(self):
        """Mutation Test: Denominator mutated from 111 to 98 -> MathChecksumError."""
        with self.assertRaises(MathChecksumError):
            validate_math_checksum(n=29, reported_pct=26.1, group_N=98, pct_decimals=1)

    def test_04b_mutation_typo_in_percent(self):
        """Mutation Test: Typo in reported percentage (21.6 instead of 26.1) -> MathChecksumError."""
        with self.assertRaises(MathChecksumError):
            validate_math_checksum(n=29, reported_pct=21.6, group_N=111, pct_decimals=1)

    def test_04c_mutation_within_rounding_tolerance_passes(self):
        """Tolerance Test: 29 / 111 = 26.126% vs reported 26.1% (delta=0.026 <= 0.05%) PASS."""
        res = validate_math_checksum(n=29, reported_pct=26.1, group_N=111, pct_decimals=1)
        self.assertEqual(res["status"], "PASS")
        self.assertTrue(res["checksum_discriminates"])

    # --------------------------------------------------------------------------
    # 5. FAIL-LOUD TESZTEK (SOHA NE FOLYTASSON CSENDBEN)
    # --------------------------------------------------------------------------
    def test_05a_nonexistent_column_fails_loudly(self):
        """Fail-Loud: Nonexistent column header -> ColumnChannelNotFoundError."""
        with self.assertRaises(ColumnChannelNotFoundError):
            detect_column_channel(self.perez_doc, header_page_num=5, col_query="NONEXISTENT_HEADER_XYZ")

    def test_05b_nonexistent_row_fails_loudly(self):
        """Fail-Loud: Nonexistent row query -> RowNotFoundError."""
        with self.assertRaises(RowNotFoundError):
            find_row_band(self.perez_doc, target_page_num=6, row_query="NONEXISTENT_ROW_ABC")

    def test_05c_empty_clip_fails_loudly(self):
        """Fail-Loud: Intersection in empty white margin -> EmptyCellError."""
        empty_col = ColumnChannel("Margin", header_page=6, x0=10, x1=30, header_rect=fitz.Rect(10, 10, 30, 20))
        valid_row = find_row_band(self.perez_doc, target_page_num=6, row_query="Death", parent_context="Death or NDI")
        with self.assertRaises(EmptyCellError):
            extract_cell_at_intersection(self.perez_doc, empty_col, valid_row)

    # --------------------------------------------------------------------------
    # 6. REGRESSZIÓS TESZTEK (3 MEGLÉVŐ KULCSCSIKK)
    # --------------------------------------------------------------------------
    def test_06a_perez_seizures_regression(self):
        """Regression: Perez Seizures -> Page 6, 51 (45.9), N=111."""
        spec = {
            "header_page": 5,
            "target_page": 6,
            "col_query": "Hyperglycemia",
            "row_query": "Seizures",
            "group_N": 111
        }
        res = extract_tabular_datapoint(self.perez_doc, spec)
        self.assertEqual(res["value"], 51)
        self.assertEqual(res["pct"], 45.9)
        self.assertEqual(res["checksum"]["status"], "PASS")
        self.assertEqual(res["checksum"]["decimals"], 1)
        self.assertTrue(res["checksum"]["checksum_discriminates"])

    def test_06b_basu_primary_outcome_regression(self):
        """Regression: Basu Primary Outcome -> Page 6 Table 2, Hyperglycemia (59 [68%]), N=87."""
        spec = {
            "header_page": 6,
            "target_page": 6,
            "col_query": "Hyperglycaemia (n=87)",
            "row_query": "Died or severe disability at 18 months",
            "group_N": 87
        }
        res = extract_tabular_datapoint(self.basu_doc, spec)
        self.assertEqual(res["value"], 59)
        self.assertEqual(res["pct"], 68.0)
        self.assertEqual(res["checksum"]["status"], "PASS")
        self.assertEqual(res["checksum"]["decimals"], 0)
        self.assertAlmostEqual(res["checksum"]["tolerance"], 0.5, places=3)
        self.assertTrue(res["checksum"]["checksum_discriminates"])
        self.assertEqual(res["checksum"]["n_tolerance_window"], [59, 59])

    def test_06c_basu_normoglycemia_control_regression(self):
        """Regression: Basu Primary Outcome -> Page 6 Table 2, Normoglycaemia (44 [49%]), N=89."""
        spec = {
            "header_page": 6,
            "target_page": 6,
            "col_query": "Normoglycaemia",
            "row_query": "Died or severe disability at 18 months",
            "group_N": 89
        }
        res = extract_tabular_datapoint(self.basu_doc, spec)
        self.assertEqual(res["value"], 44)
        self.assertEqual(res["pct"], 49.0)
        self.assertEqual(res["checksum"]["status"], "PASS")
        self.assertEqual(res["checksum"]["decimals"], 0)
        self.assertAlmostEqual(res["checksum"]["tolerance"], 0.5, places=3)
        self.assertTrue(res["checksum"]["checksum_discriminates"])
        self.assertEqual(res["checksum"]["n_tolerance_window"], [44, 44])

    def test_06d_parmentier_death_before_discharge_regression(self):
        """Regression: Parmentier Death before discharge -> Page 4 Table 1, 12 (18.5), N=65 in Hypoglycemia."""
        spec = {
            "header_page": 4,
            "target_page": 4,
            "col_query": "Hypoglycemia (n = 65)",
            "row_query": "Death before discharge",
            "group_N": 65
        }
        res = extract_tabular_datapoint(self.parm_doc, spec)
        self.assertEqual(res["value"], 12)
        self.assertEqual(res["pct"], 18.5)
        self.assertEqual(res["checksum"]["status"], "PASS")
        self.assertEqual(res["checksum"]["decimals"], 1)
        self.assertTrue(res["checksum"]["checksum_discriminates"])

    # --------------------------------------------------------------------------
    # 7. TAMPER-EVIDENCE & HUMAN VERIFICATION CROP
    # --------------------------------------------------------------------------
    def test_07_tamper_evidence_and_crop(self):
        """Verification: SHA-256 tamper evidence and visual crop rendering."""
        spec = {
            "header_page": 5,
            "target_page": 6,
            "col_query": "Hyperglycemia",
            "row_query": "Death",
            "parent_context": "Death or NDI",
            "group_N": 111
        }
        res = extract_tabular_datapoint(self.perez_doc, spec)
        self.assertIsNotNone(res["tamper_sha256"])
        self.assertEqual(len(res["tamper_sha256"]), 16)

        crop_pix = render_verification_crop(
            self.perez_doc,
            target_page_num=spec["target_page"],
            row_band=res["row_band"],
            col_channel=res["col_channel"],
            cell_bbox=fitz.Rect(res["bbox"])
        )
        self.assertGreater(crop_pix.width, 100)
        self.assertGreater(crop_pix.height, 20)

    # --------------------------------------------------------------------------
    # 8. NAGY N PRECÍZIÓ & DISZKRIMINÁLÓ ABLAK (TASK 1b & 1c #1)
    # --------------------------------------------------------------------------
    def test_08_large_n_discriminative_window(self):
        """Task 1c #1: Large N=1000, reported 50% (d=0). Check window, discrimination, and mutation."""
        # 1. Base N=1000, n=500, reported 50% (d=0) -> tol = 0.5%
        res_base = validate_math_checksum(n=500, reported_pct=50, group_N=1000, pct_decimals=0)
        self.assertEqual(res_base["status"], "PASS")
        # In a sample of 1000 with d=0, percentages 49.5%..50.5% map to 495..505
        self.assertEqual(res_base["n_tolerance_window"], [495, 505])
        # Because window width > 1, checksum cannot uniquely determine n:
        self.assertFalse(res_base["checksum_discriminates"])

        # 2. Mutate n by 2 (n=502): inside window [495, 505]
        # Checksum passes mathematically (50.2% rounds to 50%), but discriminates must be False!
        res_mut2 = validate_math_checksum(n=502, reported_pct=50, group_N=1000, pct_decimals=0)
        self.assertEqual(res_mut2["status"], "PASS")
        self.assertFalse(res_mut2["checksum_discriminates"])

        # 3. Mutate n by 10 (n=510): outside window [495, 505]
        # Delta = |50.0 - 51.0| = 1.0% > 0.5% -> MUST raise MathChecksumError!
        with self.assertRaises(MathChecksumError):
            validate_math_checksum(n=510, reported_pct=50, group_N=1000, pct_decimals=0)

        # 4. If reported with d=1 (50.0%), tol = 0.05% -> window is [500, 500], discriminates = True!
        res_d1 = validate_math_checksum(n=500, reported_pct=50.0, group_N=1000, pct_decimals=1)
        self.assertEqual(res_d1["status"], "PASS")
        self.assertEqual(res_d1["n_tolerance_window"], [500, 500])
        self.assertTrue(res_d1["checksum_discriminates"])

    # --------------------------------------------------------------------------
    # 9. HATÁRESETEK (TASK 1c #2 - BOUNDARY TESTING)
    # --------------------------------------------------------------------------
    def test_09_boundary_precision_cases(self):
        """Task 1c #2: Boundary tests for d=1 (tol=0.05%) and d=0 (tol=0.5%)."""
        # --- CASE A: d=1, tol = 0.05% ---
        # 1. Delta = +0.049% (just below 0.05%) -> PASS
        # Let N=10000, expected=10.049%, reported=10.0% (n=1005 vs 1000)
        # 1004.9 / 10000 = 10.049%
        res_pass_d1 = validate_math_checksum(n=1004.9, reported_pct=10.0, group_N=10000, pct_decimals=1)
        self.assertEqual(res_pass_d1["status"], "PASS")
        self.assertAlmostEqual(res_pass_d1["delta"], 0.049, places=3)

        # 2. Delta = +0.051% (just above 0.05%) -> MathChecksumError
        with self.assertRaises(MathChecksumError):
            validate_math_checksum(n=1005.1, reported_pct=10.0, group_N=10000, pct_decimals=1)

        # --- CASE B: d=0, tol = 0.5% ---
        # 3. Delta = +0.499% (just below 0.5%) -> PASS
        # 1049.9 / 10000 = 10.499%, reported=10%
        res_pass_d0 = validate_math_checksum(n=1049.9, reported_pct=10, group_N=10000, pct_decimals=0)
        self.assertEqual(res_pass_d0["status"], "PASS")
        self.assertAlmostEqual(res_pass_d0["delta"], 0.499, places=3)

        # 4. Delta = +0.501% (just above 0.5%) -> MathChecksumError
        with self.assertRaises(MathChecksumError):
            validate_math_checksum(n=1050.1, reported_pct=10, group_N=10000, pct_decimals=0)

    # --------------------------------------------------------------------------
    # 10. AZONOS ÉRTÉK KÉT SORBAN (TASK 1c #3 - PEREZ-HIBA SZINTETIKUS TESZT)
    # --------------------------------------------------------------------------
    def test_10_synthetic_perez_parity_bug_isolation(self):
        """Task 1c #3: Identical 29 (26.1) in Maternal parity (y~150) and Death (y~250)."""
        # A: Querying 'Death' must return cell in Death row (y ~ 250), NEVER the parity row (y ~ 150)
        spec_death = {
            "header_page": 1,
            "target_page": 1,
            "col_query": "Hyperglycemia",
            "row_query": "Death",
            "parent_context": "Outcomes Table",
            "group_N": 111
        }
        res_death = extract_tabular_datapoint(self.synthetic_doc, spec_death)
        self.assertEqual(res_death["value"], 29)
        self.assertEqual(res_death["pct"], 26.1)
        # Verify vertical bounding box is around y = 250, strictly NOT y = 150
        self.assertAlmostEqual(res_death["bbox"][1], 240.3, delta=10.0)
        self.assertGreater(res_death["bbox"][1], 200.0)

        # B: Querying 'Maternal parity = 2' must return cell in Parity row (y ~ 150)
        spec_parity = {
            "header_page": 1,
            "target_page": 1,
            "col_query": "Hyperglycemia",
            "row_query": "Maternal parity = 2",
            "parent_context": "Characteristics",
            "group_N": 111
        }
        res_parity = extract_tabular_datapoint(self.synthetic_doc, spec_parity)
        self.assertEqual(res_parity["value"], 29)
        self.assertEqual(res_parity["pct"], 26.1)
        # Verify vertical bounding box is around y = 150
        self.assertAlmostEqual(res_parity["bbox"][1], 140.3, delta=10.0)
        self.assertLess(res_parity["bbox"][1], 200.0)

        # C: If duplicate identical row label appears twice without parent_context -> AmbiguousRowError
        with self.assertRaises(AmbiguousRowError):
            find_row_band(self.duplicate_row_doc, target_page_num=1, row_query="Death")

    # --------------------------------------------------------------------------
    # 11. SZOMSZÉDOS AZONOS ÉRTÉK (TASK 1c #4 - ADJACENT COLUMN ISOLATION)
    # --------------------------------------------------------------------------
    def test_11_adjacent_column_identical_value_isolation(self):
        """Task 1c #4: In Death row, both Euglycemia and Hyperglycemia have 29 (26.1)."""
        # A: Extract from Euglycemia channel (x ~ 200)
        spec_eugly = {
            "header_page": 1,
            "target_page": 1,
            "col_query": "Euglycemia",
            "row_query": "Death",
            "parent_context": "Outcomes Table",
            "group_N": 111
        }
        res_eugly = extract_tabular_datapoint(self.synthetic_doc, spec_eugly)
        self.assertEqual(res_eugly["value"], 29)
        self.assertLess(res_eugly["bbox"][0], 250.0)  # Located in Euglycemia column

        # B: Extract from Hyperglycemia channel (x ~ 360)
        spec_hyper = {
            "header_page": 1,
            "target_page": 1,
            "col_query": "Hyperglycemia",
            "row_query": "Death",
            "parent_context": "Outcomes Table",
            "group_N": 111
        }
        res_hyper = extract_tabular_datapoint(self.synthetic_doc, spec_hyper)
        self.assertEqual(res_hyper["value"], 29)
        self.assertGreater(res_hyper["bbox"][0], 330.0)  # Located in Hyperglycemia column

        # Absolute spatial separation between the two extracted bboxes
        self.assertLess(res_eugly["bbox"][2], res_hyper["bbox"][0])

    # --------------------------------------------------------------------------
    # 12. EMBERI MEGERŐSÍTÉS NAPLÓZÁSA ÉS LINTER KAPU (TASK 1d)
    # --------------------------------------------------------------------------
    def test_12_human_confirmation_gate(self):
        """Task 1d: Human confirmation defaults to PENDING and blocks unconfirmed export."""
        spec = {
            "header_page": 5,
            "target_page": 6,
            "col_query": "Hyperglycemia",
            "row_query": "Death",
            "parent_context": "Death or NDI",
            "group_N": 111,
            "study_id": "Perez_2023",
            "variable_canonical": "mortality_hyperglycemia_events"
        }
        res = extract_tabular_datapoint(self.perez_doc, spec)

        # 1. Verification of default PENDING state
        self.assertEqual(res["human_confirmation"]["status"], "PENDING")
        self.assertIsNone(res["human_confirmation"]["reviewer"])
        self.assertIsNone(res["human_confirmation"]["timestamp"])

        # 2. Gate MUST fail on PENDING status
        with self.assertRaises(HumanConfirmationPendingError):
            check_human_confirmation_gate(res)

        # 3. Explicit human action confirms the datapoint
        confirmed_res = confirm_human_verification(res, reviewer_name="Dr. Kovács")
        self.assertEqual(confirmed_res["human_confirmation"]["status"], "CONFIRMED")
        self.assertEqual(confirmed_res["human_confirmation"]["reviewer"], "Dr. Kovács")
        self.assertIsNotNone(confirmed_res["human_confirmation"]["timestamp"])

        # 4. Gate passes on CONFIRMED status
        self.assertTrue(check_human_confirmation_gate(confirmed_res))


if __name__ == "__main__":
    unittest.main(verbosity=2)
