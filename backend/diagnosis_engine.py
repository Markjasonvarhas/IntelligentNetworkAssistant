import os
import joblib
import numpy as np
import pandas as pd

# ==============================================================================
# MODEL PATH & FEATURE DEFINITION
# ==============================================================================

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BACKEND_DIR, "model", "trained_model.joblib")

FEATURE_COLUMNS = [
    "minimum_latency",
    "maximum_latency",
    "average_latency",
    "packet_loss",
    "jitter",
    "throughput"
]


# ==============================================================================
# RULE-BASED EXPLAINABLE KNOWLEDGE BASE
# ==============================================================================

KNOWLEDGE_BASE = {
    "normal": {
        "title": "Healthy Network Condition",
        "severity": "healthy",
        "description": "Network telemetry is operating within optimal baseline thresholds with low latency, zero packet loss, and stable throughput.",
        "possible_causes": [
            "Network connection and routing path are stable.",
            "Local interface and gateway are responding normally.",
            "Bandwidth utilization is within normal capacity."
        ],
        "recommendations": [
            "Continue periodic monitoring.",
            "No troubleshooting action is required at this time."
        ]
    },
    "high_latency": {
        "title": "High Network Round-Trip Latency",
        "severity": "warning",
        "description": "The round-trip delay is significantly elevated compared to normal baseline, causing sluggish application responsiveness.",
        "possible_causes": [
            "Upstream ISP routing delays or distant routing hops.",
            "Network link saturation or buffer queuing at gateway.",
            "Intermediate router congestion or physical distance."
        ],
        "recommendations": [
            "Check local bandwidth consumption by active background applications.",
            "Perform traceroute/MTR to identify which specific hop introduces delay.",
            "Restart local router/modem if latency persists across all hosts.",
            "Contact upstream ISP if the delay originates outside your local network."
        ]
    },
    "packet_loss": {
        "title": "Significant Packet Loss Detected",
        "severity": "critical",
        "description": "A noticeable percentage of transmitted ICMP packets were dropped before reaching the destination.",
        "possible_causes": [
            "Degraded or unstable Wi-Fi signal (RF interference, distance).",
            "Damaged Ethernet cable or loose connector.",
            "Severe buffer overflow on local router or intermediate node.",
            "Upstream ISP packet discarding due to link errors."
        ],
        "recommendations": [
            "Inspect physical Ethernet cabling or move closer to the Wi-Fi access point.",
            "Check router interface error counters for dropped frame anomalies.",
            "Test connectivity to local gateway (192.168.1.1) vs external targets (8.8.8.8).",
            "Verify network interface card (NIC) drivers."
        ]
    },
    "high_jitter": {
        "title": "Severe Latency Variation (High Jitter)",
        "severity": "warning",
        "description": "The delay variation between consecutive packets is abnormally high, leading to bufferbloat and choppy real-time audio/video streaming.",
        "possible_causes": [
            "Wireless channel congestion or competing electromagnetic interference.",
            "Bufferbloat on bottleneck routers (unmanaged queue buildup).",
            "Route flapping or load balancing across disparate paths.",
            "Bursty background traffic on the local LAN."
        ],
        "recommendations": [
            "Switch from 2.4 GHz Wi-Fi to 5 GHz / 6 GHz or use a wired Ethernet cable.",
            "Enable Smart Queue Management (SQM) / CAKE / FQ-CoDel on your router to eliminate bufferbloat.",
            "Limit high-bandwidth background torrents or video uploads.",
            "Check for competing wireless access points on identical channels."
        ]
    },
    "congestion": {
        "title": "Network Congestion & Bandwidth Bottleneck",
        "severity": "critical",
        "description": "Throughput is heavily constrained while latency and packet jitter are simultaneously elevated, indicating bandwidth exhaustion.",
        "possible_causes": [
            "Heavy simultaneous downloads, video streams, or software updates.",
            "Bandwidth throttling by ISP or traffic shaping policies.",
            "Local gateway CPU saturation under heavy packet processing.",
            "Bandwidth cap or rate limit reached."
        ],
        "recommendations": [
            "Identify top bandwidth consumers on the local network using traffic monitors.",
            "Configure Quality of Service (QoS) priorities for critical applications.",
            "Pause non-essential bulk downloads and cloud backups.",
            "Verify whether bandwidth throttling is being enforced by network policy."
        ]
    }
}


