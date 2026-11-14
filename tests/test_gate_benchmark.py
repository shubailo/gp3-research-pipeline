#!/usr/bin/env python3
"""
tests/test_gate_benchmark.py
================================================================================
GP3 Data Integrity Audit Gate — Synthetic Benchmark Test Suite
================================================================================
Szintetikus adatkészleteken teszteli, hogy az audit kapu determinisztikusan:
1. Buktatja a betelepített kollineáris identitást (exit code 1)
2. Buktatja a betelepített célváltozó-szivárgást (exit code 1)
3. "NEM ELDÖNTHETŐ / ALULMINTÁZOTT"-ra állítja a kis klaszterszámú (G < 15) adatot (exit code 2)
4. Átengedi a valós, független jelet mutató, megfelelő mintanagyságú adatot ÉS érvényes provenance-t (exit code 0)
5. Buktatja az azonos fiziológiai kompartment egyidejű szivárgását (exit code 1)
6. ÁTENGEDI a közös klinikai dokumentációs forrásból (clinical_chart) származó változókat (pl. GA + életnap), nem blokkol tévesen!
7. FIGYELMEZTETÉSKÉNT (és NEM blokkoló hibaként) kezeli a környezeti expozíció hatását a kimenetelre (Room_T -> Torzs), nem zárja ki a kutatási kérdést!
"""

import sys
import os
import io
import contextlib
import json
import unittest
import numpy as np
import pandas as pd

# Insert src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
try:
    from audit_data_integrity import audit_data
except ImportError:
    try:
        from src.audit_data_integrity import audit_data
    except ImportError:
        audit_data = None


