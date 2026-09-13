# OncoVault — Phase 3: AI Diagnostic & Decision Support Engine

## 1. Overview & Clinical Purpose
The **OncoVault AI Diagnostic Engine** is an assistive **Clinical Decision Support System (CDSS)** designed to evaluate leukemia risk profiles from structured Electronic Health Record (EHR) data. 

> **Important Clinical Scope & Disclaimer:**
> The AI engine provides risk stratification ("Elevated Risk" vs. "Lower Risk") to assist clinicians during intake and follow-up. It is **not** an automated diagnostic system, does not replace bone marrow aspirate/biopsy or specialist pathologist review, and does not alter chemotherapy prescriptions or treatment plans. A doctor remains in the loop at all times.

---

## 2. Independent Dataset Architecture
To prevent artificial data synthesis and false correlation assumptions, OncoVault trains and serves two completely independent models on separate clinical cohorts:

```
                            OncoVault EHR
                                 │
                ┌────────────────┴────────────────┐
                │                                 │
          16 Symptoms                        9 CBC Features
                │                                 │
                ▼                                 ▼
      Symptom Risk Model                 CBC Risk Model
       (Dhaka Shishu 709)               (Multi-Site 26.9k)
                │                                 │
                ▼                                 ▼
       Symptom Risk Score                 CBC Risk Score
       (leukemia-symptom-v1)              (leukemia-cbc-v1)
                │                                 │
                └────────────────┬────────────────┘
                                 ▼
                      Doctor-in-the-Loop Review
                                 │
                                 ▼
                     Firestore EHR AI Metadata
```

---

## 3. Dataset A: Symptom Dataset

### Source & Structure
- **Origin:** Pediatric leukemia research study (*"Symptom Based Explainable Artificial Intelligence Model for Leukemia Detection"*, Akter et al., Bangladesh). Public repository: `https://github.com/akterhossain312/leukemiadataset`.
- **Total Patients:** 840 subjects (600 leukemia, 240 non-leukemia).
- **Hospital-Separated Split (Strictly Preserved):**
  - **Training Set (`train.csv`):** **Dhaka Shishu Hospital** (709 patients: 510 leukemia, 199 non-leukemia).
  - **Independent External Test Set (`test.csv`):** **NICRH** (131 patients: 90 leukemia, 41 non-leukemia).
- **Pediatric Limitation:** Data was collected exclusively from pediatric wards in Bangladesh. It represents pediatric hematologic presentations and should not be generalized across all adult age groups or global demographics.

### Finalized 16 Symptom Features
1. `shortness_of_breath` (`shortness of breath`)
2. `bone_pain` (`bone_pain`)
3. `fever` (`fever`)
4. `family_history` (`family_history`)
5. `frequent_infections` (`frequent_infections`)
6. `itchy_skin_rash` (`Itchy_skin_or_rash`)
7. `loss_of_appetite_nausea` (`loss_of_appetite_or_nausea`)
8. `persistent_weakness_fatigue` (`Persistent_weakness _and_fatigue`)
9. `swollen_painless_lymph_nodes` (`swollen,painless_lymph`)
10. `significant_bruising_bleeding` (`significant_bruising,bleeding`)
11. `enlarged_liver` (`enlarged_liver`)
12. `oral_cavity_changes` (`oral_cavity`)
13. `vision_blurring` (`vision_blurring`)
14. `jaundice` (`jaundice`)
15. `night_sweats` (`night_sweats`)
16. `smoking_history` (`smokes`)

---

## 4. Dataset B: CBC Dataset

### Source & Structure
- Multi-site hematology analyzer datasets containing 446,663 total patient records across 11 files.
- **Training Sites (3 files):** `train_site_A.csv`, `train_site_B.csv`, `train_site_C.csv` (26,922 patients: 8,974 leukemia, 17,948 healthy).
- **Validation Sites (7 files):** `valid_site_A.csv` through `valid_site_G.csv` (361,260 patients).
- **Independent Test Site (1 file):** `test_site_true_world.csv` (58,481 patients: 2,290 leukemia, 56,191 healthy).

### Finalized 9 CBC Features
1. `WBC` (`WBC(10^9/L)`): White Blood Cell Count
2. `RBC` (`RBC(10^12/L)`): Red Blood Cell Count
3. `HGB` (`HGB(g/L)`): Hemoglobin
4. `PLT` (`PLT(10^9/L)`): Platelet Count
5. `NEUT#` (`NEUT#(10^9/L)`): Absolute Neutrophil Count
6. `NEUT%` (`NEUT%(%)`): Neutrophil Percentage
7. `MONO#` (`MONO#(10^9/L)`): Absolute Monocyte Count
8. `RDW-SD` (`RDW-SD(fL)`): Red Cell Distribution Width (SD)
9. `RDW-CV` (`RDW-CV(%)`): Red Cell Distribution Width (CV)

---

## 5. Preprocessing & Leakage Prevention
- **Leakage Elimination:** All preprocessors (`StandardScaler`) are fitted strictly on the respective training datasets (`X_train`). Independent validation cohorts and test sets (`NICRH`, `test_site_true_world.csv`) are transformed using the already-fitted scaler.
- **Cross-Validation:** 5-Fold Stratified Cross-Validation performed entirely within training records.

---

## 6. Model Evaluation & Comparison Results

### Symptom Model Comparison (5-Fold Stratified CV on Dhaka Shishu Hospital, N=709)