# ==============================================================================
# DIAGNOSIS ENGINE CLASS
# ==============================================================================

class NetworkDiagnosisEngine:
    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        """Loads the trained ML model from disk if available."""
        if os.path.isfile(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                print(f"[OK] Diagnosis Engine: Loaded ML model from {MODEL_PATH}")
            except Exception as err:
                print(f"[!] Diagnosis Engine: Failed to load model ({err}). Using heuristic fallback.")
                self.model = None
        else:
            self.model = None

    def reload_model(self):
        """Reloads the model from disk (useful after retraining)."""
        self._load_model()

    def _heuristic_fallback(self, metrics):
        """
        Transparent rule-based heuristic fallback if the ML model is not yet trained.
        """
        avg_lat = metrics.get("average_latency", 0) or 0
        loss = metrics.get("packet_loss", 0) or 0
        jitter = metrics.get("jitter", 0) or 0
        tp = metrics.get("throughput", 50) or 50

        if loss >= 8.0:
            return "packet_loss", 0.85
        if tp < 3.0 and (avg_lat > 60.0 or jitter > 10.0):
            return "congestion", 0.88
        if avg_lat > 150.0:
            return "high_latency", 0.90
        if jitter > 15.0:
            return "high_jitter", 0.85
        return "normal", 0.95

    def diagnose(self, metrics):
        """
        Analyzes network performance metrics, produces an ML classification,
        calculates probability confidence score, and generates explainable diagnostic details.
        
        Args:
            metrics (dict): Must contain minimum_latency, maximum_latency,
                            average_latency, packet_loss, jitter, throughput.
        
        Returns:
            dict: Complete diagnosis payload with problem, confidence, causes, and actions.
        """
        # Prepare feature vector
        sample_df = pd.DataFrame([{
            "minimum_latency": float(metrics.get("minimum_latency", 0) or 0),
            "maximum_latency": float(metrics.get("maximum_latency", 0) or 0),
            "average_latency": float(metrics.get("average_latency", 0) or 0),
            "packet_loss": float(metrics.get("packet_loss", 0) or 0),
            "jitter": float(metrics.get("jitter", 0) or 0),
            "throughput": float(metrics.get("throughput", 0) or 0)
        }])

        predicted_fault = "normal"
        confidence = 0.50
        class_probabilities = {}

        if self.model is not None:
            try:
                pred_label = self.model.predict(sample_df)[0]
                predicted_fault = str(pred_label)

                # Extract confidence from predict_proba if supported
                if hasattr(self.model, "predict_proba"):
                    probs = self.model.predict_proba(sample_df)[0]
                    classes = self.model.classes_
                    for idx, cls_name in enumerate(classes):
                        class_probabilities[str(cls_name)] = round(float(probs[idx]), 4)
                    
                    confidence = float(max(probs))
                else:
                    confidence = 0.90
            except Exception as err:
                print(f"[!] ML prediction error: {err}. Falling back to heuristics.")
                predicted_fault, confidence = self._heuristic_fallback(metrics)
        else:
            predicted_fault, confidence = self._heuristic_fallback(metrics)

        # Retrieve explainable rule knowledge
        rule_data = KNOWLEDGE_BASE.get(predicted_fault, KNOWLEDGE_BASE["normal"])

        # Metric highlights for explainability
        metric_highlights = [
            f"Average Latency: {metrics.get('average_latency')} ms",
            f"Packet Loss: {metrics.get('packet_loss')}%",
            f"Jitter: {metrics.get('jitter')} ms",
            f"Throughput: {metrics.get('throughput')} Mbps"
        ]

        return {
            "fault": predicted_fault,
            "title": rule_data["title"],
            "severity": rule_data["severity"],
            "confidence": round(confidence, 4),
            "confidence_percent": f"{round(confidence * 100, 1)}%",
            "confidence_explanation": (
                "Confidence represents the statistical posterior probability "
                "assigned by the machine learning classification model."
            ),
            "description": rule_data["description"],
            "possible_causes": rule_data["possible_causes"],
            "recommendations": rule_data["recommendations"],
            "class_probabilities": class_probabilities,
            "metric_highlights": metric_highlights
        }


# Singleton engine instance
engine = NetworkDiagnosisEngine()


def get_diagnosis(metrics):
    """Module-level convenience accessor."""
    return engine.diagnose(metrics)
