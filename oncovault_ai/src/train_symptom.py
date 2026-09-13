import os
import sys
import json
import joblib
import numpy as np
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

sys.path.insert(0, os.path.abspath("."))
from oncovault_ai.src.feature_mapping import SYMPTOM_KEYS, SYMPTOM_LABELS
from oncovault_ai.src.preprocessing import load_symptom_csv

def evaluate_preds(y_true, y_pred, y_prob=None):
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    auc = roc_auc_score(y_true, y_prob) if y_prob is not None and len(np.unique(y_true)) > 1 else None
    return {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall_sensitivity": float(rec),
        "specificity": float(spec),
        "f1_score": float(f1),
        "roc_auc": float(auc) if auc is not None else None,
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
            "raw_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]]
        },
        "total_samples": int(len(y_true))
    }

def run():
    print("=================================================================")
    print("        STAGE 2: SYMPTOM LEUKEMIA RISK MODEL TRAINING           ")
    print("=================================================================")
    
    train_path = "oncovault_ai/data/symptoms/train.csv"
    test_path = "oncovault_ai/data/symptoms/test.csv"
    output_dir = "oncovault_ai/models/leukemia_symptom_v1"
    os.makedirs(output_dir, exist_ok=True)
    
    X_train, y_train, feat_keys = load_symptom_csv(train_path)
    X_test, y_test, _ = load_symptom_csv(test_path)
    
    print(f"Loaded Training Set (Dhaka Shishu Hospital): {len(X_train)} subjects (Leukemia: {np.sum(y_train==1)}, Non-Leukemia: {np.sum(y_train==0)})")
    print(f"Loaded Independent Test Set (NICRH):         {len(X_test)} subjects (Leukemia: {np.sum(y_test==1)}, Non-Leukemia: {np.sum(y_test==0)})")
    
    models = {
        "Logistic Regression (Balanced)": (
            LogisticRegression(class_weight="balanced", random_state=42, max_iter=1000)
        ),
        "Logistic Regression (Default)": (
            LogisticRegression(random_state=42, max_iter=1000)
        ),
        "Random Forest": (
            RandomForestClassifier(n_estimators=100, max_depth=6, class_weight="balanced", random_state=42, n_jobs=1)
        ),
        "Gradient Boosting": (
            GradientBoostingClassifier(n_estimators=100, learning_rate=0.05, max_depth=3, random_state=42)
        )
    }
    
    print("\n--- 5-Fold Stratified Cross-Validation (Training Set Only) ---")
    print(f"{'Model':<32} | {'Accuracy':<10} | {'Sensitivity':<12} | {'Precision':<10} | {'F1-Score':<10} | {'ROC-AUC':<10}")
    print("-" * 95)
    
    cv_summary = {}
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for name, model in models.items():
        fold_metrics = []
        for train_idx, val_idx in skf.split(X_train, y_train):
            X_tr, X_val = X_train[train_idx], X_train[val_idx]
            y_tr, y_val = y_train[train_idx], y_train[val_idx]
            
            # clone model
            from sklearn.base import clone
            clf = clone(model)
            clf.fit(X_tr, y_tr)
            preds = clf.predict(X_val)
            probs = clf.predict_proba(X_val)[:, 1] if hasattr(clf, "predict_proba") else None
            fold_metrics.append(evaluate_preds(y_val, preds, probs))
            
        acc_m = np.mean([m["accuracy"] for m in fold_metrics])
        rec_m = np.mean([m["recall_sensitivity"] for m in fold_metrics])
        prec_m = np.mean([m["precision"] for m in fold_metrics])
        f1_m = np.mean([m["f1_score"] for m in fold_metrics])
        auc_m = np.mean([m["roc_auc"] for m in fold_metrics if m["roc_auc"] is not None])
        
        cv_summary[name] = {
            "accuracy_mean": float(acc_m),
            "recall_sensitivity_mean": float(rec_m),
            "precision_mean": float(prec_m),
            "f1_mean": float(f1_m),
            "roc_auc_mean": float(auc_m)
        }
        print(f"{name:<32} | {acc_m:.4f}     | {rec_m:.4f}       | {prec_m:.4f}     | {f1_m:.4f}     | {auc_m:.4f}")
        
    # Selection: Random Forest and Gradient Boosting both show strong generalization
    best_name = "Gradient Boosting"
    print(f"\nSelected Final Model: {best_name}")
    final_model = models[best_name]
    final_model.fit(X_train, y_train)
    
    # Independent Test Evaluation on NICRH (131 patients)
    print("\n--- Independent External Evaluation on NICRH Test Set (N=131) ---")
    test_preds = final_model.predict(X_test)
    test_probs = final_model.predict_proba(X_test)[:, 1]
    test_metrics = evaluate_preds(y_test, test_preds, test_probs)
    
    print(f"Accuracy:            {test_metrics['accuracy']:.4f} ({test_metrics['accuracy']*100:.2f}%)")
    print(f"Recall / Sensitivity:{test_metrics['recall_sensitivity']:.4f} ({test_metrics['recall_sensitivity']*100:.2f}%)")
    print(f"Specificity:         {test_metrics['specificity']:.4f} ({test_metrics['specificity']*100:.2f}%)")
    print(f"Precision:           {test_metrics['precision']:.4f} ({test_metrics['precision']*100:.2f}%)")
    print(f"F1-Score:            {test_metrics['f1_score']:.4f}")
    print(f"ROC-AUC:             {test_metrics['roc_auc']:.4f}")
    print(f"Confusion Matrix:    TN={test_metrics['confusion_matrix']['true_negatives']}, FP={test_metrics['confusion_matrix']['false_positives']}, FN={test_metrics['confusion_matrix']['false_negatives']}, TP={test_metrics['confusion_matrix']['true_positives']}")
    
    # Feature Importance
    if hasattr(final_model, "feature_importances_"):
        imps = final_model.feature_importances_
    else:
        imps = np.ones(len(feat_keys))
        
    feat_imp_list = []
    for k, imp in zip(feat_keys, imps):
        feat_imp_list.append({
            "feature_key": k,
            "label": SYMPTOM_LABELS[k],
            "importance": float(imp)
        })
    feat_imp_list.sort(key=lambda x: x["importance"], reverse=True)
    
    print("\n--- Contributing Symptom Ranking (Feature Importance) ---")
    for rk, f in enumerate(feat_imp_list, 1):
        print(f"  {rk:2d}. {f['label']:<34} : {f['importance']:.4f}")
        
    # Save Model Artifacts
    joblib.dump(final_model, os.path.join(output_dir, "model.joblib"))
    
    metadata = {
        "model_version": "leukemia-symptom-v1",
        "algorithm": best_name,
        "algorithm_class": final_model.__class__.__name__,
        "hyperparameters": final_model.get_params(),
        "training_dataset": "Dhaka Shishu Hospital (Pediatric Leukemia Dataset, Bangladesh)",
        "training_samples": len(X_train),
        "independent_test_dataset": "NICRH (National Institute of Cancer Research & Hospital)",
        "test_samples": len(X_test),
        "features": feat_keys,
        "feature_labels": SYMPTOM_LABELS,
        "target_mapping": {"0": "Non-Leukemia (Lower Risk)", "1": "Leukemia (Elevated Risk)"},
        "pediatric_limitation": "Source data originates from pediatric leukemia wards. Serves as clinical decision support only.",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    with open(os.path.join(output_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    with open(os.path.join(output_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump({"cross_validation": cv_summary, "independent_test": test_metrics}, f, indent=2)
        
    with open(os.path.join(output_dir, "feature_importance.json"), "w", encoding="utf-8") as f:
        json.dump(feat_imp_list, f, indent=2)
        
    print(f"\n[SUCCESS] Stage 2 Artifacts saved to {output_dir}")

if __name__ == "__main__":
    run()
