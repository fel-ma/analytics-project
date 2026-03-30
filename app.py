"""
app.py
======
Main entry point for the Monkey Baa AI Reporting System.
Run with:  PYTHONPATH=$(pwd) streamlit run app.py

Handles:
- Sidebar: API key, model, CSV upload (shared across ALL pages)
- Stores df, api_key, model in st.session_state so pages don't re-upload
"""

import io
import pandas as pd
import streamlit as st

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
# Shared data loader (CSV — with comma fix)
# ─────────────────────────────────────────────────────────
@st.cache_data
def load_audience_csv(file_bytes: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    # Fix: remove commas from numbers like "3,213.00"
    df["Audience_n"] = pd.to_numeric(
        df["Audience"].astype(str).str.strip().str.replace(",", "", regex=False),
        errors="coerce",
    )
    df["Year"]        = pd.to_numeric(df["Year"], errors="coerce")
    df["Regional II"] = df["Regional II"].fillna("Unknown").str.strip()
    return df


# ─────────────────────────────────────────────────────────
# Sidebar — shared across ALL pages
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎭 Monkey Baa")
    st.caption("AI Reporting System")
    st.divider()

    st.markdown("#### ⚙️ Configuration")
    api_key = st.text_input(
        "OpenAI API key", type="password", placeholder="sk-...",
        help="Your key is never stored — only lives in this session.",
    )
    model = st.selectbox("Model", ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])

    if api_key:
        st.session_state["api_key"] = api_key
    if model:
        st.session_state["model"] = model

    st.divider()
    st.markdown("#### 📂 Data — upload once")

    uploaded = st.file_uploader(
        "Audience_final_data.csv",
        type=["csv"],
        help="Upload once — available on all report pages automatically.",
    )

    if uploaded:
        df = load_audience_csv(uploaded.read())
        st.session_state["df_audience"] = df
        total = int(df["Audience_n"].sum())
        st.success(f"✅ {len(df):,} records loaded")
        st.caption(f"Total audience: {total:,} · Years: 2021–2025")
    elif "df_audience" in st.session_state:
        st.success("✅ Audience data loaded")
        st.caption("Navigate to any report ↑")
    else:
        st.info("Upload the Audience CSV to enable all reports.")

    st.markdown("#### 📂 Survey data")
    uploaded2 = st.file_uploader(
        "Survey CSV or Excel",
        type=["csv", "xlsx"],
        help="Upload the survey dataset — available on all pages automatically.",
        key="survey_upload",
    )

    if uploaded2:
        raw = uploaded2.read()
        if uploaded2.name.endswith(".xlsx"):
            import io as _io
            df2 = pd.read_excel(_io.BytesIO(raw))
        else:
            import io as _io
            df2 = pd.read_csv(_io.BytesIO(raw), encoding="utf-8-sig")
        df2.columns = df2.columns.str.strip()
        st.session_state["df_survey"] = df2
        st.success(f"✅ Survey: {len(df2):,} rows loaded")
        st.caption(f"Columns: {', '.join(df2.columns[:4].tolist())}…")
    elif "df_survey" in st.session_state:
        st.success("✅ Survey data loaded")
    else:
        st.info("Upload the survey file when ready.")

    st.divider()
    st.caption("Select a report from the navigation above ↑")


# ─────────────────────────────────────────────────────────
# Home screen
# ─────────────────────────────────────────────────────────
st.title("🎭 Monkey Baa — AI Reporting System")
st.caption("Upload the CSV once in the sidebar, then navigate to any report.")

st.markdown("""
### Available Reports

| # | Report | What it covers |
|---|--------|----------------|
| 2 | **Access & Audience Reach** | Total audience, geographic reach, Metro vs Regional vs Remote |
| 3 | **High Quality Outcomes** | Year-on-year growth, event quality, performance trends |
| 4 | **Emotional & Social Impact** | Community outcomes, equity, social value |
| 5 | **Arts & Cultural Impact** | Cultural reach, sector contribution, artistic footprint |
| 6 | **Executive Overview** | Full program summary for leadership and board |
| 7 | **Impact Report — Sponsors** | ROI and outcomes tailored for funders and sponsors |

---

### How to use
1. Enter your **OpenAI API key** in the sidebar
2. Upload **Audience_final_data.csv** once — stays loaded across all pages
3. Navigate to any report using the menu above
4. Click **Generate AI Insights** inside the report

---

### Dataset at a glance
- **603 records** across 2021–2025
- **8 states** — NSW leads, followed by VIC and QLD
- **Total audience: 351,772**
- **Event types**: Workshop, On-Tour, Self-presented, Co-Presented, Placemaking
""")