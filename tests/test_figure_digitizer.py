#!/usr/bin/env python3
"""
test_figure_digitizer.py
========================
Comprehensive Unit Test Suite for Figure Digitizer Module (Section 3.5).
Covers:
  1. Logarithmic & Linear Axis Calibration
  2. Fail-Loud Error Policies:
     - Fewer than 3 calibration points -> InsufficientCalibrationPointsError
     - Residual exceeding threshold -> CalibrationResidualExceededError
     - Unsupported scale -> InvalidAxisScaleError
     - Point estimate outside CI -> InconsistentConfidenceIntervalError
     - Mismatch with reported text -> CrossCheckMismatchError
  3. Forest Plot Extraction & Text Cross-Check (Perez Figure 4B specification)
  4. Structured Output Format Compliance (Section 3.5.5)
"""

import os
import sys
import unittest

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORKSPACE_DIR, "src"))

from figure_digitizer import (
    AxisCalibration,
    extract_forest_plot_datapoint,
    InsufficientCalibrationPointsError,
    CalibrationResidualExceededError,
    InvalidAxisScaleError,
    InconsistentConfidenceIntervalError,
    CrossCheckMismatchError
)


class TestFigureDigitizer(unittest.TestCase):

    # --------------------------------------------------------------------------
    # 1. TENGELYKALIBRÁCIÓS TESZTEK (LOG & LINEAR)
    # --------------------------------------------------------------------------
    def test_01_log_axis_calibration_success(self):
        """Test robust log-scale calibration with 3 points."""
        # Realistic coordinates where x = a * ln(v) + b
        # Let b = 268.9 (coord at v=1.0), and a = (381.7 - 268.9) / ln(4.0) = 81.368
        # v=0.5 -> 268.9 + 81.368 * ln(0.5) = 268.9 - 56.40 = 212.5
        ref_points = [
            {"value": 0.5, "coord": 212.5},
            {"value": 1.0, "coord": 268.9},
            {"value": 4.0, "coord": 381.7}
        ]
        calib = AxisCalibration(scale="log", reference_points=ref_points, max_residual_pct=0.5)
        self.assertEqual(calib.scale, "log")
        self.assertLess(calib.max_residual_pct, 0.5)

        # Test forward mapping: v=2.0 -> coord
        c_2 = calib.value_to_coord(2.0)
        self.assertAlmostEqual(c_2, 268.9 + 81.368 * 0.69315, delta=1.0)

        # Test inverse mapping: coord -> v
        v_back = calib.coord_to_value(c_2)
        self.assertAlmostEqual(v_back, 2.0, places=2)

    def test_02_linear_axis_calibration_success(self):
        """Test linear calibration with 4 points."""
        ref_points = [
            {"value": 0.0, "coord": 100.0},
            {"value": 10.0, "coord": 200.0},
            {"value": 20.0, "coord": 300.0},
            {"value": 30.0, "coord": 400.0}
        ]
        calib = AxisCalibration(scale="linear", reference_points=ref_points)
        self.assertEqual(calib.scale, "linear")
        self.assertAlmostEqual(calib.coord_to_value(250.0), 15.0, places=3)
        self.assertAlmostEqual(calib.value_to_coord(15.0), 250.0, places=3)

    # --------------------------------------------------------------------------
    # 2. FAIL-LOUD HIBAMÓD TESZTEK (3.5.6 TÁBLÁZAT)
    # --------------------------------------------------------------------------
    def test_03_insufficient_calibration_points_fails_loudly(self):
        """Fail-Loud: Fewer than 3 calibration points -> InsufficientCalibrationPointsError."""
        two_points = [
            {"value": 1.0, "coord": 100.0},
            {"value": 2.0, "coord": 200.0}
        ]
        with self.assertRaises(InsufficientCalibrationPointsError):
            AxisCalibration(scale="linear", reference_points=two_points)

    def test_04_excessive_residual_fails_loudly(self):
        """Fail-Loud: High calibration residual (non-linear data on linear scale) -> Error."""
        curved_points = [
            {"value": 1.0, "coord": 100.0},
            {"value": 2.0, "coord": 150.0},
            {"value": 4.0, "coord": 400.0}  # strong deviation
        ]
        with self.assertRaises(CalibrationResidualExceededError):
            AxisCalibration(scale="linear", reference_points=curved_points, max_residual_pct=0.5)

    def test_05_unsupported_scale_fails_loudly(self):
        """Fail-Loud: Ambiguous/unsupported scale type -> InvalidAxisScaleError."""
        points = [{"value": 1, "coord": 10}, {"value": 2, "coord": 20}, {"value": 3, "coord": 30}]
        with self.assertRaises(InvalidAxisScaleError):
            AxisCalibration(scale="quadratic", reference_points=points)

    def test_06_inconsistent_ci_fails_loudly(self):
        """Fail-Loud: Point estimate falls outside confidence interval -> InconsistentConfidenceIntervalError."""
        ref_points = [
            {"value": 0.5, "coord": 212.5},
            {"value": 1.0, "coord": 268.9},
            {"value": 4.0, "coord": 381.7}
        ]
        calib = AxisCalibration(scale="log", reference_points=ref_points)

        spec = {
            "study_id": "Test_2024",
            "variable_canonical": "test_outcome",
            "figure_label": "Figure 1",
            "page_number": 1
        }
        # Point coord at 400 (v ~ 5.0), but CI high is at 350 (v ~ 2.7)
        with self.assertRaises(InconsistentConfidenceIntervalError):
            extract_forest_plot_datapoint(
                spec=spec,
                x_calibration=calib,
                point_coord=400.0,
                ci_low_coord=200.0,
                ci_high_coord=350.0
            )

    def test_07_text_cross_check_mismatch_fails_loudly(self):
        """Fail-Loud: Digitized value deviates from reported text -> CrossCheckMismatchError."""
        ref_points = [
            {"value": 0.5, "coord": 212.5},
            {"value": 1.0, "coord": 268.9},
            {"value": 4.0, "coord": 381.7}
        ]
        calib = AxisCalibration(scale="log", reference_points=ref_points)

        spec = {
            "study_id": "Test_2024",
            "variable_canonical": "test_outcome",
            "figure_label": "Figure 1",
            "page_number": 1
        }
        # Coordinates for point ~ 2.52
        point_c = calib.value_to_coord(2.52)
        low_c = calib.value_to_coord(1.10)
        high_c = calib.value_to_coord(5.77)

        # But reported text states 1.45 (mismatch > 8%)
        reported_mismatch = "aOR 1.45; 95% CI 1.10-5.77"
        with self.assertRaises(CrossCheckMismatchError):
            extract_forest_plot_datapoint(
                spec=spec,
                x_calibration=calib,
                point_coord=point_c,
                ci_low_coord=low_c,
                ci_high_coord=high_c,
                reported_text=reported_mismatch,
                cross_check_tolerance=0.08
            )

    # --------------------------------------------------------------------------
    # 3. TELJES FOREST PLOT KINYERÉS & STRUKTÚRA MEGFELELŐSÉG (SECTION 3.5.5)
    # --------------------------------------------------------------------------
    def test_08_perez_figure_4b_extraction_and_schema(self):
        """Full Verification: Perez Figure 4B extraction matches Section 3.5.5 JSON structure."""
        ref_points = [
            {"value": 0.5, "coord": 212.4},
            {"value": 1.0, "coord": 268.9},
            {"value": 4.0, "coord": 381.7}
        ]
        calib = AxisCalibration(scale="log", reference_points=ref_points, max_residual_pct=0.5)

        spec = {
            "study_id": "Perez_2023",
            "variable_canonical": "mortality_aOR_hyperglycemia",
            "figure_label": "Figure 4B",
            "page_number": 8,
            "figure_bbox": [60.0, 120.0, 540.0, 420.0],
            "mode": "VECTOR",
            "series": "Hyperglycemia vs Normoglycemia"
        }

        # Value 2.52, CI [1.10, 5.77]
        point_coord = calib.value_to_coord(2.52)
        ci_low_coord = calib.value_to_coord(1.10)
        ci_high_coord = calib.value_to_coord(5.77)

        reported_text = "aOR 2.52; 95% CI 1.10-5.77"

        res = extract_forest_plot_datapoint(
            spec=spec,
            x_calibration=calib,
            point_coord=point_coord,
            ci_low_coord=ci_low_coord,
            ci_high_coord=ci_high_coord,
            reported_text=reported_text
        )

        # Check required fields from Section 3.5.5
        self.assertEqual(res["study_id"], "Perez_2023")
        self.assertEqual(res["variable_canonical"], "mortality_aOR_hyperglycemia")
        self.assertEqual(res["extracted_value"], 2.52)
        self.assertEqual(res["value_origin"], "DIGITIZED")
        self.assertEqual(res["figure"]["label"], "Figure 4B")
        self.assertEqual(res["figure"]["chart_type"], "FOREST_PLOT")
        self.assertEqual(res["estimate"]["point"], 2.52)
        self.assertEqual(res["estimate"]["ci_low"], 1.10)
        self.assertEqual(res["estimate"]["ci_high"], 5.77)
        self.assertEqual(res["cross_check"]["status"], "VERIFIED_AGAINST_TEXT")
        self.assertTrue(res["cross_check"]["within_tolerance"])
        self.assertEqual(res["human_confirmation"]["status"], "PENDING")
        self.assertEqual(len(res["context_sha256"]), 16)


if __name__ == "__main__":
    unittest.main(verbosity=2)