| Model | Accuracy | Sensitivity (Recall) | Precision | F1-Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Logistic Regression (Balanced) | 92.95% | 92.16% | 97.92% | 0.9492 | 0.9873 |
| Logistic Regression (Default) | 94.36% | 96.67% | 95.57% | 0.9610 | 0.9870 |
| Random Forest | 93.37% | 93.53% | 97.16% | 0.9528 | 0.9881 |
| **Gradient Boosting (Selected)** | **94.50%** | **96.27%** | **96.09%** | **0.9617** | **0.9901** |

#### Symptom Model Independent Test (NICRH, N=131)
- **Accuracy:** **93.13%**
- **Sensitivity / Recall:** **94.44%**
- **Specificity:** **90.24%**
- **Precision:** **95.51%**
- **F1-Score:** **0.9497**
- **ROC-AUC:** **0.9867**
- **Confusion Matrix:** $TN=37, FP=4, FN=5, TP=85$

---

### CBC Model Comparison (5-Fold Stratified CV on Multi-Site Training, N=26,922)

| Model | Accuracy | Sensitivity (Recall) | Precision | F1-Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Logistic Regression | 84.72% | 83.42% | 74.03% | 0.7844 | 0.9125 |
| Random Forest | 90.17% | 89.64% | 82.42% | 0.8587 | 0.9619 |
| **Gradient Boosting (Selected)** | **90.87%** | **85.90%** | **86.60%** | **0.8625** | **0.9644** |

#### CBC Model Independent Test (True-World Test Site, N=58,481)
- **Accuracy:** **92.75%**
- **Sensitivity / Recall:** **88.73%**
- **Specificity:** **92.91%**
- **Precision:** **33.79%** (reflecting true-world low population disease prevalence)
- **ROC-AUC:** **0.9643**
- **Confusion Matrix:** $TN=52,209, FP=3,982, FN=258, TP=2,032$

---

## 7. Model Explainability & Contributing Factors

### Top Contributing Symptoms (`leukemia-symptom-v1`)
1. **Swollen Painless Lymph Nodes** (Importance: 0.1665)
2. **Frequent Infections** (Importance: 0.1635)
3. **Enlarged Liver / Hepatomegaly** (Importance: 0.1514)
4. **Bone Pain** (Importance: 0.1433)
5. **Persistent Weakness & Fatigue** (Importance: 0.1048)
6. **Jaundice** (Importance: 0.0680)
7. **Loss of Appetite / Nausea** (Importance: 0.0679)
8. **Family History of Cancer** (Importance: 0.0637)

### Top Contributing CBC Parameters (`leukemia-cbc-v1`)
1. **Platelet Count** (Importance: 0.5355)
2. **White Blood Cell Count** (Importance: 0.1622)
3. **Absolute Monocyte Count (MONO#)** (Importance: 0.0846)
4. **Red Cell Distribution Width (SD)** (Importance: 0.0566)
5. **Red Blood Cell Count** (Importance: 0.0542)
6. **Absolute Neutrophil Count (NEUT#)** (Importance: 0.0426)

---

## 8. FastAPI Endpoints

### 1. Symptom Risk Assessment
`POST /predict-symptoms`

**Request:**
```json
{
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
```

**Response:**
```json
{
  "prediction": "Elevated Risk",
  "riskScore": 0.9421,
  "modelVersion": "leukemia-symptom-v1",
  "contributingFactors": [
    "Swollen Painless Lymph Nodes",
    "Frequent Infections",
    "Enlarged Liver / Hepatomegaly",
    "Bone Pain",
    "Persistent Weakness & Fatigue"
  ],
  "analyzedAt": "2026-09-11T12:00:00Z",
  "disclaimer": "AI risk assessment is for clinical decision support and is not a definitive medical diagnosis."
}
```

### 2. CBC Risk Assessment
`POST /predict-cbc`

**Request:**
```json
{
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
```

**Response:**
```json
{
  "prediction": "Elevated Risk",
  "riskScore": 0.8845,
  "modelVersion": "leukemia-cbc-v1",
  "contributingFactors": [
    "Platelet Count (10^9/L)",
    "White Blood Cell Count (10^9/L)",
    "Absolute Monocyte Count (MONO#) (10^9/L)",
    "Red Cell Distribution Width (SD) (fL)"
  ],
  "analyzedAt": "2026-09-11T12:00:00Z",
  "disclaimer": "AI risk assessment is for clinical decision support and is not a definitive medical diagnosis."
}
```

---

## 9. Flutter Doctor-in-the-Loop Integration
- **`AiRiskAssessmentService` (`lib/services/ai_risk_assessment_service.dart`):** Manages API communication with configurable fallback heuristics.
- **`AiDiagnosisScreen` (`lib/screens/doctor/ai_diagnosis_screen.dart`):** Dual assessment view featuring distinct Symptom and CBC risk cards, risk percentage progress meters, and dynamic contributing factor tags.
- **Doctor Review Action:** Clinicians review AI findings and click **"Confirm Doctor Review & Save to EHR"**, committing `AiAnalysisMetadata` (`prediction`, `riskScore`, `modelVersion`, `doctorReviewed: true`, `analyzedAt`) into Firestore.
- **Zero Phase 1 & 2 Regressions:** Preserves all EHR viewing/editing, voice dictation, Whisper transcription, and MedSpaCy concept extraction pipelines.
