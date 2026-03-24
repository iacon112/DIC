"""
Streamlit Dashboard — reads from SQLite and displays KPIs, charts, and raw data.
Auto-refreshes every 5 seconds.
"""

import os
import sqlite3
import time
import streamlit as st
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aiotdb.db")

st.set_page_config(
    page_title="AIoT Sensor Dashboard",
    page_icon="📡",
    layout="wide",
)

st.title("📡 AIoT Sensor Dashboard")
st.caption("ESP32 + DHT11 → Flask → SQLite → Streamlit")


@st.cache_resource
def get_connection():
    """Return a shared SQLite connection (read-only)."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def load_data(limit: int = 200) -> pd.DataFrame:
    """Load the most recent sensor rows into a DataFrame."""
    conn = get_connection()
    try:
        df = pd.read_sql_query(
            f"SELECT * FROM sensors ORDER BY id DESC LIMIT {limit}",
            conn,
        )
    except Exception:
        return pd.DataFrame()
    return df


# ── Load data ────────────────────────────────────────────────────────────

df = load_data()

if df.empty:
    st.warning("No sensor data yet. Start the Flask server and ESP32 simulator.")
    time.sleep(5)
    st.rerun()
else:
    # ── KPI Cards ────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📊 Total Readings", len(df))
    k2.metric("🌡️ Avg Temperature", f"{df['temperature'].mean():.1f} °C")
    k3.metric("💧 Avg Humidity", f"{df['humidity'].mean():.1f} %")
    k4.metric("📟 Last Device", df.iloc[0]["device_id"])

    st.divider()

    # ── Charts ───────────────────────────────────────────────────────────
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

    # ── Raw Data Table ───────────────────────────────────────────────────
    st.subheader("📋 Raw Sensor Data (last 200)")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Auto-refresh ─────────────────────────────────────────────────────
    time.sleep(5)
    st.rerun()
