"""
OncoVault AI Engine - Feature Definitions & Mappings
Defines canonical feature orders, CSV column mappings, human-readable labels, and conversion utilities.
"""
from typing import Dict, List, Any, Tuple

# 16 Finalized Symptoms in canonical order
SYMPTOM_FEATURES: List[Dict[str, str]] = [
    {
        "key": "shortness_of_breath",
        "csv_col": "shortness of breath",
        "label": "Shortness of Breath",
        "ehr_field": "shortnessOfBreath"
    },
    {
        "key": "bone_pain",
        "csv_col": "bone_pain",
        "label": "Bone Pain",
        "ehr_field": "bonePain"
    },
    {
        "key": "fever",
        "csv_col": "fever",
        "label": "Fever",
        "ehr_field": "fever"
    },
    {
        "key": "family_history",
        "csv_col": "family_history",
        "label": "Family History of Cancer",
        "ehr_field": "familyHistory"
    },
    {
        "key": "frequent_infections",
        "csv_col": "frequent_infections",
        "label": "Frequent Infections",
        "ehr_field": "frequentInfections"
    },
    {
        "key": "itchy_skin_rash",
        "csv_col": "Itchy_skin_or_rash",
        "label": "Itchy Skin / Rash",
        "ehr_field": "itchySkinOrRash"
    },
    {
        "key": "loss_of_appetite_nausea",
        "csv_col": "loss_of_appetite_or_nausea",
        "label": "Loss of Appetite / Nausea",
        "ehr_field": "lossOfAppetiteOrNausea"
    },
    {
        "key": "persistent_weakness_fatigue",
        "csv_col": "Persistent_weakness _and_fatigue",
        "label": "Persistent Weakness & Fatigue",
        "ehr_field": "persistentWeaknessAndFatigue"
    },
    {
        "key": "swollen_painless_lymph_nodes",
        "csv_col": "swollen,painless_lymph",
        "label": "Swollen Painless Lymph Nodes",
        "ehr_field": "swollenPainlessLymphNodes"
    },
    {
        "key": "significant_bruising_bleeding",
        "csv_col": "significant_bruising,bleeding",
        "label": "Significant Bruising / Bleeding",
        "ehr_field": "significantBruisingOrBleeding"
    },
    {
        "key": "enlarged_liver",
        "csv_col": "enlarged_liver",
        "label": "Enlarged Liver / Hepatomegaly",
        "ehr_field": "enlargedLiver"
    },
    {
        "key": "oral_cavity_changes",
        "csv_col": "oral_cavity",
        "label": "Oral Cavity Changes",
        "ehr_field": "oralCavityChanges"
    },
    {
        "key": "vision_blurring",
        "csv_col": "vision_blurring",
        "label": "Vision Blurring",
        "ehr_field": "visionBlurring"
    },
    {
        "key": "jaundice",
        "csv_col": "jaundice",
        "label": "Jaundice",
        "ehr_field": "jaundice"
    },
    {
        "key": "night_sweats",
        "csv_col": "night_sweats",
        "label": "Night Sweats",
        "ehr_field": "nightSweats"
    },
    {
        "key": "smoking_history",
        "csv_col": "smokes",
        "label": "Smoking History",
        "ehr_field": "smokes"
    },
]

SYMPTOM_KEYS = [f["key"] for f in SYMPTOM_FEATURES]
SYMPTOM_CSV_COLS = [f["csv_col"] for f in SYMPTOM_FEATURES]
SYMPTOM_LABELS = {f["key"]: f["label"] for f in SYMPTOM_FEATURES}

# 9 Finalized CBC Parameters in canonical order
CBC_FEATURES: List[Dict[str, str]] = [
    {
        "key": "WBC",
        "csv_col": "WBC(10^9/L)",
        "label": "White Blood Cell Count",
        "unit": "10^9/L",
        "ehr_field": "WBC"
    },
    {
        "key": "RBC",
        "csv_col": "RBC(10^12/L)",
        "label": "Red Blood Cell Count",
        "unit": "10^12/L",
        "ehr_field": "RBC"
    },
    {
        "key": "HGB",
        "csv_col": "HGB(g/L)",
        "label": "Hemoglobin",
        "unit": "g/L",
        "ehr_field": "Hemoglobin"
    },
    {
        "key": "PLT",
        "csv_col": "PLT(10^9/L)",
        "label": "Platelet Count",
        "unit": "10^9/L",
        "ehr_field": "Platelets"
    },
    {
        "key": "NEUT_ABS",
        "csv_col": "NEUT#(10^9/L)",
        "label": "Absolute Neutrophil Count (NEUT#)",
        "unit": "10^9/L",
        "ehr_field": "Neutrophils.absolute"
    },
    {
        "key": "NEUT_PCT",
        "csv_col": "NEUT%(%)",
        "label": "Neutrophil Percentage (NEUT%)",
        "unit": "%",
        "ehr_field": "Neutrophils.percentage"
    },
    {
        "key": "MONO_ABS",
        "csv_col": "MONO#(10^9/L)",
        "label": "Absolute Monocyte Count (MONO#)",
        "unit": "10^9/L",
        "ehr_field": "Monocytes.absolute"
    },
    {
        "key": "RDW_SD",
        "csv_col": "RDW-SD(fL)",
        "label": "Red Cell Distribution Width (SD)",
        "unit": "fL",
        "ehr_field": "RDW-SD"
    },
    {
        "key": "RDW_CV",
        "csv_col": "RDW-CV(%)",
        "label": "Red Cell Distribution Width (CV)",
        "unit": "%",
        "ehr_field": "RDW-CV"
    },
]

CBC_KEYS = [f["key"] for f in CBC_FEATURES]
CBC_CSV_COLS = [f["csv_col"] for f in CBC_FEATURES]
CBC_LABELS = {f["key"]: f["label"] for f in CBC_FEATURES}
CBC_UNITS = {f["key"]: f["unit"] for f in CBC_FEATURES}
