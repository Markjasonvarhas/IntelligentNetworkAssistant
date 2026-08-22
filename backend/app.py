import os
import sys
import json
import platform
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from network_monitor import (
    collect_metrics,
    verify_environment,
    probe_multi_targets,
    fast_live_probe,
    run_traceroute,
    run_dns_benchmark,
    probe_critical_ports,
    test_path_mtu
)
from diagnosis_engine import get_diagnosis, engine
from database.db import (
    insert_diagnosis,
    get_recent_diagnoses,
    insert_telemetry,
    get_recent_telemetry,
    get_statistics
)

# ==============================================================================
# FLASK APPLICATION INITIALIZATION
# ==============================================================================

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for Vue 3 frontend

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BACKEND_DIR)
FRONTEND_DIST_DIR = os.path.join(ROOT_DIR, "frontend", "dist")
METRICS_JSON_PATH = os.path.join(BACKEND_DIR, "model", "model_metrics.json")


# ==============================================================================
# API ENDPOINTS
# ==============================================================================

import urllib.request

@app.route("/api/status", methods=["GET"])
def get_system_status():
    """
    Returns system health status, OS platform details, active ML model, and database status.
    """
    model_loaded = engine.model is not None
    is_linux = platform.system() == "Linux"

    return jsonify({
        "status": "online",
        "service": "Intelligent Network Troubleshooting Assistant",
        "platform": platform.system(),
        "is_wsl_linux": is_linux,
        "model_loaded": model_loaded,
        "model_type": type(engine.model.named_steps["classifier"]).__name__ if model_loaded else "Heuristic Rule Engine"
    }), 200


def detect_vpn_status(org, asn_str, isp_str):
    """
    Analyzes ASN, Organization, and ISP signatures to determine if traffic is routed through
    Cloudflare WARP, commercial VPNs (Nord, Express, Mullvad, Proton), WireGuard, or Cloud Proxies.
    """
    text = f"{org} {asn_str} {isp_str}".lower()
    
    # 1. Cloudflare WARP / Gateway
    if "cloudflare" in text or "as13335" in text or "as209242" in text:
        return {
            "is_vpn": True,
            "vpn_name": "Cloudflare WARP / 1.1.1.1 Tunnel",
            "tunnel_type": "WireGuard / MASQUE (Cloudflare Edge)",
            "security_status": "Encrypted VPN Tunnel Active",
            "overhead_estimate": "Low (~5-15ms)",
            "dns_shield": "Cloudflare Secure DNS"
        }
    
    # 2. Commercial / Privacy VPNs
    vpn_keywords = {
        "mullvad": "Mullvad VPN (WireGuard/OpenVPN)",
        "nordvpn": "NordVPN (NordLynx / WireGuard)",
        "expressvpn": "ExpressVPN (Lightway)",
        "surfshark": "Surfshark VPN",
        "proton": "ProtonVPN (WireGuard)",
        "wireguard": "WireGuard Encrypted Tunnel",
        "tailscale": "Tailscale WireGuard Mesh",
        "private internet access": "Private Internet Access (PIA)",
        "cyberghost": "CyberGhost VPN",
        "windscribe": "Windscribe VPN",
        "ovpn": "OpenVPN Tunnel"
    }
    for kw, label in vpn_keywords.items():
        if kw in text:
            return {
                "is_vpn": True,
                "vpn_name": label,
                "tunnel_type": "Encrypted Virtual Private Network",
                "security_status": "Encrypted VPN Tunnel Active",
                "overhead_estimate": "Moderate (~20-40ms)",
                "dns_shield": "VPN Encrypted Resolver"
            }
            
    # 3. Datacenter / Cloud Proxy Hosting
    datacenter_keywords = ["digitalocean", "amazon.com", "aws", "google cloud", "microsoft azure", "ovh", "linode", "hetzner", "oracle cloud", "vultr"]
    for dc in datacenter_keywords:
        if dc in text:
            return {
                "is_vpn": True,
                "vpn_name": "Cloud Proxy / Datacenter Egress",
                "tunnel_type": "Encrypted Cloud Proxy",
                "security_status": "Datacenter / Proxy Egress Active",
                "overhead_estimate": "Variable",
                "dns_shield": "Datacenter DNS"
            }

    # 4. Direct Residential / Mobile ISP
    return {
        "is_vpn": False,
        "vpn_name": "None (Direct ISP)",
        "tunnel_type": "Direct Physical Routing (No VPN)",
        "security_status": "Direct Physical Link",
        "overhead_estimate": "0 ms (Native)",
        "dns_shield": "ISP Default DNS"
    }


