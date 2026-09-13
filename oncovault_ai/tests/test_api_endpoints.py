import os
import sys
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("."))
from oncovault_nlp.main import app

class TestDiagnosticApi(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_predict_symptoms_endpoint(self):
        payload = {
            "shortness_of_breath": 1,
            "bone_pain": 1,
            "fever": 1,
            "family_history": 0,
            "frequent_infections": 1,
            "itchy_skin_rash": 0,
            "loss_of_appetite_nausea": 1,
            "persistent_weakness_fatigue": 1,
            "swollen_painless_lymph_nodes": 1,
            "significant_bruising_bleeding": 1,
            "enlarged_liver": 1,
            "oral_cavity_changes": 0,
            "vision_blurring": 0,
            "jaundice": 0,
            "night_sweats": 1,
            "smoking_history": 0
        }
        res = self.client.post("/predict-symptoms", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("prediction", data)
        self.assertIn("riskScore", data)
        self.assertEqual(data["modelVersion"], "leukemia-symptom-v1")
        self.assertIsInstance(data["contributingFactors"], list)
        self.assertIn("disclaimer", data)

    def test_predict_cbc_endpoint(self):
        payload = {
            "WBC": 45.0,
            "RBC": 2.8,
            "HGB": 80.0,
            "PLT": 30.0,
            "NEUT_ABS": 3.0,
            "NEUT_PCT": 20.0,
            "MONO_ABS": 0.5,
            "RDW_SD": 55.0,
            "RDW_CV": 18.0
        }
        res = self.client.post("/predict-cbc", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("prediction", data)
        self.assertIn("riskScore", data)
        self.assertEqual(data["modelVersion"], "leukemia-cbc-v1")
        self.assertIsInstance(data["contributingFactors"], list)

    def test_health_check_preserved(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "online")

if __name__ == "__main__":
    unittest.main()
