import os
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
TARGET_CSV = os.path.join(DATASET_DIR, "experimental_data.csv")

ROOT_DIR = os.path.dirname(BASE_DIR)
OLD_EXP_CSV = os.path.join(ROOT_DIR, "dataset", "experimental_data.csv")
NORMAL_BASELINE_CSV = os.path.join(DATASET_DIR, "normal_baseline.csv")

CSV_FIELDNAMES = [
    "timestamp",
    "host",
    "minimum_latency",
    "maximum_latency",
    "average_latency",
    "packet_loss",
    "jitter",
    "throughput",
    "fault_label"
]


def clean_and_merge_datasets():
    """
    Consolidates existing baseline and experimental CSV files into
    the unified backend/dataset/experimental_data.csv.
    Filters out rows with missing/null values to guarantee ML research integrity.
    """
    os.makedirs(DATASET_DIR, exist_ok=True)
    all_valid_rows = []
    seen_timestamps = set()

    sources = [
        (OLD_EXP_CSV, "old_experimental_csv", None),
        (NORMAL_BASELINE_CSV, "normal_baseline_csv", "normal")
    ]

    for filepath, desc, default_label in sources:
        if not os.path.isfile(filepath):
            print(f"[!] Source not found: {filepath}")
            continue

        print(f"Reading from {desc}: {filepath}")
        with open(filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ts = row.get("timestamp", "").strip()
                if not ts:
                    continue

                label = row.get("fault_label", "")
                if not label and default_label:
                    label = default_label

                # Check if all numeric fields are present and valid
                try:
                    min_lat = float(row.get("minimum_latency", ""))
                    max_lat = float(row.get("maximum_latency", ""))
                    avg_lat = float(row.get("average_latency", ""))
                    pkt_loss = float(row.get("packet_loss", ""))
                    jitter = float(row.get("jitter", ""))
                    tp_val = row.get("throughput", "")
                    if not tp_val:
                        print(f"  [x] Dropping row with missing throughput: {ts}")
                        continue
                    throughput = float(tp_val)

                    if not label:
                        label = "normal"

                    cleaned_row = {
                        "timestamp": ts,
                        "host": row.get("host", "8.8.8.8"),
                        "minimum_latency": round(min_lat, 2),
                        "maximum_latency": round(max_lat, 2),
                        "average_latency": round(avg_lat, 2),
                        "packet_loss": round(pkt_loss, 2),
                        "jitter": round(jitter, 2),
                        "throughput": round(throughput, 2),
                        "fault_label": label.strip()
                    }

                    if ts not in seen_timestamps:
                        seen_timestamps.add(ts)
                        all_valid_rows.append(cleaned_row)

                except (ValueError, TypeError) as err:
                    print(f"  [x] Dropping invalid row {ts}: {err}")

    # Write unified dataset
    with open(TARGET_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_valid_rows)

    print(f"\n[OK] Consolidated dataset created at: {TARGET_CSV}")
    print(f"[OK] Total clean samples: {len(all_valid_rows)}")

    # Print breakdown
    breakdown = {}
    for r in all_valid_rows:
        lbl = r["fault_label"]
        breakdown[lbl] = breakdown.get(lbl, 0) + 1

    print("\nDataset Class Distribution:")
    for lbl, count in breakdown.items():
        print(f"  - {lbl.ljust(15)}: {count} samples")


if __name__ == "__main__":
    clean_and_merge_datasets()
