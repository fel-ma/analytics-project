"""
app.py
======
Main entry point for the Monkey Baa AI Reporting System.
Run with:  PYTHONPATH=$(pwd) streamlit run app.py

Handles:
- Login authentication
- Sidebar: API key input, model selector, CSV upload (shared across ALL pages)
- Stores df, api_key, model in st.session_state so pages don't re-upload
"""

import io
import pandas as pd
import streamlit as st

# ─────────────────────────────────────────────────────────
# Login credentials — change as needed
# ─────────────────────────────────────────────────────────
VALID_USERS = {
    "admin":   "monkeybaa2025",
    "analyst": "report2025",
}

# ─────────────────────────────────────────────────────────
# Design tokens — same as report pages
# ─────────────────────────────────────────────────────────
ORANGE      = "#E8673A"
ORANGE_DARK = "#C4512A"
BEIGE       = "#F5F0EA"
WHITE       = "#FFFFFF"
GRAY_TEXT   = "#555555"
TEAL_DARK   = "#2F6F73"

# ─────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Monkey Baa — AI Reporting System",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────
# Global CSS
# ─────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  .stApp {{ background-color: {BEIGE}; }}

  [data-testid="stSidebar"] {{
    background-color: {TEAL_DARK} !important;
  }}
  [data-testid="stSidebar"] * {{
    color: #ffffff !important;
  }}
  [data-testid="stSidebar"] .stSuccess,
  [data-testid="stSidebar"] .stInfo,
  [data-testid="stSidebar"] .stCaption {{
    color: #d0eaeb !important;
  }}
  [data-testid="stSidebar"] hr {{
    border-color: rgba(255,255,255,0.2) !important;
  }}
  [data-testid="stSidebar"] .stButton > button {{
    background-color: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    color: white !important;
    border-radius: 8px;
  }}

  .card {{
    background-color: {WHITE};
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 14px;
  }}

  .report-row {{
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 12px 0;
    border-bottom: 1px solid #ede5dc;
  }}
  .report-row:last-child {{ border-bottom: none; }}
  .report-num {{
    background-color: {ORANGE};
    color: white;
    border-radius: 8px;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 700;
    flex-shrink: 0;
    margin-top: 2px;
  }}
  .report-title {{
    font-size: 13px;
    font-weight: 700;
    color: #222;
    margin-bottom: 2px;
  }}
  .report-desc {{
    font-size: 12px;
    color: {GRAY_TEXT};
    line-height: 1.5;
  }}

  .step-row {{
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 12px;
  }}
  .step-num {{
    background-color: {ORANGE};
    color: white;
    border-radius: 50%;
    width: 26px;
    height: 26px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 700;
    flex-shrink: 0;
    margin-top: 1px;
  }}
  .step-text {{
    font-size: 13px;
    color: {GRAY_TEXT};
    line-height: 1.6;
    padding-top: 3px;
  }}
  .step-text b {{ color: #222; }}

  .section-label {{
    font-size: 11px;
    font-weight: 600;
    color: {ORANGE};
    text-transform: uppercase;
    letter-spacing: 0.7px;
    margin-bottom: 4px;
  }}
  .section-heading {{
    font-size: 16px;
    font-weight: 700;
    color: #222;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 2px solid {ORANGE};
    display: inline-block;
  }}

  .page-header {{ padding: 4px 0 12px 0; }}
  .page-eyebrow {{
    font-size: 11px;
    color: #999;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 4px;
  }}
  .page-title {{
    font-size: 26px;
    font-weight: 700;
    color: #222;
    line-height: 1.2;
  }}

  hr.div {{
    border: none;
    border-top: 1px solid #e0d8d0;
    margin: 6px 0 16px 0;
  }}

  .login-wrap {{
    max-width: 380px;
    margin: 80px auto 0;
  }}
  .login-title {{
    font-size: 22px;
    font-weight: 700;
    color: #222;
    margin-bottom: 4px;
  }}
  .login-sub {{
    font-size: 13px;
    color: {GRAY_TEXT};
    margin-bottom: 24px;
  }}

  .stDownloadButton > button {{ width: 100%; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# Shared data loader
# ─────────────────────────────────────────────────────────
@st.cache_data
def load_audience_csv(file_bytes: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    df["Audience_n"] = pd.to_numeric(
        df["Audience"].astype(str).str.strip().str.replace(",", "", regex=False),
        errors="coerce",
    )
    df["Year"]        = pd.to_numeric(df["Year"], errors="coerce")
    df["Regional II"] = df["Regional II"].fillna("Unknown").str.strip()
    return df


# ─────────────────────────────────────────────────────────
# Authentication — using session state, no st.stop()
# ─────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("""
    <div class='login-wrap'>
      <div class='login-title'>Monkey Baa</div>
      <div class='login-sub'>AI Reporting System — sign in to continue</div>
    </div>
    """, unsafe_allow_html=True)

    col_c, col_form, col_r = st.columns([1, 2, 1])
    with col_form:
        with st.form("login_form"):
            username  = st.text_input("Username", placeholder="Enter username")
            password  = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Sign in", use_container_width=True, type="primary")

        if submitted:
            if username in VALID_USERS and VALID_USERS[username] == password:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("Incorrect username or password. Please try again.")

else:
    # ─────────────────────────────────────────────────────
    # Sidebar — only shown when authenticated
    # ─────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### AI Reporting System")
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
            st.caption("Navigate to any report above ↑")
        else:
            st.info("Upload the Audience CSV to enable reports.")

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
        user = st.session_state.get("username", "")
        st.caption(f"Signed in as **{user}**")
        if st.button("Sign out", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["username"] = ""
            st.rerun()

    # ─────────────────────────────────────────────────────
    # User Guide — main content
    # ─────────────────────────────────────────────────────
    h1, h2 = st.columns([3, 1])
    with h1:
        st.markdown("""
        <div class='page-header'>
          <div class='page-eyebrow'>Monkey Baa Theatre</div>
          <div class='page-title'>User Guide</div>
        </div>
        """, unsafe_allow_html=True)
    with h2:
        st.markdown("""
        <div style='text-align:right;padding-top:14px;font-size:22px;
                    font-weight:700;color:#222;font-style:italic;'>
          monkey baa
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='div'>", unsafe_allow_html=True)

    col_left, col_right = st.columns([5, 4], gap="large")

    with col_left:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Navigation</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-heading'>Available Reports</div>", unsafe_allow_html=True)

        reports = [
            ("1", "Executive Overview",
             "Full program summary for leadership and board — all key metrics in one view."),
            ("2", "Access & Audience Reach",
             "Total audience, geographic reach, Metro vs Regional vs Remote breakdown."),
            ("3", "Audience Feedback",
             "Comment sentiment analysis, improvement areas, and audience voice."),
            ("4", "Emotional & Social Impact",
             "Community outcomes, equity of experience, and social value of the program."),
            ("5", "Arts & Cultural Impact",
             "Cultural outcomes from the survey — identity, curiosity, and story recognition."),
            ("6", "High Quality Outcomes",
             "Year-on-year performance quality, event trends, and output benchmarks."),
            ("7", "Impact Report — Sponsors",
             "ROI narrative and outcomes tailored for funders and philanthropic partners."),
        ]

        for num, title, desc in reports:
            st.markdown(f"""
            <div class='report-row'>
              <div class='report-num'>{num}</div>
              <div>
                <div class='report-title'>{title}</div>
                <div class='report-desc'>{desc}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Getting Started</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-heading'>How to Use</div>", unsafe_allow_html=True)

        steps = [
            ("Enter your API key",
             "Paste your <b>OpenAI API key</b> in the sidebar. "
             "It stays only in this session and is never stored."),
            ("Upload data",
             "Use the <b>sidebar</b> to upload <b>Audience_final_data.csv</b> and the <b>Survey file</b>. "
             "Files stay loaded as you move between reports."),
            ("Select a report",
             "Use the <b>navigation menu</b> on the left to open any report page."),
            ("Generate insights",
             "Click <b>Generate AI Insights</b> inside the report. "
             "The system analyses your data and returns AI-powered findings."),
            ("Review & download",
             "Read the insights, charts, and executive summary. "
             "Download the report as a <b>Markdown</b> or <b>JSON</b> file at the bottom."),
        ]

        for i, (title, text) in enumerate(steps, 1):
            st.markdown(f"""
            <div class='step-row'>
              <div class='step-num'>{i}</div>
              <div class='step-text'><b>{title}</b> — {text}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class='card' style='background-color:#FDF3EE;border-left:4px solid {ORANGE};
                                 padding:14px 18px;margin-top:0;'>
          <div style='font-size:12px;font-weight:700;color:{ORANGE_DARK};margin-bottom:6px;'>
            About AI Insights
          </div>
          <div style='font-size:12px;color:{GRAY_TEXT};line-height:1.65;'>
            All insights are generated by GPT-4o using your uploaded data.
            Numbers are always drawn from the dataset — the model never fabricates figures.
            Each insight is aligned with Monkey Baa's Theory of Change framework.
          </div>
        </div>
        """, unsafe_allow_html=True)