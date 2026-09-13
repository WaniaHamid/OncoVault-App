import sys, os
sys.path.insert(0, os.path.abspath("."))
from oncovault_ai.src.predict import DiagnosticEngine

engine = DiagnosticEngine.get_instance()

# 1. Test Symptoms from screenshot
sym_res = engine.assess_symptoms({
    "shortness_of_breath": 1,
    "significant_bruising_bleeding": 1,
    "night_sweats": 1
})
print("Symptom Result:", sym_res)

# 2. Test CBC from screenshot (Only WBC=2.4, PLT=45, NEUT%=45%)
cbc_res = engine.assess_cbc({
    "WBC": 2.4,
    "PLT": 45.0,
    "NEUT_PCT": 45.0
})
print("\nCBC Result (Only recorded fields):", cbc_res)
