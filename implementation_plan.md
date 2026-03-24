# AIoT Demo: ESP32 Simulator → Flask → SQLite → Streamlit

Build a local Python AIoT demo in `c:\Users\USER\IoT_L1`.

## Proposed Changes

### Application Files

#### [NEW] [requirements.txt](file:///c:/Users/USER/IoT_L1/requirements.txt)
- `flask`, `requests`, `streamlit`, `pandas`

#### [NEW] [flask_app.py](file:///c:/Users/USER/IoT_L1/flask_app.py)
- Flask API on port 5000
- `GET /health` — liveness check
- `POST /sensor` — accepts JSON payload, inserts into SQLite
- `GET /sensors` — returns last 100 readings
- `GET /sensors/count` — total row count
- Auto-creates `aiotdb.db` with `sensors` table on startup

#### [NEW] [esp32_sim.py](file:///c:/Users/USER/IoT_L1/esp32_sim.py)
- Sends fake DHT11 data every 5s via HTTP POST to `/sensor`
- Payload: `device_id`, `ssid`, `ip_address`, `temperature`, `humidity`
- No WiFi delay or network simulation

#### [NEW] [streamlit_app.py](file:///c:/Users/USER/IoT_L1/streamlit_app.py)
- 4 KPI cards: Total Readings, Avg Temp, Avg Humidity, Last Device
- Temperature line chart (red), Humidity line chart (teal)
- Raw data table (last 200 rows)
- Auto-refresh every 5s

### Environment Setup
- Create venv in `c:\Users\USER\IoT_L1\venv`
- Install dependencies from `requirements.txt`

## Verification Plan

### Automated Tests
1. `curl http://127.0.0.1:5000/health` → expect `{"status": "ok"}`
2. Start `esp32_sim.py`, wait ~15s, query `SELECT COUNT(*) FROM sensors` → expect ≥ 2 rows
3. `python -m streamlit run streamlit_app.py --server.port 8501 --server.headless true` → expect process running
4. Open `http://localhost:8501` in browser to verify dashboard renders
