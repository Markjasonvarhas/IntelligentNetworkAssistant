import os
import sqlite3
import json
from datetime import datetime

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BACKEND_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "network.db")


def get_db_connection():
    """Returns a connection to the SQLite database with row dictionary mapping."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes SQLite database tables for diagnosis history and real-time telemetry."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table 1: Diagnosis History
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diagnoses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            host TEXT NOT NULL,
            minimum_latency REAL,
            maximum_latency REAL,
            average_latency REAL,
            packet_loss REAL,
            jitter REAL,
            throughput REAL,
            fault TEXT NOT NULL,
            title TEXT NOT NULL,
            severity TEXT NOT NULL,
            confidence REAL NOT NULL,
            possible_causes_json TEXT,
            recommendations_json TEXT
        )
    """)

    # Table 2: Real-time Telemetry Stream (for charts & live HUD)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry_stream (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            latency REAL,
            packet_loss REAL,
            jitter REAL,
            throughput REAL
        )
    """)

    conn.commit()
    conn.close()


def insert_diagnosis(metrics, diagnosis_res):
    """Inserts an automated diagnosis event into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    timestamp = metrics.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    host = metrics.get("host", "8.8.8.8")

    cursor.execute("""
        INSERT INTO diagnoses (
            timestamp, host, minimum_latency, maximum_latency, average_latency,
            packet_loss, jitter, throughput, fault, title, severity, confidence,
            possible_causes_json, recommendations_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp,
        host,
        metrics.get("minimum_latency"),
        metrics.get("maximum_latency"),
        metrics.get("average_latency"),
        metrics.get("packet_loss"),
        metrics.get("jitter"),
        metrics.get("throughput"),
        diagnosis_res.get("fault", "normal"),
        diagnosis_res.get("title", "Unknown"),
        diagnosis_res.get("severity", "normal"),
        diagnosis_res.get("confidence", 0.0),
        json.dumps(diagnosis_res.get("possible_causes", [])),
        json.dumps(diagnosis_res.get("recommendations", []))
    ))

    diag_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return diag_id


def get_recent_diagnoses(limit=50, offset=0):
    """Retrieves recent diagnosis records formatted for API responses."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM diagnoses
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))

    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "host": r["host"],
            "metrics": {
                "minimum_latency": r["minimum_latency"],
                "maximum_latency": r["maximum_latency"],
                "average_latency": r["average_latency"],
                "packet_loss": r["packet_loss"],
                "jitter": r["jitter"],
                "throughput": r["throughput"]
            },
            "diagnosis": {
                "fault": r["fault"],
                "title": r["title"],
                "severity": r["severity"],
                "confidence": r["confidence"],
                "confidence_percent": f"{round(r['confidence'] * 100, 1)}%",
                "possible_causes": json.loads(r["possible_causes_json"] or "[]"),
                "recommendations": json.loads(r["recommendations_json"] or "[]")
            }
        })
    return results


def insert_telemetry(metrics):
    """Inserts a live telemetry measurement point."""
    conn = get_db_connection()
    cursor = conn.cursor()

    timestamp = metrics.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    cursor.execute("""
        INSERT INTO telemetry_stream (timestamp, latency, packet_loss, jitter, throughput)
        VALUES (?, ?, ?, ?, ?)
    """, (
        timestamp,
        metrics.get("average_latency"),
        metrics.get("packet_loss"),
        metrics.get("jitter"),
        metrics.get("throughput")
    ))

    conn.commit()
    conn.close()


def get_recent_telemetry(limit=60):
    """Returns historical telemetry data points for live Chart.js time-series plots."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, latency, packet_loss, jitter, throughput
        FROM telemetry_stream
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    # Return in chronological order
    rows.reverse()
    return [{
        "timestamp": r["timestamp"],
        "latency": r["latency"],
        "packet_loss": r["packet_loss"],
        "jitter": r["jitter"],
        "throughput": r["throughput"]
    } for r in rows]


def get_statistics():
    """Computes high-level aggregated research diagnostic statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM diagnoses")
    total_scans = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT fault, COUNT(*) as count, AVG(confidence) as avg_conf
        FROM diagnoses
        GROUP BY fault
    """)
    fault_breakdown = {}
    for r in cursor.fetchall():
        fault_breakdown[r["fault"]] = {
            "count": r["count"],
            "avg_confidence": round(float(r["avg_conf"] or 0.0), 4)
        }

    conn.close()
    return {
        "total_diagnoses": total_scans,
        "fault_breakdown": fault_breakdown
    }


# Initialize tables on import
init_db()
