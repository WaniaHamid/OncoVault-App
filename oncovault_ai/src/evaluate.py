"""
OncoVault AI Engine - Model Evaluation & Metrics
Computes standardized academic metrics (Sensitivity, Specificity, F1, ROC-AUC, Confusion Matrix).
"""
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)
from sklearn.model_selection import StratifiedKFold

def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None) -> Dict[str, Any]:
    """
    Computes comprehensive binary classification metrics with clinical emphasis on sensitivity.
    """
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0) # Sensitivity
    f1 = f1_score(y_true, y_pred, zero_division=0)
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    
    auc = None
    if y_prob is not None and len(np.unique(y_true)) > 1:
        try:
            auc = roc_auc_score(y_true, y_prob)
        except Exception:
            auc = None
            
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
        "total_samples": int(len(y_true)),
        "positive_samples": int(tp + fn),
        "negative_samples": int(tn + fp)
    }

def cross_validate_model(model_cls, model_kwargs: dict, X: np.ndarray, y: np.ndarray, n_splits: int = 5, random_state: int = 42) -> Dict[str, Any]:
    """
    Performs Stratified K-Fold Cross Validation within training data only.
    """
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    
    fold_metrics = []
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
        X_train_fold, X_val_fold = X[train_idx], X[val_idx]
        y_train_fold, y_val_fold = y[train_idx], y[val_idx]
        
        clf = model_cls(**model_kwargs)
        clf.fit(X_train_fold, y_train_fold)
        
        preds = clf.predict(X_val_fold)
        probs = clf.predict_proba(X_val_fold)[:, 1] if hasattr(clf, "predict_proba") else None
        
        metrics = evaluate_predictions(y_val_fold, preds, probs)
        fold_metrics.append(metrics)
        
    avg_metrics = {
        "accuracy_mean": float(np.mean([m["accuracy"] for m in fold_metrics])),
        "accuracy_std": float(np.std([m["accuracy"] for m in fold_metrics])),
        "recall_sensitivity_mean": float(np.mean([m["recall_sensitivity"] for m in fold_metrics])),
        "recall_sensitivity_std": float(np.std([m["recall_sensitivity"] for m in fold_metrics])),
        "precision_mean": float(np.mean([m["precision"] for m in fold_metrics])),
        "precision_std": float(np.std([m["precision"] for m in fold_metrics])),
        "f1_mean": float(np.mean([m["f1_score"] for m in fold_metrics])),
        "f1_std": float(np.std([m["f1_score"] for m in fold_metrics])),
        "roc_auc_mean": float(np.mean([m["roc_auc"] for m in fold_metrics if m["roc_auc"] is not None])),
        "roc_auc_std": float(np.std([m["roc_auc"] for m in fold_metrics if m["roc_auc"] is not None])),
        "n_folds": n_splits
    }
    return avg_metrics
