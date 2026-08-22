import os
import sys
import json
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# ==============================================================================
# DIRECTORY & FILE PATHS
# ==============================================================================

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BACKEND_DIR, "dataset", "experimental_data.csv")
MODEL_DIR = os.path.join(BACKEND_DIR, "model")
MODEL_SAVE_PATH = os.path.join(MODEL_DIR, "trained_model.joblib")
METRICS_SAVE_PATH = os.path.join(MODEL_DIR, "model_metrics.json")

# Base Raw Telemetry Columns
BASE_FEATURE_COLUMNS = [
    "minimum_latency",
    "maximum_latency",
    "average_latency",
    "packet_loss",
    "jitter",
    "throughput"
]

# Engineered Domain Physics Features
ENGINEERED_FEATURE_COLUMNS = [
    "latency_spread",
    "jitter_to_latency_ratio",
    "loss_impact_index",
    "itu_r_quality_factor"
]

ALL_FEATURE_COLUMNS = BASE_FEATURE_COLUMNS + ENGINEERED_FEATURE_COLUMNS
TARGET_COLUMN = "fault_label"


# ==============================================================================
# NETWORK DOMAIN FEATURE ENGINEERING
# ==============================================================================

def compute_network_features(df):
    """
    Transforms raw telemetry into 10 physics-informed domain features based on
    RFC 3550 jitter variance, queue oscillation spread, and ITU-T G.107 E-model ratings.
    """
    feat_df = df.copy()
    
    # 1. Latency Spread / Bufferbloat Fluctuation Delta
    feat_df["latency_spread"] = np.maximum(0.0, feat_df["maximum_latency"] - feat_df["minimum_latency"])
    
    # 2. Jitter-to-Latency Relative Ratio
    feat_df["jitter_to_latency_ratio"] = feat_df["jitter"] / (feat_df["average_latency"] + 1e-5)
    
    # 3. Loss-Impacting Index (Severity on active bandwidth)
    feat_df["loss_impact_index"] = feat_df["packet_loss"] / (feat_df["throughput"] + 0.1)
    
    # 4. ITU-T G.107 Standard Transmission Rating Factor (R)
    avg_l = feat_df["average_latency"].values
    loss_v = feat_df["packet_loss"].values
    
    id_factor = 0.024 * avg_l + 0.11 * np.maximum(0.0, avg_l - 177.3)
    ie_factor = 11.0 + 40.0 * np.log(1.0 + 10.0 * (loss_v / 100.0))
    r_factor = np.clip(93.2 - id_factor - ie_factor, 0.0, 100.0)
    feat_df["itu_r_quality_factor"] = np.round(r_factor, 2)
    
    return feat_df


# ==============================================================================
# DATASET LOADING & VALIDATION
# ==============================================================================

