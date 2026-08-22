import os
import sys
import platform
import subprocess
import re
import time
import urllib.request
from datetime import datetime


# ==============================================================================
# ENVIRONMENT VALIDATION (WSL / LINUX CHECK)
# ==============================================================================

def verify_environment():
    """
    Verifies that the script is running inside a Linux/WSL environment.
    Linux `ping` and `tc` traffic control require Linux kernel utilities.
    """
    current_os = platform.system()
    if current_os != "Linux":
        print("\n" + "!" * 70)
        print("[WARNING] Non-Linux environment detected!")
        print(f"Current OS: {current_os}")
        print("This tool is designed to run inside WSL2 (Ubuntu Linux).")
        print("Please run using: python3 network_monitor.py inside WSL terminal.")
        print("!" * 70 + "\n")
        return False
    return True


# ==============================================================================
# PING METRIC TEST
# ==============================================================================

def test_ping(host="8.8.8.8", count=10, timeout=30):
    """
    Executes Linux ping command and parses:
    - Minimum Latency (ms)
    - Maximum Latency (ms)
    - Average Latency (ms)
    - Packet Loss (%)
    - Jitter (ms) [Mean absolute consecutive latency difference]
    
    Returns a dictionary containing all measured ping metrics.
    """
    command = [
        "ping",
        "-c", str(count),
        host
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout
    except subprocess.TimeoutExpired:
        print(f"[!] Ping test timed out after {timeout} seconds.")
        return {
            "latency_values": [],
            "minimum_latency": None,
            "maximum_latency": None,
            "average_latency": None,
            "packet_loss": 100.0,
            "jitter": None
        }
    except Exception as err:
        print(f"[!] Ping execution error: {err}")
        return {
            "latency_values": [],
            "minimum_latency": None,
            "maximum_latency": None,
            "average_latency": None,
            "packet_loss": 100.0,
            "jitter": None
        }

    # Extract individual packet latencies (e.g. "time=24.5 ms" or "time<1 ms")
    latency_values = []
    matches = re.findall(r"time[=<]([\d.]+)\s*ms", output)
    for value in matches:
        try:
            latency_values.append(float(value))
        except ValueError:
            continue

    # Extract packet loss percentage (e.g. "0% packet loss" or "10.0% packet loss")
    loss_match = re.search(r"(\d+(?:\.\d+)?)%\s*packet loss", output)
    if loss_match:
        packet_loss = float(loss_match.group(1))
    else:
        if count > 0:
            lost = count - len(latency_values)
            packet_loss = float((lost / count) * 100.0)
        else:
            packet_loss = 100.0

    # Calculate latency statistics
    if latency_values:
        minimum_latency = round(min(latency_values), 2)
        maximum_latency = round(max(latency_values), 2)
        average_latency = round(sum(latency_values) / len(latency_values), 2)
    else:
        minimum_latency = None
        maximum_latency = None
        average_latency = None

    # Calculate Jitter (RFC 3550: Mean absolute difference between consecutive delays)
    if len(latency_values) >= 2:
        diffs = [
            abs(latency_values[i] - latency_values[i - 1])
            for i in range(1, len(latency_values))
        ]
        jitter = round(sum(diffs) / len(diffs), 2)
    elif len(latency_values) == 1:
        jitter = 0.0
    else:
        jitter = None

    return {
        "latency_values": latency_values,
        "minimum_latency": minimum_latency,
        "maximum_latency": maximum_latency,
        "average_latency": average_latency,
        "packet_loss": round(packet_loss, 2),
        "jitter": jitter
    }


# ==============================================================================
# THROUGHPUT TEST
# ==============================================================================

def test_throughput(timeout=25, retries=1):
    """
    Measures download throughput in Mbps by retrieving a 5MB payload from Cloudflare CDN.
    Returns:
        float: Throughput in Mbps (rounded to 2 decimal places), or None if test fails.
    """
    url = "https://speed.cloudflare.com/__down?bytes=5000000"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) IntelligentNetworkAssistant/1.0",
        "Accept": "*/*"
    }

    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            start_time = time.time()

            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = response.read()

            elapsed_time = time.time() - start_time
            if elapsed_time <= 0:
                return None

            data_size_bytes = len(data)
            # Convert bytes to megabits: (bytes * 8) / 1,000,000
            data_size_megabits = (data_size_bytes * 8) / 1_000_000.0
            throughput = data_size_megabits / elapsed_time

            return round(throughput, 2)

        except Exception as err:
            if attempt < retries:
                time.sleep(1)
                continue
            print(f"[!] Throughput measurement failed: {err}")
            return None


