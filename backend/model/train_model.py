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
from sklearn.ensemble import RandomForestClassifier
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

# Independent variables (Features)
FEATURE_COLUMNS = [
    "minimum_latency",
    "maximum_latency",
    "average_latency",
    "packet_loss",
    "jitter",
    "throughput"
]

# Dependent variable (Target)
TARGET_COLUMN = "fault_label"


# ==============================================================================
# DATASET LOADING & INTEGRITY CHECKS
# ==============================================================================

def load_and_validate_dataset():
    """
    Loads dataset from CSV, performs strict research validation,
    and removes any non-feature columns (timestamp, host) to prevent data leakage.
    """
    if not os.path.isfile(DATASET_PATH):
        raise FileNotFoundError(f"Dataset file not found at: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)
    print(f"\n[+] Loaded dataset from: {DATASET_PATH}")
    print(f"[+] Total raw samples: {len(df)}")

    # Check for required columns
    required_cols = FEATURE_COLUMNS + [TARGET_COLUMN]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column in dataset: {col}")

    # Drop any rows with NaN/null values to preserve research integrity
    cleaned_df = df[required_cols].dropna().copy()
    dropped_count = len(df) - len(cleaned_df)
    if dropped_count > 0:
        print(f"[!] Warning: Dropped {dropped_count} incomplete rows with null values.")

    print("\nDataset Class Distribution:")
    class_counts = cleaned_df[TARGET_COLUMN].value_counts()
    for cls_name, count in class_counts.items():
        print(f"  - {cls_name.ljust(15)}: {count} samples ({count / len(cleaned_df) * 100:.1f}%)")

    # Research validation check
    unique_classes = cleaned_df[TARGET_COLUMN].unique()
    if len(unique_classes) < 2:
        raise ValueError("Dataset must contain at least 2 distinct classes to train a classifier.")

    X = cleaned_df[FEATURE_COLUMNS]
    y = cleaned_df[TARGET_COLUMN]

    return X, y, class_counts.to_dict()


# ==============================================================================
# MODEL TRAINING & COMPARATIVE BENCHMARKING
# ==============================================================================

def train_and_compare_models(X, y):
    """
    Trains and compares multiple classification models:
    1. Decision Tree (Explainable baseline)
    2. Random Forest (Ensemble classifier)
    3. Logistic Regression (Linear probabilistic classifier)

    Uses Stratified Train/Test Split (75% Train, 25% Test) to preserve class proportions.
    """
    print("\n" + "=" * 65)
    print("      MACHINE LEARNING MODEL TRAINING & COMPARATIVE BENCHMARK")
    print("=" * 65)

    # Check if smallest class has enough samples for stratified split
    min_class_count = y.value_counts().min()
    use_stratify = y if min_class_count >= 2 else None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.25,
        random_state=42,
        stratify=use_stratify
    )

    print(f"Training Set Size : {len(X_train)} samples")
    print(f"Testing Set Size  : {len(X_test)} samples")
    print("-" * 65)

    # Candidate Models with standardized pipelines
    models = {
        "Decision Tree": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", DecisionTreeClassifier(
                max_depth=5,
                min_samples_split=4,
                random_state=42
            ))
        ]),
        "Random Forest": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", RandomForestClassifier(
                n_estimators=100,
                max_depth=6,
                min_samples_split=3,
                random_state=42
            ))
        ]),
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(
                max_iter=1000,
                C=1.0,
                random_state=42
            ))
        ])
    }

    results = {}
    best_model_name = None
    best_f1_score = -1.0
    best_pipeline = None

    unique_labels = sorted(list(y.unique()))

    for name, pipeline in models.items():
        print(f"\n[*] Training {name}...")
        pipeline.fit(X_train, y_train)

        # Predictions
        y_pred = pipeline.predict(X_test)

        # Metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
        cm = confusion_matrix(y_test, y_pred, labels=unique_labels).tolist()

        # Cross Validation (if sufficient samples)
        cv_scores = []
        if min_class_count >= 3:
            try:
                cv = StratifiedKFold(n_splits=min(3, min_class_count), shuffle=True, random_state=42)
                cv_scores = cross_val_score(pipeline, X, y, cv=cv, scoring="accuracy").tolist()
            except Exception:
                cv_scores = [acc]
        else:
            cv_scores = [acc]

        mean_cv = float(np.mean(cv_scores)) if cv_scores else acc

        results[name] = {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "cv_accuracy_mean": round(mean_cv, 4),
            "cv_scores": [round(float(s), 4) for s in cv_scores],
            "confusion_matrix": cm,
            "classification_report": classification_report(
                y_test, y_pred,
                labels=unique_labels,
                output_dict=True,
                zero_division=0
            )
        }

        print(f"  -> Accuracy : {acc * 100:.2f}%")
        print(f"  -> F1-Score : {f1:.4f}")
        print(f"  -> Precision: {prec:.4f}")
        print(f"  -> Recall   : {rec:.4f}")

        # Choose best model primarily based on weighted F1-Score (balances precision & recall)
        if f1 > best_f1_score:
            best_f1_score = f1
            best_model_name = name
            best_pipeline = pipeline

    print("\n" + "=" * 65)
    print(f" [OK] BEST PERFORMING MODEL: {best_model_name}")
    print(f" [OK] Top Weighted F1-Score: {best_f1_score:.4f}")
    print("=" * 65)

    return {
        "best_model_name": best_model_name,
        "best_pipeline": best_pipeline,
        "labels": unique_labels,
        "feature_names": FEATURE_COLUMNS,
        "model_comparisons": results,
        "test_size": len(X_test),
        "train_size": len(X_train)
    }


# ==============================================================================
# MODEL PERSISTENCE & METRICS EXPORT
# ==============================================================================

def save_trained_artifacts(training_results, class_distribution):
    """
    Saves the best trained pipeline to .joblib and exports all evaluation
    metrics to a JSON file for the Flask API and Vue Dashboard.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)

    # 1. Save ML Model Pipeline
    joblib.dump(training_results["best_pipeline"], MODEL_SAVE_PATH)
    print(f"\n[OK] Model successfully saved to: {MODEL_SAVE_PATH}")

    # 2. Export Metrics JSON
    metrics_payload = {
        "model_name": training_results["best_model_name"],
        "target_classes": training_results["labels"],
        "feature_names": training_results["feature_names"],
        "train_samples": training_results["train_size"],
        "test_samples": training_results["test_size"],
        "class_distribution": class_distribution,
        "model_comparisons": training_results["model_comparisons"],
        "selected_model_metrics": training_results["model_comparisons"][training_results["best_model_name"]]
    }

    with open(METRICS_SAVE_PATH, mode="w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)

    print(f"[OK] Model evaluation metrics exported to: {METRICS_SAVE_PATH}")


# ==============================================================================
# MAIN EXECUTION ENTRYPOINT
# ==============================================================================

def main():
    try:
        X, y, class_distribution = load_and_validate_dataset()
        results = train_and_compare_models(X, y)
        save_trained_artifacts(results, class_distribution)
        print("\n[OK] Machine Learning Pipeline Execution Complete.\n")
    except Exception as err:
        print(f"\n[!] Training Pipeline Error: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
