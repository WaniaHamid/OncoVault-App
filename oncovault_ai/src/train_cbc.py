import os
import sys
import glob
import json
import joblib
import numpy as np
from datetime import datetime, timezone
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

sys.path.insert(0, os.path.abspath("."))
from oncovault_ai.src.feature_mapping import CBC_KEYS, CBC_LABELS, CBC_UNITS
from oncovault_ai.src.preprocessing import load_cbc_csv, load_multi_site_cbc

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
    print("           STAGE 3: CBC LEUKEMIA RISK MODEL TRAINING             ")
    print("=================================================================")
    
    train_files = sorted(glob.glob("oncovault_ai/data/cbc/training/*.csv"))
    valid_files = sorted(glob.glob("oncovault_ai/data/cbc/validation/*.csv"))
    test_file = "oncovault_ai/data/cbc/test/test_site_true_world.csv"
    output_dir = "oncovault_ai/models/leukemia_cbc_v1"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Load Training Multi-Site Data
    print(f"Loading training data from {len(train_files)} sites...")
    X_train_raw, y_train, feat_keys = load_multi_site_cbc(train_files)
    print(f"Loaded Training Data: {len(X_train_raw):,} records (Leukemia: {np.sum(y_train==1):,}, Healthy: {np.sum(y_train==0):,})")
    
    # 2. Strict Preprocessing Pipeline: Fit Scaler ONLY on Training Data
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train_raw)
    
    # 3. Model Candidates
    models = {
        "Logistic Regression": (
            LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
        ),
        "Random Forest": (
            RandomForestClassifier(n_estimators=100, max_depth=8, class_weight="balanced", random_state=42, n_jobs=1)
        ),
        "Gradient Boosting": (
            GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
        )
    }
    
    # 4. 5-Fold Stratified Cross-Validation on Training Data
    print("\n--- 5-Fold Stratified Cross-Validation (Training Sites Only) ---")
    print(f"{'Model':<25} | {'Accuracy':<10} | {'Sensitivity':<12} | {'Precision':<10} | {'F1-Score':<10} | {'ROC-AUC':<10}")
    print("-" * 88)
    
    cv_summary = {}
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for name, model in models.items():
        fold_metrics = []
        for train_idx, val_idx in skf.split(X_train, y_train):
            X_tr, X_val = X_train[train_idx], X_train[val_idx]
            y_tr, y_val = y_train[train_idx], y_train[val_idx]
            
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
        print(f"{name:<25} | {acc_m:.4f}     | {rec_m:.4f}       | {prec_m:.4f}     | {f1_m:.4f}     | {auc_m:.4f}")
        
    # 5. Fit Final Selected Model (Gradient Boosting / Random Forest) on ALL Training Data
    best_name = "Gradient Boosting"
    print(f"\nSelected Final Model: {best_name}")
    final_model = models[best_name]
    final_model.fit(X_train, y_train)
    
    # 6. Evaluation across 7 Independent Validation Sites
    print(f"\n--- Evaluation across 7 Independent Validation Sites (N=361,260 subjects) ---")
    valid_site_results = {}
    print(f"{'Site File':<20} | {'Samples':<9} | {'Accuracy':<10} | {'Sensitivity':<12} | {'Precision':<10} | {'F1-Score':<10} | {'ROC-AUC':<10}")
    print("-" * 92)
    
    for vf in valid_files:
        v_name = os.path.basename(vf)
        X_v_raw, y_v, _ = load_cbc_csv(vf)
        X_v = scaler.transform(X_v_raw) # Transform using training-fitted scaler
        v_preds = final_model.predict(X_v)
        v_probs = final_model.predict_proba(X_v)[:, 1]
        v_metrics = evaluate_preds(y_v, v_preds, v_probs)
        valid_site_results[v_name] = v_metrics
        print(f"{v_name:<20} | {len(y_v):<9,d} | {v_metrics['accuracy']:.4f}     | {v_metrics['recall_sensitivity']:.4f}       | {v_metrics['precision']:.4f}     | {v_metrics['f1_score']:.4f}     | {v_metrics['roc_auc']:.4f}")
        
    # 7. Evaluation on Independent Test Site (test_site_true_world.csv)
    print(f"\n--- Independent Evaluation on True-World Test Site (N=58,481 subjects) ---")
    X_test_raw, y_test, _ = load_cbc_csv(test_file)
    X_test = scaler.transform(X_test_raw)
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
    
    # 8. Feature Importance for 9 CBC Features
    if hasattr(final_model, "feature_importances_"):
        imps = final_model.feature_importances_
    else:
        imps = np.ones(len(feat_keys))
        
    feat_imp_list = []
    for k, imp in zip(feat_keys, imps):
        feat_imp_list.append({
            "feature_key": k,
            "label": CBC_LABELS[k],
            "unit": CBC_UNITS[k],
            "importance": float(imp)
        })
    feat_imp_list.sort(key=lambda x: x["importance"], reverse=True)
    
    print("\n--- Contributing CBC Parameter Ranking (Feature Importance) ---")
    for rk, f in enumerate(feat_imp_list, 1):
        print(f"  {rk:2d}. {f['label']:<36} ({f['unit']:<7}): {f['importance']:.4f}")
        
    # 9. Save Model Artifacts
    joblib.dump(final_model, os.path.join(output_dir, "model.joblib"))
    joblib.dump(scaler, os.path.join(output_dir, "scaler.joblib"))
    
    metadata = {
        "model_version": "leukemia-cbc-v1",
        "algorithm": best_name,
        "algorithm_class": final_model.__class__.__name__,
        "hyperparameters": final_model.get_params(),
        "training_dataset": f"Multi-Site CBC Training Cohort ({len(train_files)} sites)",
        "training_samples": len(X_train_raw),
        "validation_dataset": f"Multi-Site CBC Validation Cohort ({len(valid_files)} sites, 361,260 samples)",
        "independent_test_dataset": "True-World Independent Test Site (58,481 samples)",
        "features": feat_keys,
        "feature_labels": CBC_LABELS,
        "feature_units": CBC_UNITS,
        "target_mapping": {"0": "Healthy (Lower Risk)", "1": "Leukemia (Elevated Risk)"},
        "disclaimer": "AI risk assessment is for clinical decision support and is not a definitive diagnosis.",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    with open(os.path.join(output_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    with open(os.path.join(output_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump({
            "cross_validation": cv_summary,
            "validation_sites": valid_site_results,
            "independent_test": test_metrics
        }, f, indent=2)
        
    with open(os.path.join(output_dir, "feature_importance.json"), "w", encoding="utf-8") as f:
        json.dump(feat_imp_list, f, indent=2)
        
    print(f"\n[SUCCESS] Stage 3 Artifacts saved to {output_dir}")

if __name__ == "__main__":
    run()
