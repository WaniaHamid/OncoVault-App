import os
import glob
import csv
import collections
import json

def audit_symptoms():
    print("=================================================================")
    print("               1. SYMPTOM DATASET AUDIT REPORT                  ")
    print("=================================================================")
    symptom_files = {
        'train.csv (Dhaka Shishu Hospital)': 'oncovault_ai/data/symptoms/train.csv',
        'test.csv (NICRH)': 'oncovault_ai/data/symptoms/test.csv'
    }
    
    expected_symptoms = [
        ("shortness_of_breath", "shortness of breath"),
        ("bone_pain", "bone_pain"),
        ("fever", "fever"),
        ("family_history", "family_history"),
        ("frequent_infections", "frequent_infections"),
        ("itchy_skin_rash", "Itchy_skin_or_rash"),
        ("loss_of_appetite_nausea", "loss_of_appetite_or_nausea"),
        ("persistent_weakness_fatigue", "Persistent_weakness _and_fatigue"),
        ("swollen_painless_lymph_nodes", "swollen,painless_lymph"),
        ("significant_bruising_bleeding", "significant_bruising,bleeding"),
        ("enlarged_liver", "enlarged_liver"),
        ("oral_cavity_changes", "oral_cavity"),
        ("vision_blurring", "vision_blurring"),
        ("jaundice", "jaundice"),
        ("night_sweats", "night_sweats"),
        ("smoking_history", "smokes")
    ]

    total_records = 0
    for name, path in symptom_files.items():
        if not os.path.exists(path):
            print(f"ERROR: File not found: {path}")
            continue
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = [r for r in reader if r and any(cell.strip() for cell in r)]
        
        total_records += len(rows)
        print(f"\n--- {name} ---")
        print(f"Path: {path}")
        print(f"Row count (excluding header): {len(rows)}")
        print(f"Number of columns: {len(header)}")
        print(f"Raw Column Names in CSV:")
        for idx, col in enumerate(header):
            print(f"  [{idx}] '{col}'")
        
        # Check label distribution
        label_col = header[-1]
        label_counts = collections.Counter(r[-1].strip() for r in rows)
        print(f"Target Column: '{label_col}'")
        for val, count in sorted(label_counts.items()):
            pct = (count / len(rows)) * 100
            label_name = "Leukemia (Positive)" if str(val) == "1" else "Non-Leukemia (Negative)"
            print(f"  Class '{val}' ({label_name}): {count} ({pct:.2f}%)")
        
        # Check missing values & binary encoding
        missing_per_col = collections.defaultdict(int)
        invalid_binary_per_col = collections.defaultdict(list)
        for r_idx, row in enumerate(rows):
            for c_idx, col in enumerate(header):
                val = row[c_idx].strip() if c_idx < len(row) else ''
                if val == '':
                    missing_per_col[col] += 1
                if c_idx > 0 and c_idx < len(header) - 1:
                    if val not in ('0', '1'):
                        invalid_binary_per_col[col].append((r_idx, val))
                        
        print(f"Missing Values: {dict(missing_per_col) if missing_per_col else '0 missing values across all cells'}")
        print(f"Binary Check: {'All symptom columns strictly binary {0, 1}' if not invalid_binary_per_col else dict(invalid_binary_per_col)}")
        
        # Check duplicates
        feature_tuples = [tuple(r[1:-1]) for r in rows]
        unique_features = len(set(feature_tuples))
        print(f"Unique Symptom Feature Combinations: {unique_features} (Duplicates: {len(rows) - unique_features})")
        
    print(f"\nTotal combined symptom records across Dhaka Shishu Hospital & NICRH: {total_records} (Expected: 840)")

    print("\nFeature Mapping Verification for OncoVault 16 Symptoms:")
    for onco_name, csv_name in expected_symptoms:
        print(f"  • OncoVault: '{onco_name}' <===> CSV: '{csv_name}'")

def audit_cbc():
    print("\n=================================================================")
    print("                 2. CBC DATASET AUDIT REPORT                     ")
    print("=================================================================")
    
    cbc_target_features = [
        ("WBC", "WBC(10^9/L)"),
        ("RBC", "RBC(10^12/L)"),
        ("HGB", "HGB(g/L)"),
        ("PLT", "PLT(10^9/L)"),
        ("NEUT#", "NEUT#(10^9/L)"),
        ("NEUT%", "NEUT%(%)"),
        ("MONO#", "MONO#(10^9/L)"),
        ("RDW-SD", "RDW-SD(fL)"),
        ("RDW-CV", "RDW-CV(%)")
    ]
    
    # Collect all CBC files
    train_files = sorted(glob.glob('oncovault_ai/data/cbc/training/*.csv'))
    valid_files = sorted(glob.glob('oncovault_ai/data/cbc/validation/*.csv'))
    test_files = sorted(glob.glob('oncovault_ai/data/cbc/test/*.csv'))
    
    all_groups = [
        ("Training Sites", train_files),
        ("Validation Sites", valid_files),
        ("Independent Test Sites", test_files)
    ]
    
    grand_total_rows = 0
    for group_name, file_list in all_groups:
        print(f"\n--- {group_name} ({len(file_list)} files) ---")
        for filepath in file_list:
            fname = os.path.basename(filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                rows = [r for r in reader if r and any(cell.strip() for cell in r)]
            
            grand_total_rows += len(rows)
            # Find target column
            target_col = None
            for cand in ['leukemia_label', 'label', 'target', 'leukemia', 'Class']:
                if cand in header:
                    target_col = cand
                    break
            
            target_idx = header.index(target_col) if target_col else -1
            label_counts = collections.Counter(r[target_idx].strip() for r in rows) if target_idx != -1 else {}
            
            # Check 9 target features existence and missing counts
            missing_9_features = {}
            for onco_feat, col_name in cbc_target_features:
                if col_name in header:
                    col_idx = header.index(col_name)
                    null_cnt = sum(1 for r in rows if col_idx >= len(r) or r[col_idx].strip() == '')
                    missing_9_features[onco_feat] = null_cnt
                else:
                    missing_9_features[onco_feat] = "MISSING_COLUMN"
            
            print(f"\nFile: {fname} (Path: {filepath})")
            print(f"  • Total Rows: {len(rows):,}")
            print(f"  • Total Columns in raw CSV: {len(header)}")
            print(f"  • Target Column: '{target_col}'")
            print(f"  • Label Distribution: {dict(label_counts)}")
            print(f"  • 9 Target CBC Features present: {'ALL 9 PRESENT' if all(v != 'MISSING_COLUMN' for v in missing_9_features.values()) else 'MISSING SOME'}")
            print(f"  • Missing values in 9 target features: {missing_9_features}")

    print(f"\nGrand Total CBC Rows across all sites: {grand_total_rows:,}")
    print("\nFeature Mapping Verification for OncoVault 9 CBC Features:")
    for onco_name, csv_name in cbc_target_features:
        print(f"  • OncoVault: '{onco_name}' <===> CSV: '{csv_name}'")

if __name__ == '__main__':
    audit_symptoms()
    audit_cbc()
