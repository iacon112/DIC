"""
Streamlit Dashboard — AIoT Sensor Data Visualization.

Cloud-compatible: contains a built-in simulator so it works on Streamlit Cloud
without Flask or a separate ESP32 simulator process.
Locally, it can also display data written by flask_app.py + esp32_sim.py.
"""

import os
import sqlite3
import random
import time
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd

import tempfile
import shutil

# ── Config ───────────────────────────────────────────────────────────────
LOCAL_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aiotdb.db")
TEMP_DB_PATH = os.path.join(tempfile.gettempdir(), "aiotdb.db")

def is_sqlite_writable(db_path):
    """Real test to see if SQLite can actually write to this database file."""
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS _test_write (id INTEGER)")
        conn.execute("INSERT INTO _test_write (id) VALUES (1)")
        conn.execute("DROP TABLE _test_write")
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

# 如果本機的 SQLite 資料庫檔可以成功寫入，就用本機的；否則 (Streamlit Cloud) 改用系統暫存區
if is_sqlite_writable(LOCAL_DB_PATH):
    DB_PATH = LOCAL_DB_PATH
else:
    DB_PATH = TEMP_DB_PATH
    # 如果暫存區已經有檔案，但因為先前的錯誤導致它是唯讀的，就強制作廢它
    if os.path.exists(DB_PATH) and not is_sqlite_writable(DB_PATH):
        try:
            os.remove(DB_PATH)
            st.cache_resource.clear() # 清除 Streamlit 的連線快取，強制重連新的可寫入檔案
        except Exception:
            pass
            
    # 如果暫存區沒有檔案，從本機複製一份過去並確保可讀寫
    if os.path.exists(LOCAL_DB_PATH) and not os.path.exists(DB_PATH):
        try:
            shutil.copyfile(LOCAL_DB_PATH, DB_PATH)
            import stat
            os.chmod(DB_PATH, stat.S_IREAD | stat.S_IWRITE)
        except Exception:
            pass

st.set_page_config(
    page_title="AIoT Sensor Dashboard",
    page_icon="📡",
    layout="wide",
)


# ── Database helpers ─────────────────────────────────────────────────────

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


@st.cache_resource
def get_connection():
    """Return a shared SQLite connection."""
    init_db()
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def insert_simulated_reading(conn, device_id, temp_range, hum_range):
    """Insert one fake sensor reading into the database."""
    conn.execute(
        """INSERT INTO sensors (device_id, ssid, ip_address, temperature, humidity)
           VALUES (?, ?, ?, ?, ?)""",
        (
            device_id,
            "Simulated_WiFi",
            "10.0.0.1",
            round(random.uniform(*temp_range), 1),
            round(random.uniform(*hum_range), 1),
        ),
    )
    conn.commit()


def seed_initial_data(conn, device_id, count=30):
    """Seed the database with historical simulated data if empty."""
    row_count = conn.execute("SELECT COUNT(*) FROM sensors").fetchone()[0]
    if row_count > 0:
        return
    base_time = datetime.now() - timedelta(seconds=count * 5)
    for i in range(count):
        ts = base_time + timedelta(seconds=i * 5)
        conn.execute(
            """INSERT INTO sensors (device_id, ssid, ip_address, temperature, humidity, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                device_id,
                "Simulated_WiFi",
                "10.0.0.1",
                round(random.uniform(20.0, 35.0), 1),
                round(random.uniform(45.0, 75.0), 1),
                ts.strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
    conn.commit()


def load_data(conn, limit: int = 200) -> pd.DataFrame:
    """Load the most recent sensor rows into a DataFrame."""
    try:
        df = pd.read_sql_query(
            f"SELECT * FROM sensors ORDER BY id DESC LIMIT {limit}",
            conn,
        )
    except Exception:
        return pd.DataFrame()
    return df


# ── Sidebar ──────────────────────────────────────────────────────────────

st.sidebar.title("⚙️ Simulator Controls")
st.sidebar.caption("Built-in ESP32 + DHT11 Simulator")

device_id = st.sidebar.text_input("Device ID", value="ESP32-AIOT-001")
temp_min, temp_max = st.sidebar.slider(
    "🌡️ Temperature Range (°C)", 0.0, 50.0, (20.0, 35.0), 0.5
)
hum_min, hum_max = st.sidebar.slider(
    "💧 Humidity Range (%)", 0.0, 100.0, (45.0, 75.0), 0.5
)

auto_sim = st.sidebar.toggle("▶️ Auto-Simulate (every 3s)", value=True)

add_one = st.sidebar.button("➕ Add 1 Reading Now")

if st.sidebar.button("🗑️ Clear Database"):
    conn_tmp = sqlite3.connect(DB_PATH)
    conn_tmp.execute("DELETE FROM sensors")
    conn_tmp.commit()
    conn_tmp.close()
    st.cache_resource.clear()
    st.rerun()

st.sidebar.divider()
st.sidebar.info(
    "This dashboard works **standalone** on Streamlit Cloud.\n\n"
    "Locally, you can also run `flask_app.py` + `esp32_sim.py` to inject real/simulated data."
)


# ── Main ─────────────────────────────────────────────────────────────────

st.title("📡 AIoT Sensor Dashboard")
st.caption("ESP32 + DHT11 → SQLite → Streamlit  |  Cloud-Ready Demo")

conn = get_connection()

# Seed initial data on first run
seed_initial_data(conn, device_id)

# Simulate a new reading
if add_one or auto_sim:
    insert_simulated_reading(
        conn, device_id, (temp_min, temp_max), (hum_min, hum_max)
    )

# Load data
df = load_data(conn)

if df.empty:
    st.warning("No sensor data yet. Click '➕ Add 1 Reading Now' in the sidebar.")
else:
    # ── KPI Cards ────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📊 Total Readings", len(df))
    k2.metric("🌡️ Avg Temperature", f"{df['temperature'].mean():.1f} °C")
    k3.metric("💧 Avg Humidity", f"{df['humidity'].mean():.1f} %")
    k4.metric("📟 Last Device", df.iloc[0]["device_id"])

    st.divider()

    # ── Charts ───────────────────────────────────────────────────────
    chart_df = df.sort_values("id").copy()
    chart_df["timestamp"] = pd.to_datetime(chart_df["timestamp"])
    chart_df = chart_df.set_index("timestamp")

    col_temp, col_hum = st.columns(2)

    with col_temp:
        st.subheader("🌡️ Temperature Over Time")
        st.line_chart(chart_df["temperature"], color="#FF4B4B")

    with col_hum:
        st.subheader("💧 Humidity Over Time")
        st.line_chart(chart_df["humidity"], color="#00C9A7")

    st.divider()

    # ── Raw Data Table ───────────────────────────────────────────────
    st.subheader("📋 Raw Sensor Data (last 200)")
    st.dataframe(df, use_container_width=True, hide_index=True)

# ── Auto-refresh ─────────────────────────────────────────────────────
if auto_sim:
    time.sleep(3)
    st.rerun()
