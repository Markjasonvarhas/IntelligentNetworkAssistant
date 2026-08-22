import os
import sys
import platform
import subprocess
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
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
    - Jitter (ms) [RFC 3550 standard]
    
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

    # Extract individual packet latencies
    latency_values = []
    matches = re.findall(r"time[=<]([\d.]+)\s*ms", output)
    for value in matches:
        try:
            latency_values.append(float(value))
        except ValueError:
            continue

    # Extract packet loss percentage
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

    # Calculate Jitter (RFC 3550: Mean absolute consecutive differences)
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
            data_size_megabits = (data_size_bytes * 8) / 1_000_000.0
            throughput = data_size_megabits / elapsed_time

            return round(throughput, 2)

        except Exception as err:
            if attempt < retries:
                time.sleep(1)
                continue
            return None


# ==============================================================================
# UNIFIED METRICS COLLECTION
# ==============================================================================

def collect_metrics(host="8.8.8.8", ping_count=10, test_speed=True):
    """
    Collects complete network performance metrics (Ping + Throughput).
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ping_res = test_ping(host=host, count=ping_count)

    throughput = None
    if test_speed:
        throughput = test_throughput()

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

    metrics = {
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

    # Add Network Health & Experience Scores
    metrics["health_scores"] = compute_quality_scores(metrics)
    return metrics


# ==============================================================================
# ADVANCED QOS & USER EXPERIENCE (MOS) HEALTH SCORING
# ==============================================================================

def compute_quality_scores(metrics):
    """
    Calculates Network Health Index (0-100), Mean Opinion Score (MOS 1.0-4.5),
    and Experience Tier ratings for Gaming, Video Streaming, and VoIP calls.
    """
    avg_lat = metrics.get("average_latency") or 30.0
    loss = metrics.get("packet_loss") or 0.0
    jitter = metrics.get("jitter") or 2.0
    tp = metrics.get("throughput") or 50.0

    # 1. ITU-T E-Model based MOS calculation
    # R factor: Transmission Rating Factor (0-100)
    effective_lat = avg_lat + (jitter * 2.0)
    r_factor = 93.2 - (effective_lat * 0.024) - (loss * 2.5)
    r_factor = max(0.0, min(100.0, r_factor))

    if r_factor < 0:
        mos = 1.0
    elif r_factor > 100:
        mos = 4.5
    else:
        mos = 1.0 + (0.035 * r_factor) + (r_factor * (r_factor - 60.0) * (100.0 - r_factor) * 7.0e-6)
    mos = round(max(1.0, min(4.5, mos)), 2)

    # 2. Overall Health Index (0 - 100)
    lat_score = max(0, 100 - (avg_lat * 0.4))
    loss_score = max(0, 100 - (loss * 10.0))
    jit_score = max(0, 100 - (jitter * 4.0))
    tp_score = min(100, tp * 1.5)
    overall_health = round((lat_score * 0.35) + (loss_score * 0.35) + (jit_score * 0.15) + (tp_score * 0.15), 1)
    overall_health = max(0.0, min(100.0, overall_health))

    # 3. Gaming Tier
    if avg_lat < 35 and jitter < 5 and loss == 0:
        gaming_grade = "S Tier (Ultra Responsive)"
        gaming_status = "optimal"
    elif avg_lat < 70 and jitter < 10 and loss < 1:
        gaming_grade = "A Tier (Competitive Ready)"
        gaming_status = "good"
    elif avg_lat < 120 and loss < 3:
        gaming_grade = "B Tier (Casual Playable)"
        gaming_status = "fair"
    else:
        gaming_grade = "D Tier (High Latency / Lag)"
        gaming_status = "poor"

    # 4. 4K Streaming Tier
    if tp >= 25.0 and loss < 1.0:
        streaming_grade = "4K UHD (Buffer-Free)"
        streaming_status = "optimal"
    elif tp >= 10.0 and loss < 3.0:
        streaming_grade = "1080p FHD (Smooth)"
        streaming_status = "good"
    elif tp >= 4.0:
        streaming_grade = "720p HD (Standard)"
        streaming_status = "fair"
    else:
        streaming_grade = "Buffering Stutter"
        streaming_status = "poor"

    # 5. Video Calling / VoIP Tier
    if mos >= 4.2:
        voip_grade = "HD Voice (Lossless)"
        voip_status = "optimal"
    elif mos >= 3.8:
        voip_grade = "Good Clarity"
        voip_status = "good"
    elif mos >= 3.2:
        voip_grade = "Acceptable"
        voip_status = "fair"
    else:
        voip_grade = "Choppy Voice / Delay"
        voip_status = "poor"

    return {
        "overall_health_score": overall_health,
        "mos_score": mos,
        "gaming": { "grade": gaming_grade, "status": gaming_status },
        "streaming": { "grade": streaming_grade, "status": streaming_status },
        "voip": { "grade": voip_grade, "status": voip_status }
    }


# ==============================================================================
# MULTI-TARGET CONCURRENT PROBE MATRIX
# ==============================================================================

DEFAULT_PROBE_TARGETS = [
    {"name": "Google DNS", "host": "8.8.8.8", "type": "Global DNS"},
    {"name": "Cloudflare DNS", "host": "1.1.1.1", "type": "Global CDN / DNS"},
    {"name": "OpenDNS (Cisco)", "host": "208.67.222.222", "type": "Security DNS"},
    {"name": "Quad9 Secure", "host": "9.9.9.9", "type": "Privacy DNS"}
]

def probe_single_target(target):
    """Fast probe with 3 packets."""
    res = test_ping(host=target["host"], count=3, timeout=6)
    return {
        "name": target["name"],
        "host": target["host"],
        "type": target["type"],
        "latency": res["average_latency"],
        "loss": res["packet_loss"],
        "jitter": res["jitter"],
        "status": "online" if res["average_latency"] is not None else "offline"
    }

def probe_multi_targets(targets=None):
    """Probes multiple network nodes concurrently in threads."""
    target_list = targets or DEFAULT_PROBE_TARGETS
    with ThreadPoolExecutor(max_workers=len(target_list)) as executor:
        results = list(executor.map(probe_single_target, target_list))
    return results


# ==============================================================================
# FAST REAL-TIME STREAMING PROBE (ANY HOST / DOMAIN / IP)
# ==============================================================================

def fast_live_probe(host="8.8.8.8"):
    """
    Rapid 2-packet probe designed for sub-second continuous real-time telemetry streaming.
    Supports any IP address, domain name (e.g. google.com, cloudflare.com), or LAN gateway.
    """
    clean_host = host.strip() or "8.8.8.8"
    res = test_ping(host=clean_host, count=2, timeout=4)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lat = res["average_latency"]
    loss = res["packet_loss"]
    jitter = res["jitter"] if res["jitter"] is not None else 0.0

    return {
        "timestamp": ts,
        "host": clean_host,
        "latency": lat,
        "minimum_latency": res["minimum_latency"],
        "maximum_latency": res["maximum_latency"],
        "packet_loss": loss,
        "jitter": jitter,
        "latency_values": res["latency_values"],
        "status": "online" if lat is not None else "offline"
    }


# ==============================================================================
# CLI EXECUTION ENTRYPOINT
# ==============================================================================

def main():
    verify_environment()
    host = "8.8.8.8"
    metrics = collect_metrics(host=host, ping_count=10, test_speed=True)

    print("\n" + "=" * 55)
    print("      INTELLIGENT NETWORK MONITORING TOOL")
    print("=" * 55)
    print(f" Target Host     : {host}")
    print(f" Avg Latency     : {metrics['average_latency']} ms")
    print(f" Packet Loss     : {metrics['packet_loss']} %")
    print(f" Jitter          : {metrics['jitter']} ms")
    print(f" Throughput      : {metrics['throughput']} Mbps")
    print(f" Health Score    : {metrics['health_scores']['overall_health_score']} / 100")
    print(f" VoIP MOS Index  : {metrics['health_scores']['mos_score']} / 4.5")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()