class TestAuditDataIntegrityGates(unittest.TestCase):
    def setUp(self):
        if audit_data is None:
            self.skipTest("audit_data_integrity module not present in pipeline core")
        np.random.seed(42)
        self.prov_path_valid = "tests/test_prov_valid.json"
        self.prov_path_chart = "tests/test_prov_chart.json"
        self.prov_path_ambient = "tests/test_prov_ambient.json"
        self.prov_path_leak = "tests/test_prov_leak.json"
        
        # Valid independent provenance fixture
        with open(self.prov_path_valid, "w", encoding="utf-8") as f:
            json.dump({
                "predictors": {
                    "Valid_Pred1": {"instrument": "device_A", "timing": "prior", "compartment": "blood_biomarker"},
                    "Valid_Pred2": {"instrument": "device_B", "timing": "prior", "compartment": "clinical_scale"}
                },
                "target": {
                    "Target": {"instrument": "device_C", "timing": "concurrent", "compartment": "clinical_outcome"}
                }
            }, f)

        # Clinical chart provenance (GA + Age_days from same chart - MUST NOT BLOCK)
        with open(self.prov_path_chart, "w", encoding="utf-8") as f:
            json.dump({
                "predictors": {
                    "GA": {"instrument": "clinical_chart", "derived_from": ["ultrasound_ga"], "timing": "prior"},
                    "Age_days": {"instrument": "clinical_chart", "derived_from": ["birth_timestamp"], "timing": "prior"}
                },
                "target": {
                    "Target": {"instrument": "device_C", "timing": "concurrent", "compartment": "clinical_outcome"}
                }
            }, f)

        # Environmental exposure provenance (Room_T influencing T_skin - MUST NOT BLOCK, ONLY WARN)
        with open(self.prov_path_ambient, "w", encoding="utf-8") as f:
            json.dump({
                "predictors": {
                    "Room_T": {"instrument": "room_sensor", "timing": "concurrent", "compartment": "room_surface"}
                },
                "target": {
                    "T_skin": {"instrument": "thermal_camera", "timing": "concurrent", "compartment": "skin_surface"}
                }
            }, f)

        # Same physiological compartment leakage (e.g. skin predicting skin concurrently - MUST BLOCK)
        with open(self.prov_path_leak, "w", encoding="utf-8") as f:
            json.dump({
                "predictors": {
                    "Back_Skin": {"instrument": "sensor_back", "timing": "concurrent", "compartment": "skin_surface"}
                },
                "target": {
                    "Trunk_Skin": {"instrument": "sensor_trunk", "timing": "concurrent", "compartment": "skin_surface"}
                }
            }, f)

    def tearDown(self):
        for p in [self.prov_path_valid, self.prov_path_chart, self.prov_path_ambient, self.prov_path_leak]:
            if os.path.exists(p):
                os.remove(p)

    def test_planted_collinear_identity(self):
        """Teszt 1: Két prediktor egymás származtatott másolata (|r| = 1.0). Elvárt: exit code 1."""
        n = 100
        x1 = np.random.normal(20, 2, n)
        x2 = 0.5 * x1 + 10.0 # Tökéletes kollinearitás
        y = np.random.binomial(1, 0.4, n)
        df = pd.DataFrame({"Target": y, "Pred_A": x1, "Pred_B": x2, "Date": [f"Day_{i%25}" for i in range(n)]})
        
        code = audit_data(df, "Target", ["Pred_A", "Pred_B"], "Date")
        self.assertEqual(code, 1, "A kapunak meg kell buktatnia a kollineáris prediktorokat!")

    def test_planted_target_leakage(self):
        """Teszt 2: A prediktor virtuálisan azonos a célváltozóval (|r| > 0.95). Elvárt: exit code 1."""
        n = 100
        y = np.random.binomial(1, 0.5, n)
        x_leak = y + np.random.normal(0, 0.05, n)
        df = pd.DataFrame({"Target": y, "Leak_Pred": x_leak, "Date": [f"Day_{i%25}" for i in range(n)]})
        
        code = audit_data(df, "Target", ["Leak_Pred"], "Date")
        self.assertEqual(code, 1, "A kapunak meg kell buktatnia a célváltozó-szivárgást!")

    def test_planted_underpowered_clusters(self):
        """Teszt 3: Alulmintázott adat, mindössze G = 6 mérési nappal (G < 15). Elvárt: exit code 2."""
        n = 60
        x1 = np.random.normal(0, 1, n)
        y = np.random.binomial(1, 0.4, n)
        groups = [f"Day_{i%6}" for i in range(n)]
        df = pd.DataFrame({"Target": y, "Pred_1": x1, "Meas_Day": groups})
        
        code = audit_data(df, "Target", ["Pred_1"], "Meas_Day")
        self.assertEqual(code, 2, "A kapunak NEM ELDÖNTHETŐ / ALULMINTÁZOTT ítéletet (exit code 2) kell hoznia G < 15 esetén!")

    def test_genuine_signal_passes_with_provenance(self):
        """Teszt 4: N=300, G=30 klaszter, független prediktorok, valódi összefüggés, érvényes provenance. Elvárt: exit code 0."""
        n = 300
        x1 = np.random.normal(0, 1, n)
        x2 = np.random.normal(10, 2, n)
        logits = 0.8 * x1 - 0.1 * (x2 - 10)
        prob = 1.0 / (1.0 + np.exp(-logits))
        y = np.random.binomial(1, prob)
        groups = [f"Day_{i%30}" for i in range(n)]
        
        df = pd.DataFrame({"Target": y, "Valid_Pred1": x1, "Valid_Pred2": x2, "Center_Day": groups})
        
        code = audit_data(df, "Target", ["Valid_Pred1", "Valid_Pred2"], "Center_Day", provenance_file=self.prov_path_valid)
        self.assertEqual(code, 0, "A kapunak át kell engednie a valódi, tiszta adatot, ha a provenance érvényes!")

    def test_same_compartment_leakage_blocks(self):
        """Teszt 5: Azonos élettani kompartment egyidejű mérése (Back_Skin prediktálja Trunk_Skin-t). Elvárt: exit code 1."""
        n = 150
        back = np.random.normal(35, 1, n)
        trunk = back + np.random.normal(0, 0.5, n)
        groups = [f"Day_{i%20}" for i in range(n)]
        df = pd.DataFrame({"Trunk_Skin": trunk, "Back_Skin": back, "Date": groups})
        
        code = audit_data(df, "Trunk_Skin", ["Back_Skin"], "Date", provenance_file=self.prov_path_leak)
        self.assertEqual(code, 1, "A kapunak blokkolnia kell az azonos élettani kompartment egyidejű szivárgását!")

    def test_clinical_chart_shared_doc_does_not_block(self):
        """Teszt 6 (Téves riasztás védelme): GA és Age_days mindkettő clinical_chart-ból származik.
        NEM minősülhet műszer-átfedésnek, exit code kötelezően 0!"""
        n = 200
        ga = np.random.normal(38, 2, n)
        age = np.random.exponential(3, n)
        y = np.random.binomial(1, 0.3, n)
        groups = [f"Day_{i%20}" for i in range(n)]
        df = pd.DataFrame({"Target": y, "GA": ga, "Age_days": age, "Date": groups})
        
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = audit_data(df, "Target", ["GA", "Age_days"], "Date", provenance_file=self.prov_path_chart)
        output = buf.getvalue()
        
        self.assertEqual(code, 0, "Közös klinikai adatlap forrás esetén a kapunak 0-s exit kóddal át kell engednie az adatot!")
        self.assertIn("Közös klinikai dokumentációs forrás", output)
        self.assertNotIn("FIZIKAI SZENZOR-ÁTFEDÉS", output)

    def test_environmental_exposure_does_not_block(self):
        """Teszt 7 (Kutatási kérdés védelme): Room_T fizikailag hat a T_skin-re.
        Ez környezeti expozíció; specifikusan meg kell jelennie a figyelmeztetésnek a naplóban, és exit code 0 kell legyen."""
        n = 200
        room_t = np.random.normal(24, 2, n)
        t_skin = 34.0 + 0.2 * room_t + np.random.normal(0, 1, n)
        groups = [f"Day_{i%20}" for i in range(n)]
        df = pd.DataFrame({"T_skin": t_skin, "Room_T": room_t, "Date": groups})
        
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = audit_data(df, "T_skin", ["Room_T"], "Date", provenance_file=self.prov_path_ambient)
        output = buf.getvalue()
        
        self.assertEqual(code, 0, "A környezeti expozíció miatt nem dobhat hibát a kapu (exit code 0 elvárt)!")
        self.assertIn("KÖRNYEZETI EXPOZÍCIÓ", output, "A kimenetnek kötelezően tartalmaznia kell a KÖRNYEZETI EXPOZÍCIÓ figyelmeztetést!")
        self.assertNotIn("KOMPARTMENT-SZIVÁRGÁS", output, "Nem minősítheti azonos kompartment szivárgásnak a szobahőmérsékletet!")

    def test_placeholder_temperature_fails_plausibility(self):
        """Teszt 8 (Fiziológiai tartomány-védelem): Room_T = 0.0 °C Excel helykitöltő beültetése. Elvárt: exit code 1."""
        n = 100
        room_t = np.random.normal(24, 2, n)
        room_t[0] = 0.0 # 0.0 °C helykitöltő hiba
        y = np.random.binomial(1, 0.4, n)
        groups = [f"Day_{i%20}" for i in range(n)]
        df = pd.DataFrame({"Target": y, "Room_T": room_t, "Date": groups})
        
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = audit_data(df, "Target", ["Room_T"], "Date", provenance_file=self.prov_path_ambient)
        output = buf.getvalue()
        
        self.assertEqual(code, 1, "A kapunak 1-es exit kóddal kell buktatnia a fiziológiailag lehetetlen 0.0 °C értéket!")
        self.assertIn("TARTOMÁNYHIBA", output)


if __name__ == "__main__":
    unittest.main()
