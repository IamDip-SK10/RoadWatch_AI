# 🛣️ RoadWatch AI

**Advanced Road Safety Analytics & Citizen Grievance Platform**
*Built for the IIT Madras Road Safety Hackathon*

---

## Overview

RoadWatch AI is a fully self-contained, single-file Streamlit application that combines:

- **Executive analytics dashboard** with 15 interactive Plotly visualisations across 4 tabs
- **State-driven conversational AI assistant** powered by Google Gemini 1.5 Flash
- **Multi-city automated grievance routing** with contractor transparency
- **Robust fallback engine** — the dashboard never crashes if the Gemini API is unavailable

---

## Project Structure

```
roadwatch-ai/
├── app.py               ← Entire application (single-file, no sub-modules)
├── requirements.txt     ← Pinned Python dependencies
├── README.md            ← This file
└── .streamlit/
    └── secrets.toml     ← Local API key (NOT committed to git)
```

---

## Quick Start (Local)

### 1. Clone & create a virtual environment

```bash
git clone https://github.com/your-org/roadwatch-ai.git
cd roadwatch-ai
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Gemini API key

```bash
mkdir -p .streamlit
cat > .streamlit/secrets.toml << 'TOML'
GEMINI_API_KEY = "your-google-gemini-api-key-here"
TOML
```

> **Get a free key:** https://aistudio.google.com/app/apikey
> The app works fully without a key — it automatically falls back to a
> rule-based DataFrame response engine.

### 4. Run the app

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`.

---

## Deploying to Streamlit Cloud (Free Tier)

1. Push the repo (with `app.py` and `requirements.txt`) to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Select your repo, branch, and set **Main file path** to `app.py`.
4. Under **Advanced settings → Secrets**, paste:

```toml
GEMINI_API_KEY = "your-google-gemini-api-key-here"
```

5. Click **Deploy**. No multi-file issues — everything lives in `app.py`.

---

## Using the Application

### Step 1 — Upload Dataset
Upload `indian_roads_dataset.csv` **or** the ZIP archive containing it.
The app reads everything entirely in memory — nothing is written to disk.

### Step 2 — Filter Data
Use the **sidebar** to filter by:

| Filter | Notes |
|--------|-------|
| State | Multi-select; city list auto-populates from selection |
| City | Multi-select; drives both analytics and grievance tickets |
| Accident Severity | fatal / major / minor |
| Road Type | highway / urban / rural |

All 15 charts, 4 metric cards, AI context, and grievance tickets update instantly.

### Step 3 — Explore the Analytics Dashboard

| Tab | Charts |
|-----|--------|
| 📅 Temporal Trends | Monthly volume (line), hourly bar, day-of-week bar, peak-hour pie |
| ⚠️ Risk Profiling | Severity × road type, severity × traffic density, risk by cause (horizontal bar), city volume vs risk (scatter) |
| 🌦️ Environmental Factors | Weather × cause (stacked bar), visibility × weather (heatmap), temperature × severity (box), risk by lanes (bar) |
| 🗺️ Hotspot Map | Risk density heatmap (mapbox), severity scatter map, casualties by state (bar) |

### Step 4 — Chat with RoadWatch AI

The AI Assistant starts with four quick-action buttons:

| Button | What it does |
|--------|-------------|
| 📊 Accident Trends | Instant data-driven summary: peak-hour %, busiest day, peak hour |
| ⚠️ Risk Hotspots | Top 3 highest-risk cities with avg risk scores |
| 📋 Grievance Procedure | Step-by-step guide including contractor transparency info |
| 💬 Other (Ask me anything) | Opens free-text mode with hybrid query engine |

**Hybrid query engine in free-text mode:**
1. **Primary** — keyword match → answered instantly from the filtered DataFrame (no API call)
2. **Secondary** — no keyword match → routed to Google Gemini 1.5 Flash
3. **Fallback** — Gemini unavailable → rule-based DataFrame response

All AI replies render with a **typewriter streaming effect** (character-by-character).
A **← Back to Menu** button returns to the quick-action buttons without clearing history.

### Step 5 — Multi-City Grievance Filing

1. Select **multiple cities** in the sidebar.
2. Open the **AI Assistant & Grievance** tab.
3. The right-hand **Grievance Routing** panel generates a **separate ticket for every selected city**.
4. Each ticket expander shows:
   - 🏛️ Unique reference number (`RW/CIT/YYYYMMDD/NNN`)
   - 👷 Executive Engineer name, phone, and official email
   - 💰 Allocated infrastructure budget (INR)
   - 🗓️ Last road relaying date
   - 🏗️ **Assigned Contractor** (contractor transparency feature)
5. Review or edit the auto-drafted complaint letter (includes the contractor name).
6. Click **📨 Submit Report** for each city individually — every button has a unique key so there is no widget collision.

---

## Dataset Schema

The application expects exactly 24 columns:

```
accident_id, city, state, latitude, longitude, date, time, hour,
day_of_week, is_weekend, road_type, lanes, traffic_signal, weather,
visibility, temperature, traffic_density, cause, accident_severity,
vehicles_involved, casualties, is_peak_hour, festival, risk_score
```

Missing columns are detected on upload and reported with a clear `st.error()` message.

---

## Mock Infrastructure Columns

The following 6 columns are injected deterministically at load time
(not in the raw CSV). The same `city + state` input always produces the
same output across sessions.

| Column | Description |
|--------|-------------|
| `executive_engineer` | Responsible PWD official (e.g., "Er. R. K. Sharma") |
| `engineer_phone` | Contact number |
| `engineer_email` | Official email derived from state domain |
| `allocated_budget` | INR infrastructure budget (state base ± city jitter) |
| `last_relaying_date` | Date the road was last resurfaced |
| `contractor_name` | Assigned construction contractor (e.g., "M/s GR Infraprojects Ltd.") |

Determinism is achieved via `random.Random(abs(hash(seed_key)) % 2**31)` —
no `random.seed()` global state is touched, so the rest of the app is unaffected.

---

## API Key & Fallback Behaviour

| Scenario | Behaviour |
|----------|-----------|
| Valid `GEMINI_API_KEY` in secrets | Full Gemini 1.5 Flash responses, streamed character-by-character |
| Query matches dataset keywords | Answered from local DataFrame instantly (no API call regardless of key) |
| Key missing or network error | Silent catch → rule-based engine, no crash, no error shown to user |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI framework | Streamlit 1.35 |
| Data processing | Pandas 2.2, NumPy 1.26 |
| Visualisations | Plotly 5.22 (15 charts) |
| Geospatial maps | Plotly Mapbox — `carto-darkmatter` tile layer |
| AI assistant | Google Gemini 1.5 Flash (`google-generativeai 0.7`) |
| File handling | Python `zipfile` + `io` (stdlib, zero disk writes) |

---

## Hackathon Evaluation Criteria Coverage

| Criteria | Implementation |
|----------|---------------|
| Data ingestion & ZIP handling | In-memory `zipfile` + `io.BytesIO`, schema validation on upload |
| Visual analytics depth | 15 Plotly charts across temporal, risk, environmental, and geospatial dimensions |
| AI integration | Gemini 1.5 Flash with live dataset context injected into system prompt |
| Grievance automation | Multi-city tickets, unique ref numbers, auto-drafted complaint letters |
| Contractor transparency | `contractor_name` column, displayed on card and in complaint draft |
| Resilience & stability | Gemini fallback engine, session-state caching, unique widget keys, no `st.rerun()` jitter |

---

## License

MIT — free for use in the hackathon and beyond.
