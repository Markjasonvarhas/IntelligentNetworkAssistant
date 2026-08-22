import os
import sys
import csv
import time
from datetime import datetime

# Import network monitoring functions
from network_monitor import collect_metrics, verify_environment


# ==============================================================================
# CONFIGURATION & FILE PATHS
# ==============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
CSV_FILE = os.path.join(DATASET_DIR, "experimental_data.csv")

TARGET_HOST = "8.8.8.8"
PING_PACKET_COUNT = 10

VALID_FAULT_LABELS = {
    "1": "normal",
    "2": "high_latency",
    "3": "packet_loss",
    "4": "high_jitter",
    "5": "congestion"
}

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


# ==============================================================================
# DIRECTORY & CSV INITIALIZATION
# ==============================================================================

def ensure_dataset_ready():
    """Ensures the dataset folder exists."""
    os.makedirs(DATASET_DIR, exist_ok=True)


def append_sample_to_csv(sample_data):
    """
    Appends a validated sample dictionary to the CSV dataset.
    Ensures headers are written only once and jitter is explicitly recorded.
    """
    ensure_dataset_ready()
    file_exists = os.path.isfile(CSV_FILE) and os.path.getsize(CSV_FILE) > 0

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        
        row = {
            "timestamp": sample_data["timestamp"],
            "host": sample_data["host"],
            "minimum_latency": sample_data["minimum_latency"],
            "maximum_latency": sample_data["maximum_latency"],
            "average_latency": sample_data["average_latency"],
            "packet_loss": sample_data["packet_loss"],
            "jitter": sample_data["jitter"],
            "throughput": sample_data["throughput"],
            "fault_label": sample_data["fault_label"]
        }
        writer.writerow(row)


# ==============================================================================
# SAMPLE COLLECTION ENGINE
# ==============================================================================

def collect_single_sample(fault_label, sample_index=1, total_samples=1):
    """
    Performs one complete measurement cycle, validates results,
    and appends to CSV if and only if all metrics are valid.
    """
    prefix = f"[{sample_index}/{total_samples}] " if total_samples > 1 else ""
    print(f"\n{prefix}Testing network metrics for label: '{fault_label}'...")

    metrics = collect_metrics(
        host=TARGET_HOST,
        ping_count=PING_PACKET_COUNT,
        test_speed=True
    )

    # Output formatted telemetry
    print(f" -> Min Latency : {metrics['minimum_latency']} ms")
    print(f" -> Max Latency : {metrics['maximum_latency']} ms")
    print(f" -> Avg Latency : {metrics['average_latency']} ms")
    print(f" -> Packet Loss : {metrics['packet_loss']} %")
    print(f" -> Jitter      : {metrics['jitter']} ms")
    print(f" -> Throughput  : {metrics['throughput']} Mbps")

    # Strict Data Integrity Check: Never save None / corrupted samples
    if not metrics["is_valid"]:
        print(f" [!] REJECTED: Sample invalid. Reason: {metrics['validation_error']}")
        print(" [!] Sample was NOT saved to the dataset.")
        return False

    # Attach fault label
    metrics["fault_label"] = fault_label

    try:
        append_sample_to_csv(metrics)
        print(f" [OK] SUCCESS: Sample saved to {CSV_FILE}")
        return True
    except Exception as err:
        print(f" [!] ERROR: Failed to write sample to CSV: {err}")
        return False


# ==============================================================================
# USER INTERACTION HELPERS
# ==============================================================================

def select_fault_label():
    """Interactive prompt for choosing a standardized experimental fault label."""
    print("\nSelect Fault Condition / Experiment Label:")
    for key, label in VALID_FAULT_LABELS.items():
        print(f"  [{key}] {label}")
    
    while True:
        choice = input("\nEnter choice (1-5) or custom label name: ").strip()
        if choice in VALID_FAULT_LABELS:
            return VALID_FAULT_LABELS[choice]
        elif choice:
            return choice
        print("Invalid input. Please choose 1-5.")


# ==============================================================================
# COLLECTION MODES
# ==============================================================================

