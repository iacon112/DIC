"""
Flask API — receives ESP32 sensor POSTs, stores to SQLite3.
"""

import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, g

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aiotdb.db")


# ── Database helpers ─────────────────────────────────────────────────────

def get_db():
    """Return a per-request database connection."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the sensors table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sensors (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id   TEXT    NOT NULL,
            ssid        TEXT,
            ip_address  TEXT,
            temperature REAL    NOT NULL,
            humidity    REAL    NOT NULL,
            timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


# ── Routes ───────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    """Liveness check."""
    return jsonify({"status": "ok", "db": DB_PATH})


@app.route("/sensor", methods=["POST"])
def receive_sensor_data():
    """Accept a DHT11 payload and save to DB."""
    data = request.get_json(force=True)

    required = ("device_id", "temperature", "humidity")
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    db = get_db()
    db.execute(
        """INSERT INTO sensors (device_id, ssid, ip_address, temperature, humidity)
           VALUES (?, ?, ?, ?, ?)""",
        (
            data["device_id"],
            data.get("ssid"),
            data.get("ip_address"),
            data["temperature"],
            data["humidity"],
        ),
    )
    db.commit()
    return jsonify({"status": "saved"}), 201


@app.route("/sensors", methods=["GET"])
def get_sensors():
    """Return the last 100 sensor readings."""
    db = get_db()
    rows = db.execute(
        "SELECT * FROM sensors ORDER BY id DESC LIMIT 100"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/sensors/count", methods=["GET"])
def sensor_count():
    """Return total row count."""
    db = get_db()
    count = db.execute("SELECT COUNT(*) FROM sensors").fetchone()[0]
    return jsonify({"count": count})


# ── Entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print(f"[flask_app] Database: {DB_PATH}")
    app.run(host="0.0.0.0", port=5000)
