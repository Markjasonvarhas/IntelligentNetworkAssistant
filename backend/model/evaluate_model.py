import os
import sys
import json
import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BACKEND_DIR, "model", "trained_model.joblib")
DATASET_PATH = os.path.join(BACKEND_DIR, "dataset", "experimental_data.csv")
METRICS_PATH = os.path.join(BACKEND_DIR, "model", "model_metrics.json")

FEATURE_COLUMNS = [
    "minimum_latency",
    "maximum_latency",
    "average_latency",
    "packet_loss",
    "jitter",
    "throughput"
]
TARGET_COLUMN = "fault_label"


def evaluate_existing_model():
    """
    Loads saved model and evaluates it against the latest dataset.
    Prints an academic-formatted evaluation table and confusion matrix.
    """
    if not os.path.isfile(MODEL_PATH):
        print(f"[!] Model not found at {MODEL_PATH}. Please run train_model.py first.")
        return

    if not os.path.isfile(DATASET_PATH):
        print(f"[!] Dataset not found at {DATASET_PATH}.")
        return

    pipeline = joblib.load(MODEL_PATH)
    df = pd.read_csv(DATASET_PATH)

    cleaned_df = df[FEATURE_COLUMNS + [TARGET_COLUMN]].dropna()
    X = cleaned_df[FEATURE_COLUMNS]
    y = cleaned_df[TARGET_COLUMN]

    labels = sorted(list(y.unique()))
    y_pred = pipeline.predict(X)

    acc = accuracy_score(y, y_pred)
    report = classification_report(y, y_pred, labels=labels, zero_division=0)
    cm = confusion_matrix(y, y_pred, labels=labels)

    print("\n" + "=" * 65)
    print("        OFFICIAL MACHINE LEARNING MODEL EVALUATION")
    print("=" * 65)
    print(f" Dataset Size        : {len(cleaned_df)} samples")
    print(f" Overall Accuracy    : {acc * 100:.2f}%")
    print("-" * 65)
    print(" CLASSIFICATION REPORT (Precision, Recall, F1-Score):")
    print("-" * 65)
    print(report)
    print("-" * 65)
    print(" CONFUSION MATRIX:")
    print("-" * 65)
    print(f" Labels Order: {labels}")
    for idx, row in enumerate(cm):
        row_str = "  ".join(f"{val:>4}" for val in row)
        print(f"  {labels[idx].ljust(15)}: [ {row_str} ]")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    evaluate_existing_model()
