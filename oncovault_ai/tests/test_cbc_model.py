import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))
from oncovault_ai.src.predict import DiagnosticEngine

class TestCbcModel(unittest.TestCase):
    def setUp(self):
        self.engine = DiagnosticEngine.get_instance()

    def test_cbc_model_loaded(self):
        self.assertIsNotNone(self.engine.cbc_model)
        self.assertIsNotNone(self.engine.cbc_scaler)
        self.assertEqual(self.engine.cbc_metadata.get("model_version"), "leukemia-cbc-v1")

    def test_abnormal_cbc_profile(self):
        # Profile characteristic of hematologic malignancy: high WBC, low PLT, low HGB
        profile = {
            "WBC": 85.0,
            "RBC": 2.1,
            "HGB": 65.0,
            "PLT": 15.0,
            "NEUT_ABS": 2.0,
            "NEUT_PCT": 10.0,
            "MONO_ABS": 0.5,
            "RDW_SD": 68.0,
            "RDW_CV": 22.0
        }
        res = self.engine.assess_cbc(profile)
        self.assertEqual(res["prediction"], "Elevated Risk")
        self.assertGreater(res["riskScore"], 0.70)
        self.assertEqual(res["modelVersion"], "leukemia-cbc-v1")
        self.assertTrue(len(res["contributingFactors"]) > 0)

    def test_normal_cbc_profile(self):
        # Typical healthy adult reference ranges
        profile = {
            "WBC": 6.5,
            "RBC": 4.8,
            "HGB": 145.0,
            "PLT": 250.0,
            "NEUT_ABS": 4.0,
            "NEUT_PCT": 60.0,
            "MONO_ABS": 0.5,
            "RDW_SD": 42.0,
            "RDW_CV": 12.5
        }
        res = self.engine.assess_cbc(profile)
        self.assertEqual(res["prediction"], "Lower Risk")
        self.assertLess(res["riskScore"], 0.40)

if __name__ == "__main__":
    unittest.main()
