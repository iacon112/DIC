# Development Log — AIoT Streamlit Dashboard

## Objective
Build and deploy a local Python AIoT demo (ESP32 Simulator → Flask → SQLite → Streamlit) and prepare it for live cloud deployment on Streamlit Cloud to fulfill HW1 requirements.

## 2026-03-24: Phase 1 — Local Demo Implementation
- **Goal:** Establish the core data pipeline and local visualization.
- **Architecture:** 
  - `esp32_sim.py`: Simulates an ESP32 sending DHT11 data (temperature, humidity).
  - `flask_app.py`: Receives POST requests, writes to SQLite3 (`aiotdb.db`).
  - `streamlit_app.py`: Reads from SQLite3, displays KPIs, charts, and raw data table.
- **Result:** Successfully built and verified the local pipeline. The dashboard correctly displayed real-time updates when both Flask and the ESP32 simulator were running.

## 2026-03-24: Phase 2 — Preparation for Streamlit Cloud Deployment
- **Goal:** Adapt the local Streamlit dashboard to run standalone on Streamlit Cloud, fulfilling the "live demo" requirement for HW1.
- **Problem:** Streamlit Cloud only hosts the Streamlit app. It does not run background Flask servers or separate simulator scripts.
- **Solution — "Self-Contained Mode":**
  1. **Built-in Database Management:** Modified `streamlit_app.py` to automatically create the `sensors` table using `init_db()` if it doesn't exist.
  2. **Integrated Simulator:** Added a built-in simulator directly inside `streamlit_app.py`. It uses Streamlit's session state and `st.rerun()` (or auto-rerun logic) to generate and insert fake DHT11 data periodically.
  3. **Sidebar Controls:** Added a control panel in the sidebar allowing users to set temperature/humidity ranges, toggle auto-simulation, manually add readings, and clear the database.
  4. **Initial Data Seeding:** Added functionality to seed the database with 30 initial historical records on first load so charts aren't empty immediately.
- **UI/UX Enhancements:** 
  - Created `.streamlit/config.toml` to enforce a dark theme (primary color red, dark background) for a premium look.
- **Dependency Optimization:** Updated `requirements.txt` to remove `flask` and `requests`, as they are no longer needed for the cloud version, keeping the deployment lightweight (`streamlit`, `pandas`).

## Verification & Outcomes
- **Local Standalone Test:** Deleted the existing `aiotdb.db` and ran the new `streamlit_app.py` directly without Flask.
- **Result:** The dashboard successfully initialized the database, seeded data, and began auto-simulating new readings. The charts (Temperature & Humidity), KPIs, and Raw Data Table all rendered correctly.
- **Next Steps:** 
  1. Push the repository to GitHub.
  2. Connect the GitHub repository to Streamlit Cloud (share.streamlit.io).
  3. Deploy the application to obtain a live public URL.

---

## Appendix: Conversation History & Decision Process

### User Request 0 (Initial Setup of AIoT Demo)
> "Create and fully run a local Python AIoT demo in this workspace: esp32_sim.py sends fake DHT11 data... Flask stores into SQLite3... Streamlit reads SQLite and shows KPI... Do not add WiFi delay, packet loss, or network simulation."

- **Assistant Response:**
  - Created an implementation plan detailing the 4 files (`flask_app.py`, `esp32_sim.py`, `streamlit_app.py`, `requirements.txt`).
  - Executed the plan by creating the files.
  - Initialized a Python virtual environment and installed all dependencies (`flask`, `requests`, `streamlit`, `pandas`).
  - Started the Flask API on port 5000 and verified the `/health` endpoint.
  - Started the ESP32 Simulator script to POST data every 5 seconds.
  - Verified SQLite database (`aiotdb.db`) insertion.
  - Launched the Streamlit dashboard (`localhost:8501`) and verified via a browser screenshot that the UI rendered correctly.
  - Documented the entire process in `walkthrough.md`.

### User Request 1
> "DEMO 的報告檔案呢?"

- **Assistant Response:** Located the previous `walkthrough.md` and `implementation_plan.md` artifacts containing the architecture, verification results, and initial plan. Asked if they should be copied to the local project folder.

### User Request 2
> "需要我把報告複製到專案目錄 c:\Users\USER\Desktop\IoT_L1\"

- **Assistant Response:** Copied `walkthrough.md`, `implementation_plan.md`, and the verification screenshot `streamlit_dashboard_verify.webp` to the target directory.

### User Request 3
> "HW1 AIoT System (重點是要有兩個部分: 真實地和模擬的, 可以寫成兩個獨立的或是合再一起的)
1. github
2. live demo on vercel or streamlit
3. development log 它的要求是要交甚麼?"

- **Assistant Response:** Outlined the 3 requirements based on the user's prompt:
  1. Push the code to a GitHub repo.
  2. Deploy a live demo on Streamlit Cloud (or Vercel).
  3. Create a Development Log documenting the build process and decisions.
  Noted that the simulated end was done, and asked which part to tackle next.

### User Request 4
> "Streamlit Cloud 部署"

- **Assistant Response:** 
  - **Planning:** Reviewed the current architecture and identified that the local setup relied on a background Flask server which wouldn't work on Streamlit Cloud.
  - **Proposed Solution:** Modify `streamlit_app.py` to be self-contained, with a built-in DB initializer and an integrated simulator using Streamlit's state. Simplify `requirements.txt` to only include `streamlit` and `pandas`.
  - **Execution:** Implemented the changes, created a `.streamlit/config.toml` for a premium dark theme, and verified the standalone app locally to confirm charts, data table, and the new sidebar simulator control panel rendered perfectly without Flask running.