# ==============================================================================
# UNIFIED METRICS COLLECTION
# ==============================================================================

def collect_metrics(host="8.8.8.8", ping_count=10, test_speed=True):
    """
    Collects complete network performance metrics (Ping + Throughput).
    Returns a validated dictionary with all 6 independent performance variables.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ping_res = test_ping(host=host, count=ping_count)

    throughput = None
    if test_speed:
        throughput = test_throughput()

    # Data validation: check if sample is valid for machine learning
    is_valid = True
    validation_error = None

    if ping_res["average_latency"] is None:
        is_valid = False
        validation_error = "Missing latency measurements (100% packet loss or ping timeout)."
    elif ping_res["jitter"] is None:
        is_valid = False
        validation_error = "Missing jitter calculation."
    elif test_speed and throughput is None:
        is_valid = False
        validation_error = "Throughput test failed to complete."

    return {
        "timestamp": timestamp,
        "host": host,
        "minimum_latency": ping_res["minimum_latency"],
        "maximum_latency": ping_res["maximum_latency"],
        "average_latency": ping_res["average_latency"],
        "packet_loss": ping_res["packet_loss"],
        "jitter": ping_res["jitter"],
        "throughput": throughput,
        "latency_values": ping_res["latency_values"],
        "is_valid": is_valid,
        "validation_error": validation_error
    }


# ==============================================================================
# CLI EXECUTION ENTRYPOINT
# ==============================================================================

def main():
    verify_environment()
    host = "8.8.8.8"
    ping_count = 10

    print("\n" + "=" * 55)
    print("      INTELLIGENT NETWORK MONITORING TOOL")
    print("=" * 55)
    print(f" Target Host     : {host}")
    print(f" Ping Count      : {ping_count} packets")
    print(f" Throughput Test : Enabled (5 MB Cloudflare payload)")
    print("-" * 55)
    print(" Running diagnostic tests, please wait...")

    metrics = collect_metrics(host=host, ping_count=ping_count, test_speed=True)

    print("\n" + "-" * 55)
    print(" NETWORK PERFORMANCE METRICS")
    print("-" * 55)
    print(f" Timestamp        : {metrics['timestamp']}")
    print(f" Target Host      : {metrics['host']}")
    
    if metrics['minimum_latency'] is not None:
        print(f" Minimum Latency  : {metrics['minimum_latency']:.2f} ms")
        print(f" Maximum Latency  : {metrics['maximum_latency']:.2f} ms")
        print(f" Average Latency  : {metrics['average_latency']:.2f} ms")
    else:
        print(f" Latency          : [FAILED] Unable to measure")

    print(f" Packet Loss      : {metrics['packet_loss']:.2f} %")

    if metrics['jitter'] is not None:
        print(f" Jitter           : {metrics['jitter']:.2f} ms")
    else:
        print(f" Jitter           : [FAILED] Unable to calculate")

    if metrics['throughput'] is not None:
        print(f" Throughput       : {metrics['throughput']:.2f} Mbps")
    else:
        print(f" Throughput       : [FAILED] Unable to measure")

    print("-" * 55)
    if metrics["is_valid"]:
        print(" Sample Status    : [VALID] Ready for ML dataset.")
    else:
        print(f" Sample Status    : [INVALID] Reason: {metrics['validation_error']}")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()