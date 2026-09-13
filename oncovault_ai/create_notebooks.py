import json

def create_symptom_notebook():
    nb = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# OncoVault — Symptom Leukemia Risk Assessment Model (`leukemia-symptom-v1`)\n",
                    "### Google Colab Training & Academic Validation Notebook\n",
                    "\n",
                    "**Dataset Source:** *Symptom Based Explainable Artificial Intelligence Model for Leukemia Detection* (Akter et al., Bangladesh)\n",
                    "- **Training Cohort:** Dhaka Shishu Hospital ($N=709$, 510 leukemia, 199 non-leukemia)\n",
                    "- **Independent Test Cohort:** NICRH ($N=131$, 90 leukemia, 41 non-leukemia)\n",
                    "\n",
                    "> **Clinical Note:** This model is designed for Clinical Decision Support and risk screening in pediatric cohorts, not automated definitive diagnosis."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# 1. Setup Environment\n",
                    "import os, csv, json, joblib\n",
                    "import numpy as np\n",
                    "from sklearn.linear_model import LogisticRegression\n",
                    "from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier\n",
                    "from sklearn.model_selection import StratifiedKFold\n",
                    "from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix\n",
                    "print('Environment initialized successfully.')"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# 2. Define 16 Finalized Symptoms\n",
                    "SYMPTOM_COLS = [\n",
                    "    'shortness of breath', 'bone_pain', 'fever', 'family_history',\n",
                    "    'frequent_infections', 'Itchy_skin_or_rash', 'loss_of_appetite_or_nausea',\n",
                    "    'Persistent_weakness _and_fatigue', 'swollen,painless_lymph',\n",
                    "    'significant_bruising,bleeding', 'enlarged_liver', 'oral_cavity',\n",
                    "    'vision_blurring', 'jaundice', 'night_sweats', 'smokes'\n",
                    "]\n",
                    "\n",
                    "def load_symptoms(filepath):\n",
                    "    with open(filepath, 'r', encoding='utf-8') as f:\n",
                    "        reader = csv.reader(f)\n",
                    "        header = next(reader)\n",
                    "        col_indices = [header.index(c) for c in SYMPTOM_COLS]\n",
                    "        label_idx = header.index('leukemia')\n",
                    "        X, y = [], []\n",
                    "        for r in reader:\n",
                    "            if not r or not any(cell.strip() for cell in r): continue\n",
                    "            X.append([float(r[i].strip()) for i in col_indices])\n",
                    "            y.append(int(float(r[label_idx].strip())))\n",
                    "    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int32)\n",
                    "\n",
                    "# Load datasets (adjust paths as needed)\n",
                    "X_train, y_train = load_symptoms('oncovault_ai/data/symptoms/train.csv')\n",
                    "X_test, y_test = load_symptoms('oncovault_ai/data/symptoms/test.csv')\n",
                    "print(f'Training subjects (Dhaka Shishu Hospital): {len(X_train)}')\n",
                    "print(f'Independent test subjects (NICRH):         {len(X_test)}')"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# 3. 5-Fold Stratified Cross Validation on Training Data Only\n",
                    "skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)\n",
                    "models = {\n",
                    "    'Logistic Regression (Balanced)': LogisticRegression(class_weight='balanced', random_state=42, max_iter=1000),\n",
                    "    'Logistic Regression (Default)':  LogisticRegression(random_state=42, max_iter=1000),\n",
                    "    'Random Forest':                 RandomForestClassifier(n_estimators=100, max_depth=6, class_weight='balanced', random_state=42),\n",
                    "    'Gradient Boosting':             GradientBoostingClassifier(n_estimators=100, learning_rate=0.05, max_depth=3, random_state=42)\n",
                    "}\n",
                    "\n",
                    "print(f\"{'Model':<30} | {'Accuracy':<10} | {'Sensitivity':<12} | {'Precision':<10} | {'F1':<8} | {'ROC-AUC':<10}\")\n",
                    "print('-'*88)\n",
                    "for name, model in models.items():\n",
                    "    accs, recs, precs, f1s, aucs = [], [], [], [], []\n",
                    "    for tr_idx, val_idx in skf.split(X_train, y_train):\n",
                    "        clf = model.__class__(**model.get_params())\n",
                    "        clf.fit(X_train[tr_idx], y_train[tr_idx])\n",
                    "        preds = clf.predict(X_train[val_idx])\n",
                    "        probs = clf.predict_proba(X_train[val_idx])[:, 1]\n",
                    "        accs.append(accuracy_score(y_train[val_idx], preds))\n",
                    "        recs.append(recall_score(y_train[val_idx], preds))\n",
                    "        precs.append(precision_score(y_train[val_idx], preds))\n",
                    "        f1s.append(f1_score(y_train[val_idx], preds))\n",
                    "        aucs.append(roc_auc_score(y_train[val_idx], probs))\n",
                    "    print(f\"{name:<30} | {np.mean(accs):.4f}     | {np.mean(recs):.4f}       | {np.mean(precs):.4f}     | {np.mean(f1s):.4f}   | {np.mean(aucs):.4f}\")"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# 4. Final Fit and Independent Evaluation on NICRH Test Set\n",
                    "final_symptom_model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.05, max_depth=3, random_state=42)\n",
                    "final_symptom_model.fit(X_train, y_train)\n",
                    "\n",
                    "test_preds = final_symptom_model.predict(X_test)\n",
                    "test_probs = final_symptom_model.predict_proba(X_test)[:, 1]\n",
                    "cm = confusion_matrix(y_test, test_preds)\n",
                    "tn, fp, fn, tp = cm.ravel()\n",
                    "\n",
                    "print('=== NICRH INDEPENDENT TEST RESULTS ===')\n",
                    "print(f'Accuracy:             {accuracy_score(y_test, test_preds):.4f}')\n",
                    "print(f'Recall / Sensitivity: {recall_score(y_test, test_preds):.4f}')\n",
                    "print(f'Specificity:          {tn/(tn+fp):.4f}')\n",
                    "print(f'Precision:            {precision_score(y_test, test_preds):.4f}')\n",
                    "print(f'F1-Score:             {f1_score(y_test, test_preds):.4f}')\n",
                    "print(f'ROC-AUC:              {roc_auc_score(y_test, test_probs):.4f}')\n",
                    "print(f'Confusion Matrix:     TN={tn}, FP={fp}, FN={fn}, TP={tp}')"
                ]
            }
        ],
        "metadata": {
            "language_info": {"name": "python", "version": "3.10"},
            "orig_nbformat": 4
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }
    with open("oncovault_ai/notebooks/train_symptom_colab.ipynb", "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2)

def create_cbc_notebook():
    nb = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# OncoVault — CBC Leukemia Risk Assessment Model (`leukemia-cbc-v1`)\n",
                    "### Google Colab Training & Multi-Site Evaluation Notebook\n",
                    "\n",
                    "- **Training Cohort:** 3 Multi-Site Training Datasets ($N=26,922$ subjects)\n",
                    "- **Validation Cohort:** 7 Independent Validation Sites ($N=361,260$ subjects)\n",
                    "- **Independent Test Cohort:** True-World Test Site ($N=58,481$ subjects)\n",
                    "\n",
                    "> **Clinical Note:** Uses exactly the 9 finalized OncoVault CBC features (`WBC`, `RBC`, `HGB`, `PLT`, `NEUT#`, `NEUT%`, `MONO#`, `RDW-SD`, `RDW-CV`)."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# 1. Setup Environment & Imports\n",
                    "import os, csv, glob, json, joblib\n",
                    "import numpy as np\n",
                    "from sklearn.preprocessing import StandardScaler\n",
                    "from sklearn.linear_model import LogisticRegression\n",
                    "from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier\n",
                    "from sklearn.model_selection import StratifiedKFold\n",
                    "from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix\n",
                    "print('Environment initialized.')"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# 2. Load 9 Finalized CBC Features\n",
                    "CBC_COLS = ['WBC(10^9/L)', 'RBC(10^12/L)', 'HGB(g/L)', 'PLT(10^9/L)', 'NEUT#(10^9/L)', 'NEUT%(%)', 'MONO#(10^9/L)', 'RDW-SD(fL)', 'RDW-CV(%)']\n",
                    "\n",
                    "def load_cbc_file(filepath):\n",
                    "    with open(filepath, 'r', encoding='utf-8') as f:\n",
                    "        reader = csv.reader(f)\n",
                    "        header = next(reader)\n",
                    "        col_indices = [header.index(c) for c in CBC_COLS]\n",
                    "        label_idx = header.index('leukemia_label')\n",
                    "        X, y = [], []\n",
                    "        for r in reader:\n",
                    "            if not r or not any(cell.strip() for cell in r): continue\n",
                    "            X.append([float(r[i].strip()) for i in col_indices])\n",
                    "            y.append(1 if r[label_idx].strip().lower() in ['leukemia', '1', 'positive'] else 0)\n",
                    "    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int32)\n",
                    "\n",
                    "train_files = sorted(glob.glob('oncovault_ai/data/cbc/training/*.csv'))\n",
                    "X_train_raw = np.vstack([load_cbc_file(fp)[0] for fp in train_files])\n",
                    "y_train = np.concatenate([load_cbc_file(fp)[1] for fp in train_files])\n",
                    "print(f'Training records across {len(train_files)} sites: {len(X_train_raw):,}')"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# 3. Preprocessing Scaler (Fitted ONLY on Training Sites)\n",
                    "scaler = StandardScaler()\n",
                    "X_train = scaler.fit_transform(X_train_raw)\n",
                    "\n",
                    "# Train Final Gradient Boosting Model\n",
                    "cbc_model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)\n",
                    "cbc_model.fit(X_train, y_train)\n",
                    "print('CBC Model training complete.')"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# 4. Evaluate on Independent Test Site\n",
                    "X_test_raw, y_test = load_cbc_file('oncovault_ai/data/cbc/test/test_site_true_world.csv')\n",
                    "X_test = scaler.transform(X_test_raw)\n",
                    "preds = cbc_model.predict(X_test)\n",
                    "probs = cbc_model.predict_proba(X_test)[:, 1]\n",
                    "cm = confusion_matrix(y_test, preds)\n",
                    "tn, fp, fn, tp = cm.ravel()\n",
                    "\n",
                    "print('=== TRUE-WORLD INDEPENDENT TEST RESULTS ===')\n",
                    "print(f'Accuracy:             {accuracy_score(y_test, preds):.4f}')\n",
                    "print(f'Recall / Sensitivity: {recall_score(y_test, preds):.4f}')\n",
                    "print(f'Specificity:          {tn/(tn+fp):.4f}')\n",
                    "print(f'Precision:            {precision_score(y_test, preds):.4f}')\n",
                    "print(f'F1-Score:             {f1_score(y_test, preds):.4f}')\n",
                    "print(f'ROC-AUC:              {roc_auc_score(y_test, probs):.4f}')\n",
                    "print(f'Confusion Matrix:     TN={tn}, FP={fp}, FN={fn}, TP={tp}')"
                ]
            }
        ],
        "metadata": {
            "language_info": {"name": "python", "version": "3.10"},
            "orig_nbformat": 4
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }
    with open("oncovault_ai/notebooks/train_cbc_colab.ipynb", "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2)

create_symptom_notebook()
create_cbc_notebook()
print("Notebooks created successfully.")
