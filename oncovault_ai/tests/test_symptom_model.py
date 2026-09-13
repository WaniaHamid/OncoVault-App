import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))
from oncovault_ai.src.predict import DiagnosticEngine

class TestSymptomModel(unittest.TestCase):
    def setUp(self):
        self.engine = DiagnosticEngine.get_instance()

    def test_symptom_model_loaded(self):
        self.assertIsNotNone(self.engine.symptom_model)
        self.assertEqual(self.engine.symptom_metadata.get("model_version"), "leukemia-symptom-v1")

    def test_high_risk_symptom_profile(self):
        profile = {
            "swollen_painless_lymph_nodes": 1,
            "frequent_infections": 1,
            "enlarged_liver": 1,
            "bone_pain": 1,
            "persistent_weakness_fatigue": 1,
            "jaundice": 1
        }
        res = self.engine.assess_symptoms(profile)
        self.assertEqual(res["prediction"], "Elevated Risk")
        self.assertGreaterEqual(res["riskScore"], 0.70)
        self.assertEqual(res["modelVersion"], "leukemia-symptom-v1")
        self.assertTrue(len(res["contributingFactors"]) > 0)
        self.assertIn("clinical decision support", res["disclaimer"].lower())

    def test_low_risk_symptom_profile(self):
        profile = {
            "shortness_of_breath": 0, "bone_pain": 0, "fever": 0, "family_history": 0,
            "frequent_infections": 0, "itchy_skin_rash": 0, "loss_of_appetite_nausea": 0,
            "persistent_weakness_fatigue": 0, "swollen_painless_lymph_nodes": 0,
            "significant_bruising_bleeding": 0, "enlarged_liver": 0, "oral_cavity_changes": 0,
            "vision_blurring": 0, "jaundice": 0, "night_sweats": 0, "smoking_history": 0
        }
        res = self.engine.assess_symptoms(profile)
        self.assertEqual(res["prediction"], "Lower Risk")
        self.assertLess(res["riskScore"], 0.50)

if __name__ == "__main__":
    unittest.main()
