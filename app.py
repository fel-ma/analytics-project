"""
app.py
======
Main entry point for the Monkey Baa AI Reporting System.
Run with:  streamlit run app.py

This file handles:
- Page configuration
- Sidebar (API key, model, file upload)
- Stores shared state (df, client) in st.session_state
- Navigation is handled automatically by Streamlit's multipage system (pages/ folder)
"""

import streamlit as st
from utils.data_loader import load_and_clean

# ─────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Monkey Baa — AI Reporting System",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stDownloadButton > button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# Sidebar — shared across all pages
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🎭 Monkey Baa")
    st.caption("AI Reporting System")
    st.divider()

    st.subheader("⚙️ Configuration")
    api_key = st.text_input(
        "OpenAI API key", type="password", placeholder="sk-...",
        help="Your key is never stored — it lives only in this session."
    )
    model = st.selectbox("Model", ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])

    st.divider()
    st.subheader("📂 Data")
    uploaded = st.file_uploader("Upload Excel file (.xlsx)", type=["xlsx"])

    if uploaded:
        df = load_and_clean(uploaded.read())
        st.session_state["df"]      = df
        st.session_state["api_key"] = api_key
        st.session_state["model"]   = model

        completed = df[df["Status"] == "Completed"]
        st.success(f"✅ {len(df):,} records loaded")
        st.caption(f"{len(completed)} completed · {(df['Status']=='Planned').sum()} planned")
    else:
        st.info("Upload the Dashboard Excel file to begin.")

    st.divider()
    st.caption("Select a report from the navigation above ↑")

# ─────────────────────────────────────────────────────────
# Home screen (shown when no page is selected)
# ─────────────────────────────────────────────────────────
st.title("🎭 Monkey Baa — AI Reporting System")
st.caption("Select a report from the sidebar navigation to get started.")

st.markdown("""
### Available Reports

| # | Report | What it covers |
|---|--------|----------------|
| 1 | **Access & Audience Reach** | Attendance, goal achievement, geographic reach |
| 2 | **High Quality Outcomes** | Performance quality metrics and year-on-year growth |
| 3 | **Emotional & Social Impact** | Audience emotional response and community outcomes |
| 4 | **Arts & Cultural Impact** | Cultural value, artistic reach, sector contribution |
| 5 | **Executive Overview** | Full program summary for leadership |
| 6 | **Impact Report — Sponsors** | ROI and outcomes tailored for funders and sponsors |

---

### How to use
1. Enter your **OpenAI API key** in the sidebar
2. **Upload the Monkey Baa Dashboard Excel file**
3. Navigate to any report using the menu above
4. Click **Run AI Analysis** inside the report

---

### Dataset at a glance
- **183 records** — 50 completed · 132 planned · 1 cancelled
- **8 states** — NSW leads (64 stops), followed by VIC (52)
- **Total completed audience** ≈ 192,000 attendees
- **Date range**: 2021 – 2025
""")
