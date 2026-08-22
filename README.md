# Intelligent Network Troubleshooting Assistant
> **BSIT Research Prototype**: *“An Intelligent Network Troubleshooting Assistant Using Network Performance Metrics for Automated Fault Diagnosis”*

An automated network monitoring and fault diagnosis system that analyzes Linux network performance metrics (Latency, Packet Loss, Jitter, Throughput), classifies network anomalies using Machine Learning (Decision Tree, Random Forest, Logistic Regression), and generates transparent, explainable root-cause diagnoses and actionable troubleshooting recommendations through a Cyberpunk/NOC-style Vue 3 dashboard.

---

## 1. System Architecture

```text
               +----------------------------------+
               |   Linux Network Traffic / WSL2   |
               | (ping, Cloudflare CDN, tc netem) |
               +-----------------+----------------+
                                 |
                                 v
               +----------------------------------+
               |      Network Monitor Engine      |
               |       (network_monitor.py)       |
               +-----------------+----------------+
                                 |
                     +-----------+-----------+
                     |                       |
                     v                       v
        +-------------------------+  +-------------------+
        |    Dataset Collector    |  |    SQLite DB      |
        |   (data_collector.py)   |  |   (network.db)    |
        +------------+------------+  +---------+---------+
                     |                         |
                     v                         |
        +-------------------------+            |
        | Machine Learning Model  |            |
        |   (Decision Tree 96%)   |            |
        +------------+------------+            |
                     |                         |
                     v                         v
        +----------------------------------------------+
        |        Explainable Diagnosis Engine          |
        |            (diagnosis_engine.py)             |
        +----------------------+-----------------------+
                               |
                               v
        +----------------------------------------------+
        |             Flask REST API Backend           |
        |                    (app.py)                  |
        +----------------------+-----------------------+
                               |
                               v
        +----------------------------------------------+
        |         Vue 3 Cyber-NOC Dashboard            |
        |   (Matrix Rain, Telemetry HUD, Chart.js)     |
        +----------------------------------------------+
```

---

## 2. Research Variables & Fault Classes

### Independent Variables (Performance Metrics)
1. **Minimum Latency** (ms)
2. **Maximum Latency** (ms)
3. **Average Latency** (ms)
4. **Packet Loss** (%)
5. **Jitter** (ms, RFC 3550 standard)
6. **Throughput** (Mbps)

### Dependent Variable (Automated Fault Classification)
1. `normal` — Nominal baseline network performance.
2. `high_latency` — Significant round-trip delay (>150ms).
3. `packet_loss` — Noticeable packet discarding (>5%).
4. `high_jitter` — High latency variance/bufferbloat without high average latency.
5. `congestion` — Constrained throughput (<2 Mbps) combined with queue delays.

---

## 3. WSL2 Simulation Commands (`tc netem`)

| Fault Class | Linux `tc netem` Command | Expected Metrics Signature |
| :--- | :--- | :--- |
| **Normal** | `sudo tc qdisc del dev eth0 root 2>/dev/null` | Latency: 15–30ms, Loss: 0%, Jitter: <3ms, Speed: >40 Mbps |
| **High Latency** | `sudo tc qdisc add dev eth0 root netem delay 200ms 10ms` | Latency: ~200–230ms, Loss: 0%, Jitter: Low-Med |
| **Packet Loss** | `sudo tc qdisc add dev eth0 root netem loss 10%` | Latency: Normal, Loss: ~10%, Jitter: Low |
| **High Jitter** | `sudo tc qdisc add dev eth0 root netem delay 25ms 20ms distribution normal` | Latency: 20–45ms, Loss: 0%, **Jitter: >15–30ms** |
| **Congestion** | `sudo tc qdisc add dev eth0 root netem rate 1.5mbit delay 80ms 25ms loss 3%` | Latency: 80–120ms, Loss: ~3%, **Throughput: <1.5 Mbps** |
| **Reset/Clear** | `sudo tc qdisc del dev eth0 root` | Reverts interface to normal |

---

## 4. Quick Start & Execution Guide

### Backend (WSL2 Ubuntu)

```bash
# 1. Navigate to backend inside WSL2
cd /mnt/c/IntelligentNetworkAssistant/backend

# 2. Install requirements
pip install -r requirements.txt

# 3. (Optional) Run dataset collector to capture new samples
python3 data_collector.py

# 4. Train and benchmark ML models
python3 model/train_model.py

# 5. Start Flask REST API
python3 app.py
```
Backend runs at: `http://localhost:5000`

### Frontend (Vue 3 + Vite Cyber-NOC)

```bash
# In Windows PowerShell or WSL terminal
cd c:\IntelligentNetworkAssistant\frontend

# Install dependencies (first time only)
npm install

# Start Vite development server
npm run dev
```
Frontend runs at: `http://localhost:3000`

---

## 5. API Endpoints

- `GET  /api/status` — System health, OS detection, active ML classifier info.
- `GET  /api/metrics?host=8.8.8.8` — Live network metrics measurement.
- `POST /api/diagnose` — Automated live diagnosis scan + SQLite logging.
- `POST /api/diagnose-custom` — Sandbox simulation diagnosis for custom metrics.
- `GET  /api/history` — Audit trail of previous diagnoses.
- `GET  /api/telemetry` — Time-series telemetry points for live Chart.js graphs.
- `GET  /api/statistics` — Aggregate breakdown by fault type.
- `GET  /api/model-performance` — ML evaluation metrics, confusion matrix, and model comparison.
- `POST /api/retrain` — Retrains the ML pipeline on the latest dataset.
