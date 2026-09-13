"""
OncoVault AI Engine - Preprocessing & Dataset Loaders
Ensures strict leakage prevention by fitting preprocessors ONLY on training sets.
"""
import os
import csv
import numpy as np
from typing import Tuple, List, Dict, Any
from .feature_mapping import (
    SYMPTOM_KEYS, SYMPTOM_CSV_COLS,
    CBC_KEYS, CBC_CSV_COLS
)

def load_symptom_csv(filepath: str) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    Loads a symptom CSV dataset and extracts the 16 finalized features and binary label.
    Returns: (X, y, feature_keys)
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Symptom file not found: {filepath}")
        
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        # Build index mapping for the 16 CSV columns
        col_indices = []
        for csv_col in SYMPTOM_CSV_COLS:
            if csv_col not in header:
                raise ValueError(f"Missing required symptom column '{csv_col}' in {filepath}")
            col_indices.append(header.index(csv_col))
            
        label_idx = header.index("leukemia") if "leukemia" in header else -1
        if label_idx == -1:
            raise ValueError(f"Target column 'leukemia' not found in {filepath}")
            
        X_list = []
        y_list = []
        for row in reader:
            if not row or not any(cell.strip() for cell in row):
                continue
            features = [float(row[idx].strip()) for idx in col_indices]
            label = int(float(row[label_idx].strip()))
            X_list.append(features)
            y_list.append(label)
            
    return np.array(X_list, dtype=np.float32), np.array(y_list, dtype=np.int32), SYMPTOM_KEYS

def load_cbc_csv(filepath: str) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    Loads a CBC CSV dataset and extracts the 9 finalized features and binary label.
    Maps 'leukemia' -> 1, 'healthy' -> 0.
    Returns: (X, y, feature_keys)
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"CBC file not found: {filepath}")
        
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        col_indices = []
        for csv_col in CBC_CSV_COLS:
            if csv_col not in header:
                raise ValueError(f"Missing required CBC column '{csv_col}' in {filepath}")
            col_indices.append(header.index(csv_col))
            
        target_col = None
        for cand in ['leukemia_label', 'label', 'target', 'leukemia']:
            if cand in header:
                target_col = cand
                break
        if not target_col:
            raise ValueError(f"Target column not found in {filepath}")
        label_idx = header.index(target_col)
        
        X_list = []
        y_list = []
        for row in reader:
            if not row or not any(cell.strip() for cell in row):
                continue
            features = [float(row[idx].strip()) for idx in col_indices]
            raw_label = row[label_idx].strip().lower()
            label = 1 if raw_label in ['leukemia', '1', 'positive'] else 0
            X_list.append(features)
            y_list.append(label)
            
    return np.array(X_list, dtype=np.float32), np.array(y_list, dtype=np.int32), CBC_KEYS

def load_multi_site_cbc(file_paths: List[str]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    Loads and concatenates multiple CBC site datasets.
    """
    all_X = []
    all_y = []
    for fp in file_paths:
        X, y, keys = load_cbc_csv(fp)
        all_X.append(X)
        all_y.append(y)
    return np.vstack(all_X), np.concatenate(all_y), CBC_KEYS
