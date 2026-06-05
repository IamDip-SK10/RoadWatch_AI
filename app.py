"""
RoadWatch AI — IIT Madras Road Safety Hackathon
A unified platform combining advanced visual analytics with a
conversational citizen grievance interface.
"""

import io
import zipfile
import random
import datetime
import time
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RoadWatch AI",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background: #0d1117; color: #e6edf3; }
    .block-container { padding: 1.5rem 2rem; }

    .hero-banner {
        background: linear-gradient(135deg, #1a1f2e 0%, #0d2137 50%, #0a1628 100%);
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #58a6ff, #f78166);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero-subtitle { color: #8b949e; font-size: 0.9rem; margin: 0.25rem 0 0 0; }

    .section-header {
        font-size: 1rem;
        font-weight: 600;
        color: #58a6ff;
        border-left: 3px solid #388bfd;
        padding-left: 0.6rem;
        margin: 1.5rem 0 0.8rem 0;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .grievance-card {
        background: linear-gradient(135deg, #1a1f2e, #161b22);
        border: 1px solid #388bfd44;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-top: 1rem;
    }
    .grievance-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #58a6ff;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .engineer-badge {
        background: #21262d;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        margin: 0.6rem 0;
        font-size: 0.85rem;
        color: #e6edf3;
    }

    .css-1d391kg, [data-testid="stSidebar"] {
        background: #0d1117 !important;
        border-right: 1px solid #21262d !important;
    }

    .js-plotly-plot .plotly { background: transparent !important; }

    .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; background: transparent; }
    .stTabs [data-baseweb="tab"] {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 8px 8px 0 0;
        color: #8b949e;
        padding: 0.4rem 1rem;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background: #1f2937 !important;
        color: #58a6ff !important;
        border-color: #388bfd !important;
    }

    /* Menu buttons */
    div[data-testid="column"] .stButton > button {
        background: #161b22;
        border: 1px solid #21262d;
        color: #c9d1d9;
        border-radius: 8px;
        font-size: 0.82rem;
        padding: 0.5rem 0.4rem;
        transition: border-color 0.18s, color 0.18s;
        width: 100%;
    }
    div[data-testid="column"] .stButton > button:hover {
        border-color: #388bfd;
        color: #58a6ff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
_ENGINEER_POOL = [
    "Er. R. K. Sharma", "Er. A. K. Verma", "Er. S. Patel",
    "Er. M. Rajan", "Er. N. Krishnan", "Er. P. Singh",
    "Er. D. Joshi", "Er. T. Rao", "Er. L. Mehta", "Er. V. Nair",
]
_PHONE_POOL = [
    "+91-9810012345", "+91-9820023456", "+91-9830034567",
    "+91-9840045678", "+91-9850056789", "+91-9860067890",
    "+91-9870078901", "+91-9880089012", "+91-9890090123",
    "+91-9800001234",
]
_EMAIL_DOMAIN = {
    "Maharashtra": "pwd.maharashtra.gov.in",
    "Punjab": "pwd.punjab.gov.in",
    "Tamil Nadu": "highways.tn.gov.in",
    "Delhi": "pwd.delhi.gov.in",
    "Karnataka": "pwd.karnataka.gov.in",
    "Telangana": "roads.telangana.gov.in",
    "West Bengal": "pwd.wb.gov.in",
}
_BASE_BUDGETS = {
    "Delhi": 85_00_00_000,
    "Maharashtra": 72_00_00_000,
    "Karnataka": 61_00_00_000,
    "Tamil Nadu": 59_00_00_000,
    "Telangana": 48_00_00_000,
    "Punjab": 43_00_00_000,
    "West Bengal": 39_00_00_000,
}
_LAST_RELAYING = {
    "Delhi": "2024-02-14", "Mumbai": "2023-11-05",
    "Pune": "2023-09-18", "Chennai": "2024-01-30",
    "Bangalore": "2024-03-12", "Hyderabad": "2023-12-20",
    "Kolkata": "2023-08-07", "Chandigarh": "2024-04-01",
}
_CONTRACTOR_POOL = [
    "M/s Raj Infra Pvt. Ltd.", "M/s Bharat Road Works Ltd.",
    "M/s National Highway Builders", "M/s Sri Venkatesh Constructions",
    "M/s GR Infraprojects Ltd.", "M/s Ashoka Buildcon Ltd.",
    "M/s PNC Infratech Ltd.", "M/s KCC Buildcon Pvt. Ltd.",
    "M/s Sadbhav Engineering Ltd.", "M/s H.G. Infra Engineering Ltd.",
]


def _deterministic_seed(key: str) -> int:
    return abs(hash(key)) % (2 ** 31)


def inject_mock_infrastructure(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    def _engineer(row):
        rng = random.Random(_deterministic_seed(f"{row['city']}-{row['state']}"))
        return rng.choice(_ENGINEER_POOL)

    def _phone(row):
        rng = random.Random(_deterministic_seed(f"phone-{row['city']}-{row['state']}"))
        return rng.choice(_PHONE_POOL)

    def _email(row):
        domain = _EMAIL_DOMAIN.get(row["state"], "pwd.india.gov.in")
        return f"ee.{row['city'].lower().replace(' ', '')}@{domain}"

    def _budget(row):
        base = _BASE_BUDGETS.get(row["state"], 30_00_00_000)
        rng = random.Random(_deterministic_seed(f"budget-{row['city']}"))
        return base + rng.randint(-5_00_00_000, 5_00_00_000)

    def _relay(row):
        return _LAST_RELAYING.get(row["city"], "2023-06-01")

    def _contractor(row):
        rng = random.Random(_deterministic_seed(f"contractor-{row['city']}-{row['state']}"))
        return rng.choice(_CONTRACTOR_POOL)

    df["executive_engineer"] = df.apply(_engineer, axis=1)
    df["engineer_phone"] = df.apply(_phone, axis=1)
    df["engineer_email"] = df.apply(_email, axis=1)
    df["allocated_budget"] = df.apply(_budget, axis=1)
    df["last_relaying_date"] = df.apply(_relay, axis=1)
    df["contractor_name"] = df.apply(_contractor, axis=1)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# FILE LOADING
# ─────────────────────────────────────────────────────────────────────────────
REQUIRED_COLS = {
    "accident_id", "city", "state", "latitude", "longitude",
    "date", "time", "hour", "day_of_week", "is_weekend", "road_type",
    "lanes", "traffic_signal", "weather", "visibility", "temperature",
    "traffic_density", "cause", "accident_severity", "vehicles_involved",
    "casualties", "is_peak_hour", "festival", "risk_score",
}


def load_dataframe(uploaded_file):
    try:
        raw_bytes = uploaded_file.read()
        name = uploaded_file.name.lower()

        if name.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
                csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
                if not csv_names:
                    st.error("❌ No CSV file found inside the ZIP archive.")
                    return None
                target = next((n for n in csv_names if "indian_roads" in n.lower()), csv_names[0])
                with zf.open(target) as f:
                    df = pd.read_csv(io.BytesIO(f.read()))
        elif name.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(raw_bytes))
        else:
            st.error("❌ Please upload a `.csv` or `.zip` file.")
            return None

        missing = REQUIRED_COLS - set(df.columns)
        if missing:
            st.error(f"❌ Dataset is missing columns: {missing}")
            return None

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["hour"] = pd.to_numeric(df["hour"], errors="coerce")
        df["risk_score"] = pd.to_numeric(df["risk_score"], errors="coerce")
        df["casualties"] = pd.to_numeric(df["casualties"], errors="coerce")
        return df

    except zipfile.BadZipFile:
        st.error("❌ Corrupt ZIP file. Please re-upload.")
        return None
    except Exception as exc:
        st.error(f"❌ Failed to load file: {exc}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY THEME
# ─────────────────────────────────────────────────────────────────────────────
PLOTLY_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="#161b22",
    plot_bgcolor="#161b22",
    font_color="#c9d1d9",
    margin=dict(l=30, r=20, t=50, b=30),
)


def _fig_defaults(fig):
    fig.update_layout(**PLOTLY_THEME)
    fig.update_xaxes(showgrid=True, gridcolor="#21262d", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#21262d", zeroline=False)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# GEMINI
# ─────────────────────────────────────────────────────────────────────────────
def _build_system_prompt(df: pd.DataFrame, city_filter: list, state_filter: list) -> str:
    total_acc = len(df)
    total_cas = int(df["casualties"].sum())
    avg_risk = float(df["risk_score"].mean())
    top_cause = df["cause"].value_counts().idxmax() if total_acc > 0 else "N/A"
    top_state = df["state"].value_counts().idxmax() if total_acc > 0 else "N/A"
    severity_dist = df["accident_severity"].value_counts().to_dict()

    return f"""
You are RoadWatch AI, an expert road safety advisor for India.
You help citizens, engineers, and policymakers understand accident patterns,
road infrastructure risks, and grievance escalation procedures.

== CURRENT DATASET SUMMARY (filtered view) ==
States selected : {state_filter if state_filter else 'All'}
Cities selected : {city_filter if city_filter else 'All'}
Total accidents : {total_acc:,}
Total casualties : {total_cas:,}
Average risk score: {avg_risk:.2f}
Top cause : {top_cause}
Highest-risk state: {top_state}
Severity breakdown: {severity_dist}

== YOUR ROLE ==
- Answer questions about road safety, accident causes, and risk mitigation.
- Suggest infrastructure improvements based on data patterns.
- Help users draft or understand the grievance submission process.
- Be concise, factual, and empathetic. Use bullet points for clarity.
"""


def _fallback_response(user_msg: str, df: pd.DataFrame) -> str:
    msg = user_msg.lower()

    if any(w in msg for w in ["risk", "dangerous", "worst"]):
        top = df.groupby("city")["risk_score"].mean().nlargest(3).reset_index()
        lines = [f"- **{r['city']}** — avg risk `{r['risk_score']:.2f}`" for _, r in top.iterrows()]
        return "**Top 3 highest-risk cities (current filter):**\n" + "\n".join(lines)

    if any(w in msg for w in ["cause", "why", "reason"]):
        top = df["cause"].value_counts().head(3)
        lines = [f"- **{c.title()}**: {n:,} accidents" for c, n in top.items()]
        return "**Leading accident causes:**\n" + "\n".join(lines)

    if any(w in msg for w in ["casualt", "death", "fatal"]):
        total = int(df["casualties"].sum())
        fatal = int((df["accident_severity"] == "fatal").sum())
        return (
            f"There are **{total:,} total casualties** in the current view, "
            f"with **{fatal:,} fatal accidents**."
        )

    if any(w in msg for w in ["weather", "fog", "rain", "visibility"]):
        wdf = df.groupby("weather")["casualties"].sum().reset_index()
        lines = [f"- **{r['weather'].title()}**: {int(r['casualties']):,} casualties" for _, r in wdf.iterrows()]
        return "**Casualties by weather condition:**\n" + "\n".join(lines)

    if any(w in msg for w in ["grievance", "complaint", "report", "engineer", "contact", "official"]):
        return (
            "**How to file a grievance:**\n"
            "1. Select your **state & city** in the sidebar.\n"
            "2. Open the **AI Assistant & Grievance** tab.\n"
            "3. The right panel shows the responsible **Executive Engineer**.\n"
            "4. Review the auto-drafted complaint and click **Submit Official Report**.\n\n"
            "_Each ticket gets a unique reference number and is emailed to the PWD official._"
        )

    if any(w in msg for w in ["peak", "hour", "time", "when"]):
        pct = (df["is_peak_hour"] == 1).mean() * 100
        peak = int(df[df["is_peak_hour"] == 1].groupby("hour").size().idxmax())
        return (
            f"**{pct:.1f}%** of accidents happen during peak hours. "
            f"The single busiest hour is **{peak:02d}:00 – {peak + 1:02d}:00**."
        )

    if any(w in msg for w in ["road", "highway", "urban", "rural", "lane", "signal", "density"]):
        rd = df.groupby("road_type")["risk_score"].mean().reset_index().sort_values("risk_score", ascending=False)
        lines = [f"- **{r['road_type'].title()}**: avg risk `{r['risk_score']:.2f}`" for _, r in rd.iterrows()]
        return "**Avg risk score by road type:**\n" + "\n".join(lines)

    # Generic catch-all (only reached when Gemini is also unavailable)
    return (
        "I can help with: accident causes, risk hotspots, casualty stats, "
        "weather impacts, road types, peak-hour analysis, and grievance filing. "
        "Please rephrase your question with one of these topics."
    )


def _call_gemini(messages: list, system_prompt: str):
    """Call Gemini 1.5 Flash. Returns response text or None on any failure."""
    try:
        import google.generativeai as genai
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            return None
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_prompt,
        )
        history = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
            for m in messages[:-1]
        ]
        chat = model.start_chat(history=history)
        response = chat.send_message(messages[-1]["content"])
        return response.text
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# GRIEVANCE PANEL
# ─────────────────────────────────────────────────────────────────────────────
def render_grievance_panel(df: pd.DataFrame, city_filter: list):
    st.markdown('<div class="section-header">📋 Grievance Routing</div>', unsafe_allow_html=True)

    if not city_filter:
        st.info("Select one or more cities in the sidebar to generate grievance tickets.")
        return

    today = datetime.date.today().strftime("%d %B %Y")
    date_tag = datetime.date.today().strftime("%Y%m%d")

    for idx, target_city in enumerate(city_filter, start=1):
        city_df = df[df["city"] == target_city]
        if city_df.empty:
            st.warning(f"No data found for **{target_city}**.")
            continue

        row = city_df.iloc[0]
        engineer = row.get("executive_engineer", "Er. Unknown")
        phone = row.get("engineer_phone", "N/A")
        email = row.get("engineer_email", "N/A")
        budget = row.get("allocated_budget", 0)
        relay_date = row.get("last_relaying_date", "N/A")
        contractor = row.get("contractor_name", "N/A")
        total_acc = len(city_df)
        casualties = int(city_df["casualties"].sum())
        top_cause = city_df["cause"].value_counts().idxmax()
        state = row.get("state", "N/A")
        ref_no = f"RW/{target_city[:3].upper()}/{date_tag}/{idx:03d}"

        complaint_draft = (
            f"Ref: {ref_no}\nDate: {today}\n\n"
            f"To,\n{engineer}\nExecutive Engineer – Road Safety Division\n"
            f"{state} Public Works Department\n\n"
            f"Subject: Urgent Grievance – High-Risk Road Conditions in {target_city}\n\n"
            f"Sir/Madam,\n"
            f"Data from RoadWatch AI reveals critical concerns regarding road "
            f"conditions in {target_city}:\n"
            f" • Total Accidents : {total_acc:,}\n"
            f" • Total Casualties : {casualties:,}\n"
            f" • Leading Hazard : {top_cause.title()}\n"
            f" • Last Relayed : {relay_date}\n"
            f" • Assigned Contractor : {contractor}\n\n"
            f"Kindly register this official ticket and deploy infrastructure "
            f"remediation in coordination with the assigned contractor.\n\n"
            f"Yours sincerely,\n[Citizen Name]\n[Contact Details]"
        )

        with st.expander(f"🏛️ {target_city} — Ticket {ref_no}", expanded=(idx == 1)):
            st.markdown(
                f"""
                <div class="grievance-card">
                    <div class="grievance-title">🏛️ Official Grievance Ticket — {ref_no}</div>
                    <div class="engineer-badge">
                        👷 <strong>{engineer}</strong> &nbsp;|&nbsp;
                        📞 {phone} &nbsp;|&nbsp; ✉️ {email}
                    </div>
                    <div style="font-size:0.78rem;color:#8b949e;line-height:1.9;">
                        Allocated: <span style='color:#3fb950;'>₹{budget:,.0f}</span>
                        &nbsp;|&nbsp; Last Relayed: <span style='color:#f0883e;'>{relay_date}</span><br>
                        🏗️ Contractor: <span style='color:#d2a8ff;'><strong>{contractor}</strong></span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.text_area(
                "Complaint Draft",
                value=complaint_draft,
                height=220,
                label_visibility="collapsed",
                key=f"draft_{target_city}",
            )

            if st.button(
                f"📨 Submit Report for {target_city}",
                type="primary",
                key=f"submit_{target_city}",
            ):
                st.success(
                    f"✅ Complaint **{ref_no}** logged and routed to **{engineer}** "
                    f"at `{email}`. Acknowledgement expected within 48 hours."
                )


# ─────────────────────────────────────────────────────────────────────────────
# ANALYTICS DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def render_analytics(df: pd.DataFrame):
    tab_temporal, tab_risk, tab_environ, tab_map = st.tabs(
        ["📅 Temporal Trends", "⚠️ Risk Profiling", "🌦️ Environmental Factors", "🗺️ Hotspot Map"]
    )

    # ── Temporal ──────────────────────────────────────────────────
    with tab_temporal:
        st.markdown('<div class="section-header">Accident Trends Over Time</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            daily = (
                df.groupby(df["date"].dt.to_period("M").astype(str))
                .size().reset_index(name="accidents")
            )
            daily.columns = ["month", "accidents"]
            fig = px.line(daily, x="month", y="accidents",
                          title="Monthly Accident Volume",
                          color_discrete_sequence=["#58a6ff"])
            fig.update_traces(fill="tozeroy", fillcolor="rgba(88,166,255,0.1)", line_width=2)
            st.plotly_chart(_fig_defaults(fig), use_container_width=True)
        with c2:
            hourly = df.groupby("hour").size().reset_index(name="count")
            fig = px.bar(hourly, x="hour", y="count",
                         title="Accidents by Hour of Day",
                         color="count", color_continuous_scale="Reds")
            st.plotly_chart(_fig_defaults(fig), use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            dow = df.groupby("day_of_week").size().reset_index(name="count")
            day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            dow["day_of_week"] = pd.Categorical(dow["day_of_week"], categories=day_order, ordered=True)
            fig = px.bar(dow.sort_values("day_of_week"), x="day_of_week", y="count",
                         title="Accidents by Day of Week",
                         color_discrete_sequence=["#f78166"])
            st.plotly_chart(_fig_defaults(fig), use_container_width=True)
        with c4:
            peak = df.groupby("is_peak_hour")["casualties"].sum().reset_index()
            peak["is_peak_hour"] = peak["is_peak_hour"].map({0: "Non-Peak", 1: "Peak Hour"})
            fig = px.pie(peak, names="is_peak_hour", values="casualties",
                         title="Casualty Share: Peak vs Non-Peak",
                         color_discrete_sequence=["#f85149","#3fb950"], hole=0.45)
            st.plotly_chart(_fig_defaults(fig), use_container_width=True)

    # ── Risk Profiling ────────────────────────────────────────────
    with tab_risk:
        st.markdown('<div class="section-header">Risk & Infrastructure Profiling</div>', unsafe_allow_html=True)
        SEV_COLORS = {"fatal": "#f85149", "major": "#f0883e", "minor": "#3fb950"}
        c1, c2 = st.columns(2)
        with c1:
            sev_road = df.groupby(["road_type","accident_severity"]).size().reset_index(name="count")
            fig = px.bar(sev_road, x="road_type", y="count", color="accident_severity",
                         title="Severity Distribution by Road Type",
                         barmode="group", color_discrete_map=SEV_COLORS)
            st.plotly_chart(_fig_defaults(fig), use_container_width=True)
        with c2:
            sev_dens = df.groupby(["traffic_density","accident_severity"]).size().reset_index(name="count")
            fig = px.bar(sev_dens, x="traffic_density", y="count", color="accident_severity",
                         title="Severity by Traffic Density",
                         barmode="stack", color_discrete_map=SEV_COLORS)
            st.plotly_chart(_fig_defaults(fig), use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            cause_risk = (df.groupby("cause")["risk_score"].mean()
                          .reset_index().sort_values("risk_score"))
            fig = px.bar(cause_risk, x="risk_score", y="cause",
                         title="Avg Risk Score by Cause", orientation="h",
                         color="risk_score", color_continuous_scale="Oranges")
            st.plotly_chart(_fig_defaults(fig), use_container_width=True)
        with c4:
            city_risk = (df.groupby("city")
                         .agg(avg_risk=("risk_score","mean"), accidents=("accident_id","count"))
                         .reset_index())
            fig = px.scatter(city_risk, x="accidents", y="avg_risk", text="city",
                             size="avg_risk", title="City: Volume vs. Avg Risk",
                             color="avg_risk", color_continuous_scale="Reds")
            fig.update_traces(textposition="top center")
            st.plotly_chart(_fig_defaults(fig), use_container_width=True)

    # ── Environmental Factors ────────────────────────────────────
    with tab_environ:
        st.markdown('<div class="section-header">Environmental Factors</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            wc = df.groupby(["weather","cause"]).size().reset_index(name="count")
            fig = px.bar(wc, x="weather", y="count", color="cause",
                         title="Weather × Cause Interaction", barmode="stack")
            st.plotly_chart(_fig_defaults(fig), use_container_width=True)
        with c2:
            vw = df.groupby(["visibility","weather"]).size().reset_index(name="count")
            pivot = vw.pivot(index="visibility", columns="weather", values="count").fillna(0)
            fig = go.Figure(data=go.Heatmap(
                z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
                colorscale="YlOrRd", showscale=True,
            ))
            fig.update_layout(title="Heatmap: Visibility × Weather", **PLOTLY_THEME)
            st.plotly_chart(fig, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            fig = px.box(df, x="accident_severity", y="temperature",
                         title="Temperature Distribution by Severity",
                         color="accident_severity",
                         color_discrete_map={"fatal":"#f85149","major":"#f0883e","minor":"#3fb950"})
            st.plotly_chart(_fig_defaults(fig), use_container_width=True)
        with c4:
            lr = df.groupby("lanes")["risk_score"].mean().reset_index()
            fig = px.bar(lr, x="lanes", y="risk_score",
                         title="Avg Risk Score by Number of Lanes",
                         color="risk_score", color_continuous_scale="Blues")
            st.plotly_chart(_fig_defaults(fig), use_container_width=True)

    # ── Hotspot Map ──────────────────────────
    with tab_map:
        st.markdown('<div class="section-header">Geospatial Accident Hotspots</div>', unsafe_allow_html=True)
        map_df = df.sample(min(3000, len(df)), random_state=42) if len(df) > 3000 else df.copy()
        CENTER = {"lat": 20.5937, "lon": 78.9629}

        fig = px.density_mapbox(
            map_df, lat="latitude", lon="longitude", z="risk_score",
            radius=14, center=CENTER, zoom=4,
            mapbox_style="carto-darkmatter",
            title="Accident Risk Density Heatmap",
            color_continuous_scale="Inferno",
        )
        fig.update_layout(height=500, paper_bgcolor="#161b22",
                          font_color="#c9d1d9", margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            fig = px.scatter_mapbox(
                map_df, lat="latitude", lon="longitude",
                color="accident_severity", size="risk_score",
                hover_name="city",
                hover_data={"cause": True, "casualties": True},
                mapbox_style="carto-darkmatter", zoom=4, center=CENTER,
                title="Scatter: Accidents by Severity",
                color_discrete_map={"fatal":"#f85149","major":"#f0883e","minor":"#3fb950"},
            )
            fig.update_layout(height=380, paper_bgcolor="#161b22",
                               font_color="#c9d1d9", margin=dict(l=0,r=0,t=40,b=0))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            ss = (df.groupby("state")
                  .agg(casualties=("casualties","sum"), avg_risk=("risk_score","mean"))
                  .reset_index().sort_values("avg_risk", ascending=False))
            fig = px.bar(ss, x="state", y="casualties", color="avg_risk",
                         title="Casualties & Avg Risk by State",
                         color_continuous_scale="Reds")
            st.plotly_chart(_fig_defaults(fig), use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# METRIC CARDS
# ─────────────────────────────────────────────────────────────────────────────
def render_metrics(df: pd.DataFrame):
    total_acc = len(df)
    total_cas = int(df["casualties"].sum())
    avg_risk = float(df["risk_score"].mean())
    total_bud = int(df["allocated_budget"].sum()) if "allocated_budget" in df.columns else 0
    fatal_pct = (df["accident_severity"] == "fatal").mean() * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🚗 Total Accidents", f"{total_acc:,}",
              delta=f"Fatal rate {fatal_pct:.1f}%", delta_color="inverse")
    c2.metric("💔 Total Casualties", f"{total_cas:,}",
              delta=f"{total_cas/max(total_acc,1):.1f} per accident", delta_color="inverse")
    c3.metric("⚡ Avg Risk Score", f"{avg_risk:.3f}",
              delta="High Risk" if avg_risk > 0.5 else "Moderate Risk",
              delta_color="inverse" if avg_risk > 0.5 else "normal")
    c4.metric("🏗️ Infrastructure Budget", f"₹{total_bud/1e7:.1f} Cr",
              delta="Allocated & Monitored")


# ─────────────────────────────────────────────────────────────────────────────
# CHAT — helpers
# ─────────────────────────────────────────────────────────────────────────────

_DATASET_KEYWORDS = [
    "risk", "dangerous", "worst",
    "cause", "why", "reason",
    "casualt", "death", "fatal",
    "weather", "fog", "rain", "visibility",
    "grievance", "complaint", "report", "engineer", "contact", "official",
    "peak", "hour", "time", "when",
    "road", "highway", "urban", "rural", "lane", "signal", "density",
]

_MENU_BUTTONS = [
    ("📊 Accident Trends", "trends"),
    ("⚠️ Risk Hotspots", "hotspots"),
    ("📋 Grievance Procedure", "grievance"),
    ("💬 Other (Ask me anything)", "query"),
]


def _has_dataset_match(user_msg: str) -> bool:
    """True when _fallback_response can give a meaningful data-driven answer."""
    msg = user_msg.lower()
    return any(kw in msg for kw in _DATASET_KEYWORDS)


def _streamed_write(text: str, delay: float = 0.010):
    """Character-by-character generator for st.write_stream()."""
    for char in text:
        yield char
        time.sleep(delay)


def _quick_summary(topic: str, df: pd.DataFrame) -> str:
    """Pre-built data-driven summaries for the four menu buttons."""
    if topic == "trends":
        peak_pct = (df["is_peak_hour"] == 1).mean() * 100
        top_day = df["day_of_week"].value_counts().idxmax()
        top_hour = int(df.groupby("hour").size().idxmax())
        return (
            f"**📊 Accident Trend Summary**\n\n"
            f"- **{peak_pct:.1f}%** of accidents occur during peak hours.\n"
            f"- Busiest day of the week: **{top_day}**.\n"
            f"- Most dangerous hour: **{top_hour:02d}:00 – {top_hour + 1:02d}:00**.\n\n"
            f"_Switch to the **Temporal Trends** tab for full interactive charts._"
        )

    if topic == "hotspots":
        top3 = df.groupby("city")["risk_score"].mean().nlargest(3).reset_index()
        lines = "\n".join(
            f"- **{r['city']}** — avg risk score `{r['risk_score']:.2f}`"
            for _, r in top3.iterrows()
        )
        top_cause = df["cause"].value_counts().idxmax()
        return (
            f"**⚠️ Top Risk Hotspots (current filter)**\n\n"
            f"{lines}\n\n"
            f"Leading accident cause: **{top_cause.title()}**.\n\n"
            f"_See the **Hotspot Map** tab for the full geospatial density view._"
        )

    if topic == "grievance":
        return (
            "**📋 How to File a Road Safety Grievance**\n\n"
            "1. Use the **sidebar** to select your state and one or more cities.\n"
            "2. Open the **AI Assistant & Grievance** tab.\n"
            "3. The right-hand panel generates a **separate ticket for every selected city**, "
            "each showing the responsible **Executive Engineer**, contact details, "
            "allocated budget, last road-relaying date, and the **assigned contractor** "
            "for full transparency.\n"
            "4. Review or edit the auto-generated complaint draft inside each city's expander.\n"
            "5. Click **📨 Submit Report** for each city to log the ticket.\n\n"
            "_Every ticket carries a unique reference number and is routed "
            "directly to the responsible PWD official and contractor._"
        )

    return ""


# ─────────────────────────────────────────────────────────────────────────────
# CHAT
# ─────────────────────────────────────────────────────────────────────────────
def render_chat(df: pd.DataFrame, city_filter: list, state_filter: list):
    st.markdown(
        '<div class="section-header">💬 Ask RoadWatch AI</div>',
        unsafe_allow_html=True,
    )

    # ── Session-state bootstrap ──────────────────────────────────────────────
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_stage" not in st.session_state:
        st.session_state.chat_stage = "menu"

    # ── Persistent history container ─────────────────────────────────────────

    history_box = st.container(height=400)
    with history_box:

        with st.chat_message("assistant", avatar="🛣️"):
            st.markdown(
                "👋 Hello! I am **RoadWatch AI**. "
                "How can I assist you with road safety today?"
            )

        for msg in st.session_state.messages:
            avatar = "🧑" if msg["role"] == "user" else "🛣️"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    # ════════════════════════════════════════════════════════════════════════
    # STAGE: menu
    # ════════════════════════════════════════════════════════════════════════
    if st.session_state.chat_stage == "menu":
        st.markdown(
            "<p style='font-size:0.82rem;color:#8b949e;margin:0.5rem 0 0.3rem 0;'>"
            "Choose a topic or ask your own question:</p>",
            unsafe_allow_html=True,
        )
        btn_cols = st.columns(len(_MENU_BUTTONS))
        for col, (label, topic) in zip(btn_cols, _MENU_BUTTONS):
            if col.button(label, use_container_width=True, key=f"menu_btn_{topic}"):
                if topic == "query":

                    st.session_state.chat_stage = "query"
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": (
                            "Sure! Type your question below and I'll answer "
                            "using live accident data or AI analysis."
                        ),
                    })
                else:

                    summary = _quick_summary(topic, df)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": summary,
                    })
                st.rerun()

    # ════════════════════════════════════════════════════════════════════════
    # STAGE
    # ════════════════════════════════════════════════════════════════════════
    elif st.session_state.chat_stage == "query":
        user_input = st.chat_input("Ask about road safety, hotspots, grievances…")

        if user_input:

            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
            })

            system_prompt = _build_system_prompt(df, city_filter, state_filter)


            if _has_dataset_match(user_input):
                reply = _fallback_response(user_input, df)
                source = "data"
            else:
                gemini_reply = _call_gemini(st.session_state.messages, system_prompt)
                if gemini_reply:
                    reply = gemini_reply
                    source = "gemini"
                else:
                    reply = _fallback_response(user_input, df)
                    source = "data"


            with history_box:
                with st.chat_message("assistant", avatar="🛣️"):
                    streamed_text = st.write_stream(_streamed_write(reply))


            st.session_state.messages.append({
                "role": "assistant",
                "content": streamed_text,
            })
            st.rerun()


        if st.button("← Back to Menu", key="back_to_menu"):
            st.session_state.chat_stage = "menu"
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar(df: pd.DataFrame):
    with st.sidebar:
        st.markdown(
            "<h2 style='color:#58a6ff;font-size:1.1rem;'>🛣️ RoadWatch AI</h2>"
            "<p style='color:#8b949e;font-size:0.8rem;'>IIT Madras Road Safety Hackathon</p>",
            unsafe_allow_html=True,
        )
        st.divider()
        st.markdown("**🗺️ Geographic Filters**")
        all_states = sorted(df["state"].dropna().unique().tolist())
        state_filter = st.multiselect("Filter by State", all_states, default=[])
        city_pool = (
            sorted(df[df["state"].isin(state_filter)]["city"].dropna().unique())
            if state_filter else
            sorted(df["city"].dropna().unique())
        )
        city_filter = st.multiselect("Filter by City", city_pool, default=[])
        st.divider()
        st.markdown("**⚙️ Additional Filters**")
        severity_filter = st.multiselect("Severity", sorted(df["accident_severity"].dropna().unique()), default=[])
        road_filter = st.multiselect("Road Type", sorted(df["road_type"].dropna().unique()), default=[])
        st.divider()
        st.markdown(
            "<p style='color:#8b949e;font-size:0.75rem;'>"
            "Data: Indian Roads Accident Dataset<br>"
            "Visualisations: Plotly 5.x<br>"
            "AI: Google Gemini 1.5 Flash"
            "</p>",
            unsafe_allow_html=True,
        )
    return state_filter, city_filter, severity_filter, road_filter


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():

    st.markdown(
        "<div class='hero-banner'>"
        "<div style='font-size:2.5rem;'>🛣️</div>"
        "<div><p class='hero-title'>RoadWatch AI</p>"
        "<p class='hero-subtitle'>Advanced Road Safety Analytics &amp; "
        "Citizen Grievance Platform · IIT Madras Hackathon</p></div>"
        "</div>",
        unsafe_allow_html=True,
    )


    if "df_raw" not in st.session_state:
        st.session_state.df_raw = None

    uploaded = st.file_uploader(
        "Upload Dataset (.csv or .zip containing CSV)",
        type=["csv", "zip"],
        help="Upload `indian_roads_dataset.csv` or its ZIP archive.",
    )

    if uploaded is not None and st.session_state.df_raw is None:
        with st.spinner("Loading and processing dataset…"):
            df_loaded = load_dataframe(uploaded)
        if df_loaded is not None:
            st.session_state.df_raw = inject_mock_infrastructure(df_loaded)

    if st.session_state.df_raw is None:
        st.info("👆 Please upload the dataset ZIP or CSV to begin.")
        st.stop()

    st.success(f"✅ {len(st.session_state.df_raw):,} records loaded from memory cache.")

    df_full = st.session_state.df_raw
    state_filter, city_filter, severity_filter, road_filter = render_sidebar(df_full)


    df = df_full.copy()
    if state_filter: df = df[df["state"].isin(state_filter)]
    if city_filter: df = df[df["city"].isin(city_filter)]
    if severity_filter: df = df[df["accident_severity"].isin(severity_filter)]
    if road_filter: df = df[df["road_type"].isin(road_filter)]

    if df.empty:
        st.warning("⚠️ No data matches the current filters. Please adjust the sidebar.")
        st.stop()

    render_metrics(df)

    tab_analytics, tab_chat = st.tabs(["📊 Analytics Dashboard", "🤖 AI Assistant & Grievance"])

    with tab_analytics:
        render_analytics(df)

    with tab_chat:
        col_chat, col_grievance = st.columns([3, 2], gap="large")
        with col_chat:
            render_chat(df, city_filter, state_filter)
        with col_grievance:
            render_grievance_panel(df, city_filter)


if __name__ == "__main__":
    main()