@app.route("/api/client-network-info", methods=["GET"])
def get_client_network_info():
    """
    Automatically detects the visitor's connected network, Public IP, ISP, ASN, Location,
    and inspects active VPN / Cloudflare WARP / Encrypted Tunnel status.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.remote_addr or "127.0.0.1"

    is_private = client_ip in ["127.0.0.1", "localhost", "::1"] or client_ip.startswith("192.168.") or client_ip.startswith("10.") or client_ip.startswith("172.")
    lookup_url = "https://ipapi.co/json/" if is_private else f"https://ipapi.co/{client_ip}/json/"

    try:
        req = urllib.request.Request(
            lookup_url,
            headers={"User-Agent": "Mozilla/5.0 IntelligentNetworkAssistant/1.0"}
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            geo_data = json.loads(resp.read().decode())
            org = geo_data.get("org", "")
            asn_str = geo_data.get("asn", "")
            isp_str = geo_data.get("org") or geo_data.get("asn", "Local Network")
            
            vpn_meta = detect_vpn_status(org, asn_str, isp_str)

            return jsonify({
                "ip": geo_data.get("ip", client_ip),
                "isp": isp_str,
                "city": geo_data.get("city", "Local City"),
                "region": geo_data.get("region", ""),
                "country": geo_data.get("country_name", "Local"),
                "country_code": geo_data.get("country_code", "LOC"),
                "asn": asn_str or "Private ASN",
                "timezone": geo_data.get("timezone", "UTC"),
                "is_local": is_private,
                "vpn": vpn_meta
            }), 200
    except Exception:
        vpn_meta = detect_vpn_status("", "", "Local LAN")
        return jsonify({
            "ip": client_ip,
            "isp": "Local Gateway / Wi-Fi Network",
            "city": "Local Network",
            "region": "",
            "country": "Local",
            "country_code": "LOC",
            "asn": "Private LAN",
            "timezone": "UTC",
            "is_local": True,
            "vpn": vpn_meta
        }), 200


@app.route("/api/realtime-stream", methods=["GET"])
def get_realtime_stream_probe():
    """
    Ultra-fast sub-second real-time telemetry probe for ANY network, IP, domain, or gateway.
    """
    host = request.args.get("host", "8.8.8.8").strip()
    data = fast_live_probe(host)

    if data["latency"] is not None:
        insert_telemetry({
            "timestamp": data["timestamp"],
            "average_latency": data["latency"],
            "packet_loss": data["packet_loss"],
            "jitter": data["jitter"],
            "throughput": None
        })

    return jsonify(data), 200


@app.route("/api/multi-probe", methods=["GET"])
def get_multi_probe():
    """
    Probes multiple global DNS and CDN target hosts concurrently.
    """
    results = probe_multi_targets()
    return jsonify(results), 200


@app.route("/api/traceroute", methods=["GET"])
def get_visual_traceroute():
    """
    Performs hop-by-hop visual traceroute and pins the exact bottleneck hop.
    """
    target = request.args.get("target", "8.8.8.8")
    max_hops = int(request.args.get("max_hops", 12))
    res = run_traceroute(target=target, max_hops=max_hops)
    return jsonify(res), 200


@app.route("/api/dns-benchmark", methods=["GET"])
def get_dns_benchmark():
    """
    Benchmarks DNS resolution latency across top 5 global resolvers and generates 1-click optimization scripts.
    """
    domain = request.args.get("domain", "google.com")
    res = run_dns_benchmark(domain=domain)
    return jsonify(res), 200


@app.route("/api/port-scan", methods=["GET"])
def get_port_scan():
    """
    Probes critical TCP ports (HTTPS 443, HTTP 80, DNS 53, SSH 22, DoT 853) and measures TLS handshake latency.
    """
    host = request.args.get("host", "8.8.8.8")
    res = probe_critical_ports(host=host)
    return jsonify(res), 200


@app.route("/api/mtu-test", methods=["GET"])
def get_path_mtu_test():
    """
    Discovers optimal Path MTU and tests for packet fragmentation.
    """
    host = request.args.get("host", "8.8.8.8")
    res = test_path_mtu(host=host)
    return jsonify(res), 200


@app.route("/api/metrics", methods=["GET"])
def get_live_metrics():
    """
    Performs on-demand live network metrics measurement (Linux ping + Throughput).
    """
    host = request.args.get("host", "8.8.8.8")
    ping_count = int(request.args.get("count", 10))
    test_speed = request.args.get("speed", "true").lower() == "true"

    metrics = collect_metrics(host=host, ping_count=ping_count, test_speed=test_speed)

    # Save to telemetry stream if valid
    if metrics["is_valid"]:
        insert_telemetry(metrics)

    return jsonify(metrics), 200


@app.route("/api/diagnose", methods=["POST"])
def run_diagnosis():
    """
    Executes live network test, runs AI ML fault diagnosis,
    generates transparent recommendations, and records event to database.
    """
    data = request.get_json(silent=True) or {}
    host = data.get("host", "8.8.8.8")
    ping_count = int(data.get("count", 10))
    test_speed = bool(data.get("speed", True))

    # 1. Collect live network metrics
    metrics = collect_metrics(host=host, ping_count=ping_count, test_speed=test_speed)

    # 2. Run AI diagnosis engine
    diag_result = get_diagnosis(metrics)

    # 3. Log event to SQLite database
    record_id = None
    if metrics["is_valid"]:
        record_id = insert_diagnosis(metrics, diag_result)
        insert_telemetry(metrics)

    return jsonify({
        "id": record_id,
        "metrics": metrics,
        "diagnosis": diag_result
    }), 200


@app.route("/api/diagnose-custom", methods=["POST"])
def diagnose_custom_metrics():
    """
    Analyzes user-provided custom metrics payload (for UI simulation sandbox & defense testing).
    """
    metrics = request.get_json(silent=True)
    if not metrics:
        return jsonify({"error": "Invalid JSON payload"}), 400

    diag_result = get_diagnosis(metrics)
    return jsonify({
        "metrics": metrics,
        "diagnosis": diag_result
    }), 200


@app.route("/api/history", methods=["GET"])
def get_history():
    """
    Retrieves previous automated diagnosis records from SQLite.
    """
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))
    history_records = get_recent_diagnoses(limit=limit, offset=offset)
    return jsonify(history_records), 200


@app.route("/api/telemetry", methods=["GET"])
def get_telemetry_stream():
    """
    Retrieves historical telemetry data points for real-time Chart.js graphs.
    """
    limit = int(request.args.get("limit", 60))
    telemetry_data = get_recent_telemetry(limit=limit)
    return jsonify(telemetry_data), 200


@app.route("/api/statistics", methods=["GET"])
def get_system_statistics():
    """
    Returns aggregate diagnostic statistics.
    """
    stats = get_statistics()
    return jsonify(stats), 200


@app.route("/api/model-performance", methods=["GET"])
def get_model_performance():
    """
    Returns machine learning evaluation metrics (Accuracy, Precision, Recall, F1, Confusion Matrix).
    """
    if os.path.isfile(METRICS_JSON_PATH):
        with open(METRICS_JSON_PATH, "r", encoding="utf-8") as f:
            metrics_data = json.load(f)
        return jsonify(metrics_data), 200
    else:
        return jsonify({
            "status": "not_trained",
            "message": "ML model has not been evaluated yet. Run train_model.py to generate metrics."
        }), 200


@app.route("/api/retrain", methods=["POST"])
def retrain_model_endpoint():
    """
    Triggers ML model retraining on the current dataset.
    """
    try:
        from model.train_model import load_and_validate_dataset, train_and_compare_models, save_trained_artifacts
        X, y, class_dist = load_and_validate_dataset()
        results = train_and_compare_models(X, y)
        save_trained_artifacts(results, class_dist)
        engine.reload_model()
        return jsonify({
            "status": "success",
            "message": f"Successfully retrained model: {results['best_model_name']}",
            "best_model": results["best_model_name"]
        }), 200
    except Exception as err:
        return jsonify({"status": "error", "message": str(err)}), 500


# ==============================================================================
# FRONTEND PRODUCTION STATIC SERVING
# ==============================================================================

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    """
    Serves the compiled Vue 3 Cyber-NOC application in production.
    """
    if path != "" and os.path.exists(os.path.join(FRONTEND_DIST_DIR, path)):
        return send_from_directory(FRONTEND_DIST_DIR, path)
    elif os.path.exists(os.path.join(FRONTEND_DIST_DIR, "index.html")):
        return send_from_directory(FRONTEND_DIST_DIR, "index.html")
    else:
        return jsonify({
            "status": "online",
            "message": "Intelligent Network Assistant API is active. Build frontend via 'npm run build' to serve UI here."
        }), 200


# ==============================================================================
# ENTRYPOINT
# ==============================================================================

if __name__ == "__main__":
    verify_environment()
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "=" * 60)
    print(f" [OK] Starting Flask REST API Backend on http://0.0.0.0:{port}")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=False)