def load_and_prepare_data():
    """
    Loads dataset, executes domain feature engineering, and performs integrity checks.
    """
    if not os.path.isfile(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found at: {DATASET_PATH}")
        
    raw_df = pd.read_csv(DATASET_PATH)
    print(f"\n[+] Loaded dataset from: {DATASET_PATH}")
    print(f"[+] Total raw samples: {len(raw_df)}")
    
    # Apply Feature Engineering
    processed_df = compute_network_features(raw_df)
    
    required_cols = ALL_FEATURE_COLUMNS + [TARGET_COLUMN]
    cleaned_df = processed_df[required_cols].dropna().copy()
    
    print("\nDataset Class Distribution:")
    class_counts = cleaned_df[TARGET_COLUMN].value_counts()
    for cls_name, count in class_counts.items():
        print(f"  - {cls_name.ljust(16)}: {count} samples ({count / len(cleaned_df) * 100:.1f}%)")
        
    X = cleaned_df[ALL_FEATURE_COLUMNS]
    y = cleaned_df[TARGET_COLUMN]
    
    return X, y, class_counts.to_dict()


# ==============================================================================
# MODEL TRAINING & CALIBRATED BENCHMARK
# ==============================================================================

def train_and_benchmark(X, y):
    """
    Trains and cross-validates multiple ML models using Stratified 5-Fold Cross-Validation.
    Selects the highest-performing Calibrated Ensemble for production inference.
    """
    print("\n" + "=" * 70)
    print("   TELECOM-GRADE MACHINE LEARNING TRAINING & CROSS-VALIDATION")
    print("=" * 70)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    print(f"Features in Pipeline : {len(ALL_FEATURE_COLUMNS)} ({', '.join(ALL_FEATURE_COLUMNS)})")
    print(f"Training Set Size    : {len(X_train)} samples")
    print(f"Testing Set Size     : {len(X_test)} samples")
    print("-" * 70)

    candidate_models = {
        "Calibrated Random Forest": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", CalibratedClassifierCV(
                estimator=RandomForestClassifier(
                    n_estimators=200,
                    max_depth=10,
                    min_samples_split=2,
                    class_weight="balanced",
                    random_state=42
                ),
                cv=3
            ))
        ]),
        "Gradient Boosting": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", GradientBoostingClassifier(
                n_estimators=120,
                learning_rate=0.08,
                max_depth=5,
                random_state=42
            ))
        ]),
        "Decision Tree (Baseline)": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", DecisionTreeClassifier(
                max_depth=6,
                class_weight="balanced",
                random_state=42
            ))
        ]),
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=42
            ))
        ])
    }

    results = {}
    best_name = "Calibrated Random Forest"
    best_f1 = -1.0
    best_pipeline = None

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    for name, pipeline in candidate_models.items():
        # 5-Fold Stratified Cross-Validation
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=skf, scoring="f1_weighted")
        
        # Train on entire training split & Evaluate on holdout test split
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        results[name] = {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "cv_mean_f1": round(float(np.mean(cv_scores)), 4),
            "cv_std": round(float(np.std(cv_scores)), 4)
        }

        print(f"\nModel: {name}")
        print(f"  5-Fold CV F1-Score : {np.mean(cv_scores):.4f} (+/- {np.std(cv_scores):.4f})")
        print(f"  Holdout Test Acc   : {acc * 100:.2f}%")
        print(f"  Holdout Weighted F1: {f1:.4f}")

        if f1 > best_f1:
            best_f1 = f1
            best_name = name
            best_pipeline = pipeline

    print("\n" + "=" * 70)
    print(f"[*] WINNING PRODUCTION MODEL: {best_name} (Holdout F1: {best_f1:.4f})")
    print("=" * 70)

    # Detailed Holdout Evaluation for winning model
    y_pred_best = best_pipeline.predict(X_test)
    labels = sorted(list(y.unique()))
    cm = confusion_matrix(y_test, y_pred_best, labels=labels)
    report_dict = classification_report(y_test, y_pred_best, target_names=labels, output_dict=True, zero_division=0)

    print("\nConfusion Matrix (Holdout Test Set):")
    cm_df = pd.DataFrame(cm, index=[f"Actual_{l}" for l in labels], columns=[f"Pred_{l}" for l in labels])
    print(cm_df.to_string())

    # Save Production Artifacts
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(best_pipeline, MODEL_SAVE_PATH)
    print(f"\n[+] Saved winning model pipeline to: {MODEL_SAVE_PATH}")

    metrics_payload = {
        "model_type": best_name,
        "features_used": ALL_FEATURE_COLUMNS,
        "total_dataset_samples": len(X),
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "accuracy": results[best_name]["accuracy"],
        "precision": results[best_name]["precision"],
        "recall": results[best_name]["recall"],
        "f1_score": results[best_name]["f1_score"],
        "cv_5fold_mean_f1": results[best_name]["cv_mean_f1"],
        "labels": labels,
        "confusion_matrix": cm.tolist(),
        "per_class_metrics": {l: report_dict[l] for l in labels if l in report_dict},
        "model_comparison": results
    }

    with open(METRICS_SAVE_PATH, "w") as f:
        json.dump(metrics_payload, f, indent=2)
    print(f"[+] Saved model metrics JSON to: {METRICS_SAVE_PATH}")

    return best_pipeline, metrics_payload


def main():
    X, y, counts = load_and_prepare_data()
    train_and_benchmark(X, y)

if __name__ == "__main__":
    main()