def run_batch_collection():
    """Automated batch collection of N samples with configurable interval."""
    label = select_fault_label()

    try:
        total_samples = int(input("\nEnter number of samples to collect (e.g. 15): ").strip())
        if total_samples <= 0:
            print("Sample count must be positive.")
            return
    except ValueError:
        print("Invalid number. Aborting.")
        return

    try:
        interval = float(input("Enter delay interval between samples in seconds (default 5): ").strip() or "5")
        if interval < 0:
            interval = 0
    except ValueError:
        interval = 5.0

    print("\n" + "=" * 60)
    print(f" STARTING BATCH COLLECTION: {total_samples} samples of '{label}'")
    print(f" Interval: {interval}s | Target: {TARGET_HOST} | CSV: {CSV_FILE}")
    print(" Press CTRL+C at any time to cancel.")
    print("=" * 60)

    successful = 0
    failed = 0

    for i in range(1, total_samples + 1):
        try:
            success = collect_single_sample(label, sample_index=i, total_samples=total_samples)
            if success:
                successful += 1
            else:
                failed += 1

            if i < total_samples:
                print(f"Waiting {interval}s before next sample...")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n[!] Batch collection interrupted by user.")
            break

    print("\n" + "=" * 60)
    print(f" BATCH COLLECTION FINISHED")
    print(f" Successfully Saved : {successful} samples")
    print(f" Failed/Rejected     : {failed} samples")
    print(f" Total in Batch      : {successful + failed} / {total_samples}")
    print("=" * 60 + "\n")


def run_continuous_collection():
    """Continuous data collection mode with interval until interrupted."""
    label = select_fault_label()

    try:
        interval = float(input("Enter interval between samples in seconds (default 10): ").strip() or "10")
        if interval < 0:
            interval = 0
    except ValueError:
        interval = 10.0

    print("\n" + "=" * 60)
    print(f" STARTING CONTINUOUS COLLECTION: '{label}'")
    print(f" Interval: {interval}s | Target: {TARGET_HOST} | CSV: {CSV_FILE}")
    print(" Press CTRL+C to stop.")
    print("=" * 60)

    count = 0
    successful = 0

    while True:
        try:
            count += 1
            success = collect_single_sample(label, sample_index=count, total_samples=count)
            if success:
                successful += 1

            print(f"Waiting {interval}s before next sample...")
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n[!] Continuous collection stopped by user.")
            break

    print(f"\nCollected {successful} valid samples for '{label}'.\n")


# ==============================================================================
# MAIN CLI MENU
# ==============================================================================

def main():
    verify_environment()
    ensure_dataset_ready()

    print("\n" + "=" * 60)
    print("     NETWORK EXPERIMENT DATASET COLLECTOR (BSIT RESEARCH)")
    print("=" * 60)
    print(" 1. Batch Collection (e.g. 15 samples with auto-interval)")
    print(" 2. Continuous Collection (runs until CTRL+C)")
    print(" 3. Collect Single Sample")
    print(" 4. View Dataset Summary")
    print(" 5. Exit")
    print("=" * 60)

    choice = input("\nSelect an option (1-5): ").strip()

    if choice == "1":
        run_batch_collection()
    elif choice == "2":
        run_continuous_collection()
    elif choice == "3":
        label = select_fault_label()
        collect_single_sample(label)
    elif choice == "4":
        show_dataset_summary()
    elif choice == "5":
        print("Exiting.")
        sys.exit(0)
    else:
        print("Invalid choice.")


def show_dataset_summary():
    """Prints current class sample counts in the CSV."""
    if not os.path.isfile(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        print(f"\n[!] Dataset file {CSV_FILE} is currently empty or does not exist.")
        return

    counts = {}
    total = 0
    with open(CSV_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lbl = row.get("fault_label", "unknown")
            counts[lbl] = counts.get(lbl, 0) + 1
            total += 1

    print("\n" + "-" * 40)
    print(f" DATASET SUMMARY ({CSV_FILE})")
    print("-" * 40)
    print(f" Total Samples : {total}")
    for lbl, cnt in counts.items():
        print(f"  - {lbl.ljust(15)}: {cnt} samples")
    print("-" * 40 + "\n")


if __name__ == "__main__":
    main()