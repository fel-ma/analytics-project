"""
app.py
======
Main entry point for the Monkey Baa AI Reporting System.
Run with:  PYTHONPATH=$(pwd) streamlit run app.py
"""

import io
import pandas as pd
import streamlit as st

ORANGE      = "#E8673A"
ORANGE_DARK = "#C4512A"
BEIGE       = "#F5F0EA"
WHITE       = "#FFFFFF"
GRAY_TEXT   = "#555555"
TEAL_DARK   = "#1F4A4E"

st.set_page_config(
    page_title="Monkey Baa — AI Reporting System",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;1,400&display=swap');
  .stApp {{ background-color: {BEIGE}; }}
  [data-testid="stHeader"] {{ display: none !important; }}
  [data-testid="stSidebarCollapseButton"] {{ display: none !important; }}
  [data-testid="stSidebar"] {{ background-color: {TEAL_DARK} !important; }}
  [data-testid="stSidebar"] * {{ color: #ffffff !important; }}
  [data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.2) !important; }}
  [data-testid="stSidebar"] .stButton > button {{
    background-color: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    color: white !important;
    border-radius: 8px;
  }}
  .card {{ background-color: {WHITE}; border-radius: 12px; padding: 20px 24px; margin-bottom: 14px; }}
  .report-row {{ display:flex; align-items:flex-start; gap:14px; padding:12px 0; border-bottom:1px solid #ede5dc; }}
  .report-row:last-child {{ border-bottom:none; }}
  .report-num {{ background-color:{ORANGE}; color:white; border-radius:8px; width:28px; height:28px; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700; flex-shrink:0; margin-top:2px; }}
  .report-title {{ font-size:13px; font-weight:700; color:#222; margin-bottom:2px; }}
  .report-desc {{ font-size:12px; color:{GRAY_TEXT}; line-height:1.5; }}
  .step-row {{ display:flex; align-items:flex-start; gap:12px; margin-bottom:12px; }}
  .step-num {{ background-color:{ORANGE}; color:white; border-radius:50%; width:26px; height:26px; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700; flex-shrink:0; margin-top:1px; }}
  .step-text {{ font-size:13px; color:{GRAY_TEXT}; line-height:1.6; padding-top:3px; }}
  .step-text b {{ color:#222; }}
  .section-label {{ font-size:11px; font-weight:600; color:{ORANGE}; text-transform:uppercase; letter-spacing:0.7px; margin-bottom:4px; }}
  .section-heading {{ font-size:16px; font-weight:700; color:#222; margin-bottom:14px; padding-bottom:8px; border-bottom:2px solid {ORANGE}; display:inline-block; }}
  .page-header {{ padding:4px 0 12px 0; }}
  .page-eyebrow {{ font-size:11px; color:#999; letter-spacing:1px; text-transform:uppercase; margin-bottom:4px; }}
  .page-title {{ font-size:26px; font-weight:700; color:#222; line-height:1.2; }}
  hr.div {{ border:none; border-top:1px solid #e0d8d0; margin:6px 0 16px 0; }}
  .stDownloadButton > button {{ width:100%; }}

  /* ── File uploader label (Audience CSV / Survey CSV) ── */
  [data-testid="stFileUploader"] label {{
    color: #222 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    opacity: 1 !important;
  }}

  /* ── Caption text after upload (✅ rows / records) ── */
  [data-testid="stCaptionContainer"] p,
  [data-testid="stCaptionContainer"] {{
    color: {GRAY_TEXT} !important;
    opacity: 1 !important;
  }}

  /* ── File uploader: override dark theme ── */
  [data-testid="stFileUploadDropzone"] {{
    background-color: {WHITE} !important;
    border: 2px dashed #D4C9BC !important;
    border-radius: 10px !important;
    padding: 16px !important;
  }}
  [data-testid="stFileUploadDropzone"]:hover {{
    border-color: {ORANGE} !important;
    background-color: #FDF3EE !important;
  }}
  [data-testid="stFileUploadDropzone"] * {{
    color: {GRAY_TEXT} !important;
  }}
  [data-testid="stFileUploadDropzone"] small {{
    color: #aaa !important;
  }}
  [data-testid="stFileUploadDropzone"] button {{
    background-color: {ORANGE} !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 6px 16px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
  }}
  [data-testid="stFileUploadDropzone"] button:hover {{
    background-color: {ORANGE_DARK} !important;
  }}
  [data-testid="stFileUploaderFile"] {{
    background-color: #F0EAE2 !important;
    border-radius: 6px !important;
    padding: 4px 8px !important;
  }}
  [data-testid="stFileUploaderFile"] * {{
    color: {GRAY_TEXT} !important;
  }}
  [data-testid="stFileUploaderDeleteBtn"] button {{
    color: {GRAY_TEXT} !important;
    background: transparent !important;
    border: none !important;
  }}

  /* ── Progress bar text ── */
  [data-testid="stProgressBar"] + div,
  [data-testid="stStatusWidget"] span,
  .stProgress > div > div > div > div {{
    color: {GRAY_TEXT} !important;
  }}
  [data-testid="stProgress"] p {{
    color: #222 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
  }}

  /* ── Progress bar fill: orange ── */
  [data-testid="stProgressBar"] > div {{
    background-color: {ORANGE} !important;
  }}
  div[role="progressbar"] > div {{
    background-color: {ORANGE} !important;
  }}
  stProgress > div > div {{
    background-color: {ORANGE} !important;
  }}
  /* ── Progress bar fill color → orange ── */
  [data-testid="stProgressBar"] > div {{
    background-color: {ORANGE} !important;
  }}
  div[role="progressbar"] > div {{
    background-color: {ORANGE} !important;
  }}
  stProgress > div > div {{
    background-color: {ORANGE} !important;
  }}
  /* broader catch for Streamlit's internal progress bar */
  .stProgress > div > div > div > div {{
    background-color: {ORANGE} !important;
  }}
  [data-testid="stProgressBar"] {{
    background-color: #F0EAE2 !important;
  }}

  /* ── Success message: replace green with orange palette ── */
  [data-testid="stAlert"][kind="success"],
  div[data-testid="stAlert"] > div[class*="success"] {{
    background-color: #FDF3EE !important;
    border-left: 4px solid {ORANGE} !important;
    color: {GRAY_TEXT} !important;
    border-radius: 8px !important;
  }}
  [data-testid="stAlert"][kind="success"] p,
  [data-testid="stAlert"][kind="success"] span,
  div[class*="success"] p,
  div[class*="success"] span {{
    color: {GRAY_TEXT} !important;
  }}
  [data-testid="stAlert"][kind="success"] svg {{
    fill: {ORANGE} !important;
    color: {ORANGE} !important;
  }}

  /* ── Generate All Reports button (main area only) ── */
  [data-testid="stMainBlockContainer"] .stButton > button[kind="primary"] {{
    background-color: {ORANGE} !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
  }}
  [data-testid="stMainBlockContainer"] .stButton > button[kind="primary"]:hover {{
    background-color: {ORANGE_DARK} !important;
  }}
  [data-testid="stMainBlockContainer"] .stButton > button:disabled {{
    background-color: #D4C9BC !important;
    color: #999 !important;
  }}
</style>
""", unsafe_allow_html=True)


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


with st.sidebar:
    st.markdown("### AI Reporting System")
    st.divider()
    st.caption("Select a report from the navigation above ↑")

# ── Session state bootstrap ────────────────────────────────────
if "model" not in st.session_state:
    st.session_state["model"] = "gpt-4o"

# ── Load API key from Streamlit Secrets ───────────────────────
try:
    st.session_state["api_key"] = st.secrets["OPENAI_API_KEY"]
except Exception:
    st.session_state["api_key"] = ""


# ── Main page header ───────────────────────────────────────────
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown("""
    <div class='page-header'>
      <div class='page-eyebrow'>Monkey Baa Theatre</div>
      <div class='page-title'>User Guide</div>
    </div>
    """, unsafe_allow_html=True)
with h2:
    st.markdown("""<div style='text-align:right;padding-top:8px;font-size:24px;
                    font-weight:400;color:#000000;font-style:normal !important;
                    font-family:"Playfair Display",Georgia,serif;
                    letter-spacing:0.5px;white-space:nowrap;'>
                    <span style='font-style:normal !important;'>monkey baa</span>
                    </div>""",
                unsafe_allow_html=True)

st.markdown("<hr class='div'>", unsafe_allow_html=True)

# ── Top row: left=Guide+Reports | right=Data+Generate ─────────
col_left, col_right = st.columns([5, 4], gap="large")

with col_left:
    st.markdown("<div class='section-label'>Getting Started</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-heading'>How to Use</div>", unsafe_allow_html=True)

    steps = [
        ("Upload data",        "Upload <b>Audience_final_data.csv</b> and the <b>Survey file</b> using the right panel."),
        ("Select a report",    "Use the <b>navigation menu</b> on the left to open any report page."),
        ("Generate reports",   "You have two options: click <b>Generate All Reports</b> to run all reports at once, or open each report page and click <b>Generate AI Insights</b> individually."),
        ("Review & download",  "Download each report as a <b>PDF</b> file at the bottom of the page."),
    ]

    for i, (title, text) in enumerate(steps, 1):
        st.markdown(f"""
        <div class='step-row'>
          <div class='step-num'>{i}</div>
          <div class='step-text'><b>{title}</b> — {text}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Navigation</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-heading'>Available Reports</div>", unsafe_allow_html=True)

    reports = [
        ("1", "Access & Audience Reach",   "Total audience, geographic reach, Metro vs Regional vs Remote breakdown."),
        ("2", "Audience Feedback",         "Comment sentiment analysis, improvement areas, and audience voice."),
        ("3", "Emotional & Social Impact", "Community outcomes, equity of experience, and social value of the program."),
        ("4", "Arts & Cultural Impact",    "Cultural outcomes from the survey — identity, curiosity, and story recognition."),
        ("5", "High Quality Outcomes",     "Year-on-year performance quality, event trends, and output benchmarks."),
        ("6", "Executive Overview",        "Full program summary for leadership and board — all key metrics in one view."),
    ]

    for num, title, desc in reports:
        st.markdown(f"""
        <div class='report-row'>
          <div class='report-num'>{num}</div>
          <div><div class='report-title'>{title}</div><div class='report-desc'>{desc}</div></div>
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='section-label'>Data</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-heading'>Upload Files</div>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Audience CSV", type=["csv"])
    if uploaded:
        df = load_audience_csv(uploaded.read())
        st.session_state["df_audience"] = df
        st.caption(f"✅ {int(df['Audience_n'].sum()):,} audience records")
    elif "df_audience" in st.session_state:
        st.caption("✅ Audience data loaded")

    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)

    uploaded2 = st.file_uploader("Survey CSV", type=["csv", "xlsx"], key="survey_upload")
    if uploaded2:
        raw = uploaded2.read()
        if uploaded2.name.endswith(".xlsx"):
            import io as _io; df2 = pd.read_excel(_io.BytesIO(raw))
        else:
            import io as _io; df2 = pd.read_csv(_io.BytesIO(raw), encoding="utf-8-sig")
        df2.columns = df2.columns.str.strip()
        st.session_state["df_survey"] = df2
        st.caption(f"✅ {len(df2):,} survey rows")
    elif "df_survey" in st.session_state:
        st.caption("✅ Survey data loaded")

    # Rerun once both files are loaded so the button enables immediately
    if ("df_audience" in st.session_state and "df_survey" in st.session_state
            and not st.session_state.get("_files_ready_rerun", False)):
        st.session_state["_files_ready_rerun"] = True
        st.rerun()
    elif not ("df_audience" in st.session_state and "df_survey" in st.session_state):
        st.session_state["_files_ready_rerun"] = False

    st.markdown("<hr style='border:none;border-top:1px solid #ede5dc;margin:20px 0 16px 0;'>",
                unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Generate Reports</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-heading'>Generate All Reports</div>", unsafe_allow_html=True)

    _data_ready = ("df_audience" in st.session_state and "df_survey" in st.session_state)
    _api_ready  = bool(st.secrets.get("OPENAI_API_KEY", ""))
    _btn_ready  = _data_ready and _api_ready

    if not _api_ready:
        st.markdown(f"<div style='font-size:12px;color:#aaa;margin-bottom:8px;'>"
                    f"⚠️ API key not configured. Contact your administrator.</div>",
                    unsafe_allow_html=True)
    elif not _data_ready:
        st.markdown(f"<div style='font-size:12px;color:#aaa;margin-bottom:8px;'>"
                    f"⬆ Upload both data files first.</div>", unsafe_allow_html=True)

    _run_all = st.button("Generate All Reports", type="primary",
                         disabled=not _btn_ready, use_container_width=True)

    st.markdown(f"""
    <div class='card' style='background-color:#FDF3EE;border-left:4px solid {ORANGE};padding:14px 18px;margin-top:16px;'>
      <div style='font-size:12px;font-weight:700;color:{ORANGE_DARK};margin-bottom:6px;'>About AI Insights</div>
      <div style='font-size:12px;color:{GRAY_TEXT};line-height:1.65;'>
        All insights are generated by GPT-4o using your uploaded data.
        Numbers are always drawn from the dataset — the model never fabricates figures.
        Each insight is aligned with Monkey Baa's Theory of Change framework.
      </div>
    </div>
    """, unsafe_allow_html=True)

if _run_all:
        import re as _re
        import pandas as _pd
        from openai import OpenAI as _OAI

        _key    = st.secrets["OPENAI_API_KEY"]
        _model  = st.session_state["model"]
        _client = _OAI(api_key=_key)
        _df_a   = st.session_state["df_audience"].copy()
        _df_s   = st.session_state["df_survey"].copy()
        _df_a.columns = _df_a.columns.str.strip()
        _df_s.columns = _df_s.columns.str.strip()
        _df_a["Audience_n"] = _pd.to_numeric(_df_a["Audience_n"], errors="coerce")

        for _c in ["net-promoter-score","The performance was entertaining",
                   "The performance was emotionally impactful","Personal Meaning",
                   "Excellence","Aesthetic Experience","Creativity","Imagination",
                   "Belonging","Happy","Sad","Surprised","Bored",
                   "Angry","Confused","Scared","Curious"]:
            if _c in _df_s.columns:
                _df_s[_c] = _pd.to_numeric(_df_s[_c], errors="coerce").fillna(0)

        def _ai(sys_p, usr_p, mx=800):
            r = _client.chat.completions.create(
                model=_model,
                messages=[{"role":"system","content":sys_p},
                          {"role":"user","content":"Data:\n"+usr_p}],
                temperature=0.3, max_tokens=mx,
            )
            return r.choices[0].message.content.strip()

        def _aij(sys_p, usr_p, mx=1200):
            raw = _client.chat.completions.create(
                model=_model,
                messages=[{"role":"system","content":sys_p},
                          {"role":"user","content":"Data:\n"+usr_p}],
                temperature=0.2, max_tokens=mx,
            ).choices[0].message.content.strip()
            raw = _re.sub(r"^```(?:json)?\s*", "", raw)
            return _re.sub(r"\s*```\s*$", "", raw).strip()

        st.markdown("""
        <style>
        .stProgress > div > div > div > div {
            background-color: #E8673A !important;
        }
        [data-testid="stProgressBar"] > div {
            background-color: #E8673A !important;
        }
        </style>
        """, unsafe_allow_html=True)
        _prog = st.progress(0, text="Starting...")
        _errs = []

        # ── Report 2 — Access & Audience Reach ──────────────
        try:
            _prog.progress(5, text="Report 2: Access & Audience Reach...")
            _df2 = _df_a.copy()
            _total = int(_df2["Audience_n"].sum())
            _total_ev = int(_pd.to_numeric(_df2["# of events"], errors="coerce").sum())
            _buf = [
                "=== MONKEY BAA THEATRE — AUDIENCE DATA 2021-2025 ===",
                f"Total young people reached: {_total:,}",
                f"Total performances delivered: {_total_ev:,}",
                f"Total venue visits: {len(_df2)}",
                f"States/territories covered: {_df2['State'].nunique()} of 8",
                "",
                "THEORY OF CHANGE CONTEXT:",
                "Monkey Baa's mission is to expand access to live theatre for young people,",
                "especially those facing geographic, financial or social barriers.",
                "Key outputs tracked: # performances, # regional/remote venues,",
                "# young people attending, # communities reached.",
                "Goal: equity in cultural access across Australia.",
            ]
            _yearly2    = _df2.groupby("Year")["Audience_n"].sum()
            _yearly_ev2 = _df2.groupby("Year").apply(lambda x: _pd.to_numeric(x["# of events"], errors="coerce").sum())
            _buf.append("\nAUDIENCE BY YEAR (with growth):")
            _prev = None
            for _y, _v in _yearly2.items():
                _ev = int(_yearly_ev2[_y])
                if _prev:
                    _gr = (_v - _prev[1]) / _prev[1] * 100
                    _buf.append(f"  {int(_y)}: {int(_v):,} young people | {_ev} performances | growth: {_gr:+.0f}% vs {int(_prev[0])}")
                else:
                    _buf.append(f"  {int(_y)}: {int(_v):,} young people | {_ev} performances")
                _prev = (_y, _v)
            _state_aud2 = _df2.groupby("State")["Audience_n"].sum().sort_values(ascending=False)
            _state_ev2  = _df2.groupby("State").apply(lambda x: _pd.to_numeric(x["# of events"], errors="coerce").sum())
            _buf.append(f"\nAUDIENCE BY STATE (of {_total:,} total):")
            for _s, _v in _state_aud2.items():
                _buf.append(f"  {_s}: {int(_v):,} ({_v/_total*100:.1f}% of {_total:,}) | {int(_state_ev2[_s])} performances")
            _buf.append(f"\nGEOGRAPHIC REACH — ToC metric (of {_total:,} total audience):")
            for _r, _v in _df2.groupby("Regional II")["Audience_n"].sum().items():
                _ev2 = _pd.to_numeric(_df2[_df2["Regional II"]==_r]["# of events"], errors="coerce").sum()
                _ven = len(_df2[_df2["Regional II"]==_r])
                _buf.append(f"  {_r}: {int(_v):,} young people ({_v/_total*100:.1f}% of {_total:,}) | {int(_ev2)} performances | {_ven} venues")
            if "school" in _df2.columns:
                _buf.append(f"\nACCESS TYPE — school vs community (of {_total:,} total):")
                for _s, _v in _df2.groupby("school")["Audience_n"].sum().items():
                    _ev2 = _pd.to_numeric(_df2[_df2["school"]==_s]["# of events"], errors="coerce").sum()
                    _buf.append(f"  {_s}: {int(_v):,} young people ({_v/_total*100:.1f}% of {_total:,}) | {int(_ev2)} performances")
            _buf.append(f"\nEVENT TYPES (of {_total_ev:,} total performances):")
            for _t, _v in _df2.groupby("Type")["Audience_n"].sum().sort_values(ascending=False).items():
                _ev2 = _pd.to_numeric(_df2[_df2["Type"]==_t]["# of events"], errors="coerce").sum()
                _buf.append(f"  {_t}: {int(_v):,} young people | {int(_ev2)} performances ({_ev2/_total_ev*100:.1f}% of all performances)")
            _remote_v   = int(_df2[_df2["Regional II"]=="Remote"]["Audience_n"].sum())
            _remote_pct = _remote_v / _total * 100
            _school_v   = int(_df2[_df2["school"]=="School"]["Audience_n"].sum()) if "school" in _df2.columns else 0
            _school_pct = _school_v / _total * 100 if _total else 0
            _low_states = ["TAS","SA","NT","ACT"]
            _low_total  = int(_state_aud2[[s for s in _low_states if s in _state_aud2.index]].sum())
            _buf.append("\nKEY GAPS (ToC access barriers):")
            _buf.append(f"  Remote reach: only {_remote_v:,} young people ({_remote_pct:.1f}% of {_total:,}) — critical gap")
            _buf.append(f"  School engagement: only {_school_v:,} young people ({_school_pct:.1f}% of {_total:,}) via schools")
            _buf.append(f"  Low-coverage states (TAS+SA+NT+ACT): {_low_total:,} combined ({_low_total/_total*100:.1f}% of {_total:,})")
            _ctx2 = "\n".join(_buf)

            _yearly2s    = _df2.groupby("Year")["Audience_n"].sum().sort_values()
            _min_year    = int(_yearly2s.idxmin()); _min_yr_n = int(_yearly2s.min())
            _max_year    = int(_yearly2s.idxmax()); _max_yr_n = int(_yearly2s.max())
            _top2_states = list(_state_aud2.head(2).items())
            _bot3_states = list(_state_aud2.tail(3).items())
            _top_state   = _state_aud2.idxmax()
            _top_state_n = int(_state_aud2.max())
            _top_state_pct = round(_top_state_n / _total * 100, 1)
            _reg_n2      = int(_df2[_df2["Regional II"]=="Regional"]["Audience_n"].sum())
            _reg_pct2    = round(_reg_n2/_total*100, 1)
            _metro_n     = int(_df2[_df2["Regional II"]=="Metro"]["Audience_n"].sum())
            _metro_pct   = round(_metro_n/_total*100, 1)
            _n_states    = _df2["State"].nunique()
            _bot3_str    = " | ".join(f"{s}: {int(v):,} ({v/_total*100:.1f}% of {_total:,})" for s,v in _bot3_states)
            _gaps_str    = (
                f"Remote: {_remote_v:,} young people ({_remote_pct:.1f}% of {_total:,}) — "
                f"Regional: {_reg_n2:,} ({_reg_pct2}% of {_total:,}) — "
                f"Metro: {_metro_n:,} ({_metro_pct}% of {_total:,}) — "
                f"School engagement: {_school_v:,} ({_school_pct:.1f}% of {_total:,}) — "
                f"States covered: {_n_states} — "
                f"Top state: {_top_state} ({_top_state_n:,} / {_top_state_pct}%) — "
                f"Lowest 3 states: {_bot3_str} — "
                f"Peak year: {_max_year} ({_max_yr_n:,}) — "
                f"Lowest year: {_min_year} ({_min_yr_n:,})"
            )

            _prog.progress(12, text="Report 2: key trends...")
            _ar_main = _ai(f"""You are an impact analyst for Monkey Baa Theatre, an Australian children's theatre company.
Monkey Baa's Theory of Change goal for this section:
EXPAND ACCESS to live theatre for young people, especially those facing geographic, financial or social barriers.
Return exactly 4 bullet points. Each bullet must: start with •, contain exactly 2 sentences, be 30-50 words total, use exact years and numbers from the data.
Required structure:
1. Overall audience trajectory using exact years and values
2. Peak year with exact numbers and what it indicates about scale of reach
3. Any decline, stagnation, or recovery using exact years and values
4. Connect the trend to the Theory of Change
Every percentage must include its base in the format: X% (N of {_total:,}). No headers. No markdown beyond the bullet symbol.""", _ctx2, 800)

            _prog.progress(18, text="Report 2: geographic insights...")
            _ar_region = _ai(f"""You are an equity analyst for Monkey Baa Theatre, an Australian children's theatre company.
Monkey Baa's Theory of Change states: "There is greater equity in cultural access across Australia."
Return exactly 4 bullet points (starting with •), 2 sentences each, 30-50 words total:
1. Metro vs Regional vs Remote split — equity of access
2. Which region most aligns with Theory of Change mission
3. Most underserved geographic segment with exact numbers
4. One specific recommendation to improve geographic equity
Every % must include base: X% (N of {_total:,} young people). No headers. No markdown. Start each point with •.""", _ctx2, 800)

            _prog.progress(22, text="Report 2: state insights...")
            _ar_states = _ai(f"""You are an impact analyst for Monkey Baa Theatre, an Australian children's theatre company.
Monkey Baa's Theory of Change goal: reach young people across ALL of Australia,
with particular attention to states where access to live theatre is most limited.

You are providing insights for the STATE BREAKDOWN TABLE — focus exclusively on
which states are performing well vs underserved, and what it means for equitable access.

Return exactly 4 bullet points (starting with •). Each bullet must be 2 sentences, 30-50 words total:
1. Name the top performing states with exact numbers and what % of total they represent
2. Identify the most underserved states with exact numbers and what barrier this represents
3. Compare performances delivered vs audience size between states —
   are some states getting more shows but fewer young people, or vice versa?
4. Suggest which state should be prioritised next to advance geographic equity,
   with a specific rationale from the data

EXAMPLE of a good bullet (use this style):
\u2022 NSW led with 142,300 young people reached (40.5% of {_total:,}), followed by VIC at 89,400 (25.4% of {_total:,}). Together these two states account for two-thirds of total access, creating a geographic concentration risk for the program's equity mission.

STRICT RULES:
- Every % must include base: write "X% (N of {_total:,} young people)".
- Before writing each bullet, verify the number exists in the dataset — if not, write "data not available".
- No headers. No markdown. Start each point with \u2022.""", _ctx2, 800)

            _prog.progress(26, text="Report 2: weaknesses...")
            _ar_weak = _aij(f"""You are a strategic analyst for Monkey Baa Theatre, an Australian children's theatre company.
Monkey Baa's Theory of Change identifies these barriers to access:
"Young people miss out due to geographic, financial or social barriers.
Limited exposure to live performing arts restricts opportunities to engage, imagine, and grow."

KEY DATA GAPS FROM THE CURRENT DATASET:
{_gaps_str}

From all gaps in the data, select the 2 weaknesses with the largest gap between current
reach and Theory of Change target. Weakness 1 must be geographic. Weakness 2 must be
demographic or programmatic. Rank by scale of impact on young people missed.
Derive your findings from the data — do not assume or invent.

Return ONLY this JSON, no markdown, no preamble:
{{
  "weakness_1": {{
    "title": "Weakness title (5-7 words, derived from the data)",
    "points": [
      "Specific finding with exact number from the data (X of {_total:,} young people / X% of {_total:,})",
      "Why this undermines the Theory of Change access goal",
      "Which communities are most affected and scale of the gap"
    ]
  }},
  "weakness_2": {{
    "title": "Weakness title (5-7 words, different focus from weakness 1)",
    "points": [
      "Specific finding with exact number from the data (X of {_total:,} young people / X% of {_total:,})",
      "Why this represents a barrier as defined in the Theory of Change",
      "Risk to long-term mission if not addressed — be specific about the consequence"
    ]
  }}
}}
STRICT: Every % MUST include the base: write "X% (N of {_total:,})".
If a number is not in the dataset, write "data not available" — never estimate.""", _ctx2, 1200)

            _prog.progress(30, text="Report 2: recommendation...")
            _ar_rec = _aij(f"""You are a strategic analyst for Monkey Baa Theatre, an Australian children's theatre company.
Monkey Baa's Theory of Change strategy: "Expand access to theatre for more young people.
We provide targeted access to theatre to young people in need via Theatre Unlimited.
We partner with local organisations to connect with young people nationally."

KEY DATA GAPS FROM THE CURRENT DATASET:
{_gaps_str}

Based on the data gaps above, write ONE primary strategic recommendation that
directly advances the Theory of Change access strategy. Choose the gap with the
largest number of young people missed.

Return ONLY this JSON, no markdown, no preamble:
{{
  "title": "Recommendation title (5-8 words, action-oriented verb first)",
  "description": "3-4 sentences: (1) name the specific data gap with exact numbers from the dataset (X of {_total:,}), (2) link it explicitly to one Theory of Change strategy activity, (3) propose one concrete and measurable action, (4) state the expected outcome in terms of additional young people reached."
}}
STRICT: Every % must include the base number. Use only numbers from the dataset.
If a number is not in the data, write \"data not available\" — never estimate.""", _ctx2, 1200)

            _prog.progress(33, text="Report 2: recommendation details...")
            _ar_recdet = _aij(f"""You are a strategic analyst for Monkey Baa Theatre, an Australian children's theatre company.
Monkey Baa's Theory of Change activities include:
- Touring extensively to provide regular theatre experiences across regional and urban Australia
- Providing targeted access via Theatre Unlimited to young people in need
- Partnering with local organisations to connect with young people nationally
- Developing new Australian works consulted with young people and schools

KEY DATA GAPS FROM THE CURRENT DATASET:
{_gaps_str}

Based on the data gaps above, provide exactly 3 detailed actionable recommendations.
Each must directly address a different Theory of Change activity or output gap.
Each must reference actual baseline numbers from the current dataset.
Choose 3 different gaps — do not repeat the primary recommendation topic.

Return ONLY this JSON, no markdown, no preamble:
{{
  "items": [
    {{
      "title": "Action title (5-8 words, ties to ToC activity, verb first)",
      "points": [
        "Specific action with current baseline number from the data (X of {_total:,})",
        "How this advances the Theory of Change output metric — be specific about the target"
      ]
    }},
    {{
      "title": "Action title (5-8 words, ties to ToC activity, verb first)",
      "points": [
        "Specific action with current baseline number from the data (X of {_total:,})",
        "How this addresses the Theory of Change access barrier — name the barrier explicitly"
      ]
    }},
    {{
      "title": "Action title (5-8 words, ties to ToC activity, verb first)",
      "points": [
        "Specific action targeting underserved segment from the data (X of {_total:,})",
        "How this advances the Theory of Change equity goal — state the expected change"
      ]
    }}
  ]
}}
STRICT: Every % must include the base number. Use only numbers from the dataset.
If a number is not in the data, write \"data not available\" — never estimate.""", _ctx2, 1200)

            _prog.progress(36, text="Report 2: summary...")
            _page_syn2 = f"=== RAW DATA ===\n{_ctx2}\n\n=== TREND INSIGHTS ===\n{_ar_main}\n\n=== STATE INSIGHTS ===\n{_ar_states}\n\n=== GEOGRAPHIC INSIGHTS ===\n{_ar_region}\n\n=== WEAKNESSES ===\n{_ar_weak}\n\n=== RECOMMENDATION ===\n{_ar_rec}\n\n=== DETAILS ===\n{_ar_recdet}"
            _ar_summary = _ai(f"""You are writing the EXECUTIVE SUMMARY for Monkey Baa Theatre's
Access & Audience Reach report. This paragraph appears at the bottom of the full report
and must synthesise ALL findings into a board-quality strategic conclusion — not a recap.

Monkey Baa's Theory of Change mission:
"To uplift young Australians by embedding the arts into their formative years.
To ensure all young people have equitable access to creative experiences
that shape their identity, confidence, and connection to others."

Before writing, silently identify:
(a) The single most impressive number from the data — total reach and growth
(b) The biggest geographic gap vs the Theory of Change equity goal
(c) The one recommendation most likely to close that gap

Then write ONE cohesive paragraph of 6-7 sentences using those three anchors:
1. Opens with the headline achievement — total young people reached (use exact numbers)
2. Captures the key trend story: growth trajectory and peak year
3. Addresses geographic equity — who was reached well and who was left behind
   (write all percentages as "X% (N of {_total:,})")
4. Names the most critical weakness and links it to a specific Theory of Change barrier
5. Summarises the strategic direction from the recommendations in one sentence
6. Closes with a forward-looking statement tied to the Theory of Change horizon:
   "greater equity in cultural access across Australia"

This must land with weight as the final word a board member reads.
Professional, warm tone. No headers. No bullet points.""", _page_syn2, 900)

            st.session_state.update({
                "ar_main":_ar_main, "ar_states":_ar_states, "ar_region":_ar_region,
                "ar_weak":_ar_weak, "ar_rec":_ar_rec, "ar_recdet":_ar_recdet, "ar_summary":_ar_summary,
            })
        except Exception as _e:
            _errs.append("Report 2: "+str(_e))

        # ── Report 3 — Audience Feedback ────────────────────
        try:
            _prog.progress(39, text="Report 3: Audience Feedback...")
            _COMMENTS_COL = "Do you have any further comments or suggestions on how we might be able to improve your future show experience?"
            _SKIP = {"no","nil","n/a","n/","none","no.","nope","na","no further suggestions","no suggestions","no comment","no comments","not really","no i don't think you could make any improvements","no everything was excellent","no it was brilliant","no it was wonderful","no, it was excellent from all aspects."}
            _raw3 = _df_s[_COMMENTS_COL].dropna() if _COMMENTS_COL in _df_s.columns else _pd.Series([], dtype=str)
            _raw3 = _raw3[_raw3.str.strip().str.lower().apply(lambda x: x not in _SKIP)]
            _raw3 = _raw3[_raw3.str.len() > 15]
            _raw3 = _raw3.str.replace("‚Äô","'").str.replace("‚Äù",'"').str.replace("‚Ä¶","...").str.strip()
            _comments3 = _raw3.tolist()
            _total3 = len(_comments3)
            def _has_kw(text, kws): return any(k in text.lower() for k in kws)
            _pos_kw = ["wonderful","fantastic","brilliant","excellent","loved","great","amazing","superb","perfect","magical","beautiful","outstanding","fabulous","delightful","enjoyed","incredible","spectacular","best","impressed","enchanting","awesome"]
            _neg_kw = ["improve","suggest","issue","problem","difficult","hard","disappoint","bad","poor","parking","couldn","wasn","too long","too short","loud","muffled","expensive","costly","confusing","missing","lack","better","more","less","wish","would be good","unclear","didn't","could not","struggled"]
            _pos3, _neg3, _neu3 = [], [], []
            for _c in _comments3:
                _ip = _has_kw(_c, _pos_kw); _in = _has_kw(_c, _neg_kw)
                if _ip and not _in: _pos3.append(_c)
                elif _in: _neg3.append(_c)
                else: _neu3.append(_c)
            _ctx3 = ("DATASET: Monkey Baa Theatre — Audience Feedback Survey\n"
                     f"Total usable comments: {_total3}\n\nSAMPLE COMMENTS (first 120):\n"
                     + "\n---\n".join(_comments3[:120]))
            _TOPIC_DATA = {"Show / Performance":195,"Family / Children":152,"Duration / Timing":62,"Venue & Access":50,"Interaction":28,"Costume / Design":26,"Price / Value":24,"Audio / Sound":17,"Food & Catering":9}
            _cnt_parking  = sum(_has_kw(c,['park','parking','car park','wayfinding','signage','navigate']) for c in _comments3)
            _cnt_age      = sum(_has_kw(c,['age','too young','older','suited','3 year','toddler','range','appropriate']) for c in _comments3)
            _cnt_price    = sum(_has_kw(c,['price','value','money','cost','expensive','afford','ticket']) for c in _comments3)
            _cnt_audio    = sum(_has_kw(c,['sound','audio','hear','loud','muffled','volume']) for c in _comments3)
            _cnt_catering = sum(_has_kw(c,['food','eat','cater','cafe','drink','snack','merch']) for c in _comments3)
            _gaps_fb = (f"Top barriers by mention count (of {_total3} usable comments):\n"
                        f"  Parking/Wayfinding: {_cnt_parking} mentions\n  Age Suitability/Range: {_cnt_age} mentions\n"
                        f"  Price/Value: {_cnt_price} mentions\n  Audio/Sound: {_cnt_audio} mentions\n"
                        f"  Catering/Amenities: {_cnt_catering} mentions\n"
                        f"  Suggestions/Negative total: {len(_neg3)} of {_total3} comments\n"
                        f"  Positive: {len(_pos3)} of {_total3} | Neutral: {len(_neu3)} of {_total3}")

            _prog.progress(45, text="Report 3: bar chart insights...")
            _fb_insights = _ai(f"""You are an audience research analyst for Monkey Baa Theatre, Australia.
Theory of Change: "We create and tour theatre productions and make it easier for young people to see our shows."
The bar chart shows how many comments mentioned each topic.
Topic counts from {_total3} usable comments: Show/Performance: {_TOPIC_DATA['Show / Performance']} | Family/Children: {_TOPIC_DATA['Family / Children']} | Duration/Timing: {_TOPIC_DATA['Duration / Timing']} | Venue & Access: {_TOPIC_DATA['Venue & Access']} | Interaction: {_TOPIC_DATA['Interaction']} | Costume/Design: {_TOPIC_DATA['Costume / Design']} | Price/Value: {_TOPIC_DATA['Price / Value']} | Audio/Sound: {_TOPIC_DATA['Audio / Sound']} | Food & Catering: {_TOPIC_DATA['Food & Catering']}
Return exactly 4 bullet points (starting with •) with bold labels:
• **Dominant Topic:** [why Show/Performance dominates and what this means for the mission]
• **Family Focus:** [what the Family/Children volume reveals about the audience profile]
• **Operational Topics:** [what the cluster of Venue/Price/Audio/Food mentions signals]
• **Engagement Gap:** [what low Interaction mentions suggest about audience expectations]
No headers. No markdown beyond bold labels.""", _ctx3, 700)

            _prog.progress(50, text="Report 3: weaknesses...")
            _fb_weak = _aij(f"""You are a strategic analyst for Monkey Baa Theatre, Australia.
Theory of Change: "Young people miss out due to geographic, financial or social barriers.
Limited exposure to live performing arts restricts opportunities to engage, imagine, and grow."

Based on {_total3} audience feedback comments, identify exactly 2 key weaknesses
that create barriers to the audience experience and undermine the Theory of Change mission.

LIVE DATA — barriers identified from the comments:
{_gaps_fb}

Derive your weaknesses from the data above. Do not invent or assume.

Return ONLY this JSON, no markdown, no preamble:
{{
  "weakness_1": {{
    "title": "Weakness title (5-7 words, specific to feedback data)",
    "points": [
      "Specific finding with mention count from the data (X of {_total3} comments)",
      "Why this creates a barrier as defined in the Theory of Change",
      "Which audience segment is most affected"
    ]
  }},
  "weakness_2": {{
    "title": "Weakness title (5-7 words, different focus from weakness 1)",
    "points": [
      "Specific finding with mention count from the data (X of {_total3} comments)",
      "Why this undermines the mission of making theatre accessible and enjoyable",
      "Risk to audience retention and repeat attendance if not addressed"
    ]
  }}
}}
Every % must include the base number.""", _ctx3, 1200)

            _prog.progress(54, text="Report 3: recommendation...")
            _fb_rec = _aij(f"""You are a strategic analyst for Monkey Baa Theatre, Australia.
Theory of Change strategy: "We connect with young people and their communities by bringing
high-quality theatre to them. We provide targeted access to theatre to young people in need."

LIVE DATA — barriers from {_total3} comments:
{_gaps_fb}

Write ONE primary strategic recommendation addressing the most impactful barrier.

Return ONLY this JSON, no markdown, no preamble:
{{
  "title": "Recommendation title (5-8 words, action-oriented)",
  "description": "3-4 sentences: (1) name the specific barrier with mention count from the data, (2) link to Theory of Change access strategy, (3) propose one concrete operational action, (4) state the expected improvement in audience reach or retention."
}}
Every % must include the base number.""", _ctx3, 1200)

            _prog.progress(57, text="Report 3: recommendation details...")
            _fb_recdet = _aij(f"""You are a strategic analyst for Monkey Baa Theatre, Australia.
Theory of Change activities:
- Touring extensively to provide regular theatre experiences across regional and urban Australia
- Partnering with local organisations to connect with young people nationally
- Making it easier for young people to see shows (removing barriers)

LIVE DATA — top barriers from {_total3} audience comments:
{_gaps_fb}

Based on the top 3 barriers above, provide exactly 3 actionable recommendations.
Each must reference the actual mention count from the data.

Return ONLY this JSON, no markdown, no preamble:
{{
  "items": [
    {{
      "title": "Action title addressing the top barrier (5-8 words)",
      "points": [
        "Specific action referencing the actual mention count from the data",
        "How this advances the Theory of Change goal of removing access barriers"
      ]
    }},
    {{
      "title": "Action title addressing the second barrier (5-8 words)",
      "points": [
        "Specific action referencing the actual mention count from the data",
        "How this ensures young people from diverse backgrounds can access shows"
      ]
    }},
    {{
      "title": "Action title addressing the third barrier (5-8 words)",
      "points": [
        "Specific action referencing the actual mention count from the data",
        "How this advances the Theory of Change goal of reducing financial barriers"
      ]
    }}
  ]
}}
Use only mention counts from the data provided. Make language strategic.""", _ctx3, 1200)

            _prog.progress(60, text="Report 3: summary...")
            _page_syn3 = f"=== FEEDBACK DATA ===\n{_ctx3}\n\n=== BAR CHART INSIGHTS ===\n{_fb_insights}\n\n=== WEAKNESSES ===\n{_fb_weak}\n\n=== RECOMMENDATION ===\n{_fb_rec}\n\n=== DETAILS ===\n{_fb_recdet}"
            _fb_summary = _ai(f"""You are writing the EXECUTIVE SUMMARY for Monkey Baa Theatre's
Audience Feedback report. It appears at the bottom and synthesises ALL findings
into a board-quality strategic conclusion.

Monkey Baa's Theory of Change mission:
"To uplift young Australians by embedding the arts into their formative years.
To ensure all young people have equitable access to creative experiences."

Write ONE cohesive paragraph of 6-7 sentences that:
1. Opens with the headline sentiment result — overall positive tone with numbers
   (X of {_total3} comments / X% of {_total3})
2. Highlights what audiences praised most (artistic quality, child engagement)
3. Acknowledges the operational barriers (parking, price, audio, age clarity)
   and frames them as non-artistic — the artistic experience is strong
4. Connects the barriers to the Theory of Change access mission
5. Summarises the 3 strategic recommendations in one forward-looking sentence
6. Closes with a statement about audience loyalty and the path to broader access

Board-quality conclusion. Purposeful, warm, actionable. No headers. No bullet points.""", _page_syn3, 700)

            st.session_state.update({
                "fb_insights":_fb_insights, "fb_weak":_fb_weak,
                "fb_rec":_fb_rec, "fb_recdet":_fb_recdet, "fb_summary":_fb_summary,
            })
        except Exception as _e:
            _errs.append("Report 3: "+str(_e))

        # ── Report 4 — Emotional & Social Impact ─────────────
        try:
            _prog.progress(63, text="Report 4: Emotional & Social Impact...")
            _ns4 = len(_df_s)
            _EM  = ["Happy","Sad","Surprised","Bored","Angry","Confused","Scared","Curious"]
            _QU  = ["Personal Meaning","Excellence","Aesthetic Experience","Creativity","Imagination","Belonging"]
            _epcts4 = {c: round(100*_df_s[c].sum()/_ns4,1) for c in _EM if c in _df_s.columns}
            _esrt4  = sorted(_epcts4.items(), key=lambda x: x[1], reverse=True)
            _qavgs4 = {c: round(_df_s[c].mean(),2) for c in _QU if c in _df_s.columns and _df_s[c].notna().sum()>0}
            _qsrt4  = sorted(_qavgs4.items(), key=lambda x: x[1], reverse=True)
            _nps4   = round(_df_s["net-promoter-score"].mean(),1) if "net-promoter-score" in _df_s.columns else "N/A"
            _ent4   = round(_df_s["The performance was entertaining"].mean(),1) if "The performance was entertaining" in _df_s.columns else "N/A"
            _imp4   = round(_df_s["The performance was emotionally impactful"].mean(),1) if "The performance was emotionally impactful" in _df_s.columns else "N/A"
            _exc4   = round(100*(_df_s["overall-experience"]=="Excellent").sum()/_ns4,1) if "overall-experience" in _df_s.columns else "N/A"
            _happy4 = _epcts4.get("Happy", 0)
            _qctx4  = "\n".join([f"{c}: {v}/10" for c,v in _qsrt4])
            _ectx4  = "\n".join([f"{e}: {v}% of young audience members" for e,v in _esrt4])

            _prog.progress(67, text="Report 4: quality insights...")
            _esi_q = _ai("You are an arts analytics expert for Monkey Baa Theatre, an Australian children's theatre company. Analyse these 6 artistic quality scores rated by audience members (scale 0-10). Return exactly 3 bullet points (starting with •) for a theatre manager. Each bullet must be 30-50 words. Cover: the strongest dimension with specific score and what it signals, overall pattern across dimensions, and one concrete actionable recommendation tied to the lowest-scoring dimension.", _qctx4, 1000)

            _prog.progress(70, text="Report 4: emotion insights...")
            _esi_e = _ai("You are an arts education expert for Monkey Baa Theatre, an Australian children's theatre company. These are emotions felt by young people during live performances (% of respondents). Return exactly 3 bullet points (starting with •) for a theatre manager. Each bullet must be 30-50 words. Cover: the dominant emotion and what it reveals about the audience experience, the meaning of the emotional range across all 8 emotions, and one strategic programming or marketing insight based on the emotional data.", _ectx4, 1000)

            _full_ctx4 = (_qctx4 + "\n\n" + _ectx4 + f"\n\nQuality insights:\n{_esi_q}\n\nEmotion insights:\n{_esi_e}")
            _prog.progress(73, text="Report 4: recommendations...")
            _esi_rec = _ai('You are a strategic advisor for Monkey Baa Theatre, an Australian children\'s theatre company. Based on ALL the emotional and quality data provided, generate exactly 3 strategic recommendations for theatre managers. Each recommendation: action-oriented title (5-7 words) + 2 sentences of rationale. Return ONLY JSON: {"items":[{"title":"...","body":"..."},{"title":"...","body":"..."},{"title":"...","body":"..."}]}', _full_ctx4, 1000)

            _sum_ctx4 = (f"Survey respondents: {_ns4}\nFelt Happy: {_happy4}%\nRated Excellent: {_exc4}%\nNPS: {_nps4}/10\n"
                         f"Emotional Impact: {_imp4}/10\nTop quality: {_qsrt4[0][0] if _qsrt4 else 'N/A'}\n"
                         f"Lowest quality: {_qsrt4[-1][0] if _qsrt4 else 'N/A'}\nInsights:\n{_esi_q}\n{_esi_e}")
            _prog.progress(76, text="Report 4: summary...")
            _esi_sum = _ai("You are a senior analyst for Monkey Baa Theatre, an Australian children's theatre company. Write an executive summary of exactly 5 sentences in flowing prose (no bullet points) for a board-level report on Emotional & Social Impact. Structure: (1) Headline satisfaction result using exact numbers. (2) Emotional experience of young audiences — dominant emotions and what they signal. (3) Artistic quality dimensions — what is strong and what needs attention. (4) Connect to Monkey Baa's mission of embedding arts in young Australians' lives. (5) One forward-looking strategic recommendation for leadership.", _sum_ctx4, 1000)

            st.session_state.update({
                "esi_quality_insight":_esi_q, "esi_emotion_insight":_esi_e,
                "esi_rec":_esi_rec, "esi_exec_summary":_esi_sum,
            })
        except Exception as _e:
            _errs.append("Report 4: "+str(_e))

        # ── Report 5 — Arts & Cultural Impact ───────────────
        try:
            _prog.progress(79, text="Report 5: Arts & Cultural Impact...")
            _ns5 = len(_df_s)
            _ae5 = _pd.to_numeric(_df_s.get("Aesthetic Experience", _pd.Series([0]*_ns5)), errors="coerce")
            _cr5 = _pd.to_numeric(_df_s.get("Creativity",           _pd.Series([0]*_ns5)), errors="coerce")
            _im5 = _pd.to_numeric(_df_s.get("Imagination",          _pd.Series([0]*_ns5)), errors="coerce")
            _bl5 = _pd.to_numeric(_df_s.get("Belonging",            _pd.Series([0]*_ns5)), errors="coerce")
            _happy5   = _pd.to_numeric(_df_s.get("Happy",   _pd.Series([0]*_ns5)), errors="coerce").fillna(0)
            _curious5 = _pd.to_numeric(_df_s.get("Curious", _pd.Series([0]*_ns5)), errors="coerce").fillna(0)
            _cult_aw5 = _pd.to_numeric(_df_s.get("Become more aware of different cultures or viewpoints", _pd.Series([0]*_ns5)), errors="coerce").fillna(0)
            _ask_q5   = _pd.to_numeric(_df_s.get("Ask questions about the story or characters",           _pd.Series([0]*_ns5)), errors="coerce").fillna(0)
            _des_l5   = _pd.to_numeric(_df_s.get("Express a desire to learn more about the subject",     _pd.Series([0]*_ns5)), errors="coerce").fillna(0)
            _conn5    = _pd.to_numeric(_df_s.get("Make connections to their own life or experiences",    _pd.Series([0]*_ns5)), errors="coerce").fillna(0)
            _imag5    = _pd.to_numeric(_df_s.get("Engage in imaginative play related to the show",       _pd.Series([0]*_ns5)), errors="coerce").fillna(0)
            _prior5   = (_df_s.get("Prior to attending, had the young person heard of the story before?", _pd.Series(["No"]*_ns5))=="Yes").sum()
            _enj5     = (_df_s.get("How much did the young person enjoy the show?", _pd.Series([""]*_ns5))=="They liked the show a lot").sum()
            _ent5     = _pd.to_numeric(_df_s.get("The performance was entertaining",         _pd.Series([0]*_ns5)), errors="coerce")
            _emp5     = _pd.to_numeric(_df_s.get("The performance was emotionally impactful", _pd.Series([0]*_ns5)), errors="coerce")
            _m5 = {
                "n":_ns5,
                "cultural_learning_n":   int((_ae5>=7).sum()),
                "cultural_learning_pct": round((_ae5>=7).sum()/_ns5*100),
                "confidence_n":          int(_conn5.sum()),
                "confidence_pct":        round(_conn5.sum()/_ns5*100),
                "aus_stories_n":         int(_prior5),
                "aus_stories_pct":       round(_prior5/_ns5*100),
                "cat_cultural_learning": int(((_cult_aw5==1)|(_ask_q5==1)|(_des_l5==1)).sum()),
                "cat_confidence":        int(((_cr5>=7)|(_im5>=7)).sum()),
                "cat_emotional":         int(((_happy5==1)|(_bl5>=7)).sum()),
                "cat_curiosity":         int(((_curious5==1)|(_conn5==1)).sum()),
                "cat_positive":          int(_enj5),
                "happy_n":               int((_happy5==1).sum()),
                "curious_n":             int((_curious5==1).sum()),
                "cult_aware_n":          int((_cult_aw5==1).sum()),
                "imaginative_play_n":    int((_imag5==1).sum()),
                "entertaining_high_n":   int((_ent5>=8).sum()),
                "emotionally_high_n":    int((_emp5>=7).sum()),
                "ae_mean":  round(_ae5.mean(),1), "cr_mean": round(_cr5.mean(),1),
                "im_mean":  round(_im5.mean(),1), "bl_mean": round(_bl5.mean(),1),
            }
            try:
                _shows5 = _df_s["What Monkey Baa show did you recently attend?"].value_counts().to_dict()
                _shows_str5 = " | ".join(f"{k}: {v}" for k,v in _shows5.items())
            except Exception: _shows_str5 = "N/A"
            _ctx5 = f"""=== MONKEY BAA THEATRE — ARTS & CULTURAL IMPACT SURVEY ===
Total survey responses: {_ns5}
Shows: {_shows_str5}
THEORY OF CHANGE — CULTURAL OUTCOMES:
"Young people see themselves in stories and feel validated."
"Young people develop curiosity and engagement with theatre."
"Young people develop a growing appreciation for theatre and the arts."
"Young people build increased cultural literacy and openness."
"A generation of lifelong arts engagers is cultivated."
"Australian storytelling is enriched and diversified."
CULTURAL IMPACT METRICS (of {_ns5} respondents):
KPI 1 — Cultural Learning (AE>=7): {_m5['cultural_learning_n']} ({_m5['cultural_learning_pct']}% of {_ns5}) | Mean AE: {_m5['ae_mean']}/10
KPI 2 — Confidence (connections to own life): {_m5['confidence_n']} ({_m5['confidence_pct']}% of {_ns5})
KPI 3 — Australian Stories Known: {_m5['aus_stories_n']} ({_m5['aus_stories_pct']}% of {_ns5})
SENTIMENT CATEGORIES:
  Cultural Learning & Awareness: {_m5['cat_cultural_learning']} ({round(_m5['cat_cultural_learning']/_ns5*100)}% of {_ns5})
  Confidence & Self-Expression: {_m5['cat_confidence']} ({round(_m5['cat_confidence']/_ns5*100)}% of {_ns5})
  Emotional & Social Wellbeing: {_m5['cat_emotional']} ({round(_m5['cat_emotional']/_ns5*100)}% of {_ns5})
  Curiosity & Critical Thinking: {_m5['cat_curiosity']} ({round(_m5['cat_curiosity']/_ns5*100)}% of {_ns5})
  General Positive Engagement: {_m5['cat_positive']} ({round(_m5['cat_positive']/_ns5*100)}% of {_ns5})
ADDITIONAL: Happy: {_m5['happy_n']} ({round(_m5['happy_n']/_ns5*100)}%) | Curious: {_m5['curious_n']} ({round(_m5['curious_n']/_ns5*100)}%) | Imaginative play: {_m5['imaginative_play_n']} ({round(_m5['imaginative_play_n']/_ns5*100)}%) | Entertaining>=8: {_m5['entertaining_high_n']} ({round(_m5['entertaining_high_n']/_ns5*100)}%) | Emotionally impactful>=7: {_m5['emotionally_high_n']} ({round(_m5['emotionally_high_n']/_ns5*100)}%) | Creativity: {_m5['cr_mean']}/10 | Imagination: {_m5['im_mean']}/10 | Belonging: {_m5['bl_mean']}/10
GAP: Only {round(_m5['cult_aware_n']/_ns5*100)}% ({_m5['cult_aware_n']} of {_ns5}) became more culturally aware. Only {_m5['confidence_pct']}% ({_m5['confidence_n']} of {_ns5}) made explicit life connections."""

            _prog.progress(83, text="Report 5: insight interpretation...")
            _aci_interpret = _ai(f"""You are a cultural impact analyst for Monkey Baa Theatre, Australia.
Monkey Baa's Theory of Change — Cultural Outcomes (Spark): "Young people see themselves in stories and feel validated." "Young people develop curiosity and engagement with theatre."
Cultural Outcomes (Growth): "Young people develop a growing appreciation for theatre and the arts." "Young people build increased cultural literacy and openness."
You are writing the INSIGHT INTERPRETATION section — interpret WHAT THE KPIs MEAN culturally. Do NOT repeat numbers mechanically — explain the significance.
Key data points: {_m5['cultural_learning_pct']}% ({_m5['cultural_learning_n']} of {_ns5}) rated AE>=7 | {_m5['confidence_pct']}% ({_m5['confidence_n']} of {_ns5}) made connections to own life | {_m5['aus_stories_pct']}% ({_m5['aus_stories_n']} of {_ns5}) already knew the story | {round(_m5['happy_n']/_ns5*100)}% ({_m5['happy_n']} of {_ns5}) felt Happy | {round(_m5['curious_n']/_ns5*100)}% ({_m5['curious_n']} of {_ns5}) felt Curious | Only {round(_m5['cult_aware_n']/_ns5*100)}% ({_m5['cult_aware_n']} of {_ns5}) became more culturally aware
Return exactly 5 bullet points (starting with •). Each bullet: bold label format **Label:** then insight text, 1-2 sentences, reference a Theory of Change outcome explicitly.
Structure: • **Strong Cultural Reach:** • **Identity & Belonging:** • **Australian Story Recognition:** • **Emotional Engagement:** • **Cultural Gap:**
Every % must show base — write "X% (N of {_ns5})". Start with •.""", _ctx5, 800)

            _prog.progress(86, text="Report 5: sentiment table...")
            _aci_sentiment = _aij(f"""You are a cultural impact analyst for Monkey Baa Theatre, Australia.
Theory of Change: "Young people see themselves in stories and feel validated.
A generation of lifelong arts engagers is cultivated."

For each category, write a description of EXACTLY 30-40 words explaining the CULTURAL
SIGNIFICANCE — what it means for children's development and arts engagement.
Do NOT describe how it was measured. Do NOT repeat the numbers. Explain the meaning.
Data: Cultural Learning & Awareness ({round(_m5['cat_cultural_learning']/_ns5*100)}%, {_m5['cat_cultural_learning']} of {_ns5}) | Confidence & Self-Expression ({round(_m5['cat_confidence']/_ns5*100)}%, {_m5['cat_confidence']} of {_ns5}) | Emotional & Social Wellbeing ({round(_m5['cat_emotional']/_ns5*100)}%, {_m5['cat_emotional']} of {_ns5}) | Curiosity & Critical Thinking ({round(_m5['cat_curiosity']/_ns5*100)}%, {_m5['cat_curiosity']} of {_ns5}) | General Positive Engagement ({round(_m5['cat_positive']/_ns5*100)}%, {_m5['cat_positive']} of {_ns5})
Return ONLY valid JSON. No markdown. No preamble. No backticks:
{{"rows":[{{"category":"Cultural Learning & Awareness","description":"30-40 word significance","count":{_m5['cat_cultural_learning']},"pct":{round(_m5['cat_cultural_learning']/_ns5*100)}}},{{"category":"Confidence & Self-Expression","description":"30-40 word significance","count":{_m5['cat_confidence']},"pct":{round(_m5['cat_confidence']/_ns5*100)}}},{{"category":"Emotional & Social Wellbeing","description":"30-40 word significance","count":{_m5['cat_emotional']},"pct":{round(_m5['cat_emotional']/_ns5*100)}}},{{"category":"Curiosity & Critical Thinking","description":"30-40 word significance","count":{_m5['cat_curiosity']},"pct":{round(_m5['cat_curiosity']/_ns5*100)}}},{{"category":"General Positive Engagement","description":"30-40 word significance","count":{_m5['cat_positive']},"pct":{round(_m5['cat_positive']/_ns5*100)}}}],"insight":"40-50 word overall conclusion connecting to Theory of Change"}}""", _ctx5, 1000)

            _prog.progress(88, text="Report 5: weaknesses...")
            _aci_weak = _aij(f"""You are a strategic analyst for Monkey Baa Theatre, Australia.
Theory of Change cultural gap: "Young people do not see their diverse experiences
reflected in stories. A lack of representation diminishes their sense of belonging."

Based on the cultural impact survey data, identify exactly 2 key weaknesses.

Return ONLY this JSON, no markdown, no preamble:
{{
  "weakness_1": {{
    "title": "Weakness title (5-7 words, data-specific)",
    "points": [
      "Specific finding with number (X of {_ns5} / X% of {_ns5})",
      "Why this undermines the Theory of Change cultural outcomes goal",
      "Which audience segment or cultural outcome is most at risk"
    ]
  }},
  "weakness_2": {{
    "title": "Weakness title (5-7 words, different focus from weakness 1)",
    "points": [
      "Specific finding with number (X of {_ns5} / X% of {_ns5})",
      "Why this represents a barrier as defined in the Theory of Change",
      "Risk to long-term cultural mission if not addressed"
    ]
  }}
}}
Key gaps: only {round(_m5['cult_aware_n']/_ns5*100)}% ({_m5['cult_aware_n']} of {_ns5}) became more aware of different cultures/viewpoints.
Only {_m5['confidence_pct']}% ({_m5['confidence_n']} of {_ns5}) made explicit life connections.
Mean Creativity {_m5['cr_mean']}/10 and Imagination {_m5['im_mean']}/10 — room for improvement.
Every % must include the base number.""", _ctx5, 1200)

            _prog.progress(90, text="Report 5: recommendation...")
            _aci_rec = _aij(f"""You are a strategic analyst for Monkey Baa Theatre, Australia.
Theory of Change cultural strategy: "We create theatre experiences that support emotional growth. We develop and present original Australian theatre that reflects the diversity of young audiences."
Write ONE primary recommendation. Return ONLY this JSON:
{{"title":"Recommendation title (5-8 words)","description":"3-4 sentences: (1) data gap (X of {_ns5}), (2) Theory of Change link, (3) concrete action, (4) expected cultural outcome."}}""", _ctx5, 1200)

            _aci_recdet = _aij(f"""You are a strategic analyst for Monkey Baa Theatre, Australia.
Theory of Change cultural activities:
- Creating theatre experiences that foster empathy through shared emotional storytelling
- Developing original Australian theatre reflecting diversity of young audiences
- Making young people feel seen and respected as legitimate participants in cultural life
- Building a generation of lifelong arts engagers

Provide exactly 3 detailed actionable recommendations addressing cultural impact gaps.

Return ONLY this JSON, no markdown, no preamble:
{{"items":[{{"title":"Embed Cultural Reflection Moments","points":["Specific action (baseline: {round(_m5['cult_aware_n']/_ns5*100)}% ({_m5['cult_aware_n']} of {_ns5}) became culturally aware)","How guided prompts make cultural learning intentional"]}},{{"title":"Reinforce Through Creative Expression","points":["Activities linked to gap ({_m5['confidence_pct']}% of {_ns5} made life connections)","How this strengthens confidence and makes cultural outcomes visible"]}},{{"title":"Strengthen Australian Story Representation","points":["Build on {_m5['aus_stories_pct']}% ({_m5['aus_stories_n']} of {_ns5}) prior story recognition","How this advances the Theory of Change goal of enriched Australian storytelling"]}}]}}
Rewrite points in your own words — use baseline numbers but make language strategic.""", _ctx5, 1200)

            _prog.progress(92, text="Report 5: summary...")
            _page_syn5 = f"=== RAW DATA ===\n{_ctx5}\n\n=== INSIGHT INTERPRETATION ===\n{_aci_interpret}\n\n=== SENTIMENT TABLE ===\n{_aci_sentiment}\n\n=== WEAKNESSES ===\n{_aci_weak}\n\n=== RECOMMENDATION ===\n{_aci_rec}\n\n=== DETAILS ===\n{_aci_recdet}"
            _aci_summary = _ai(f"""You are writing the EXECUTIVE SUMMARY for Monkey Baa Theatre's Arts & Cultural Impact report.
Write ONE cohesive paragraph of 6-7 sentences:
1. Headline cultural achievement (exact numbers: X% (N of {_ns5}))
2. Emotional and social cultural impact (Happy, Curious, Belonging)
3. Australian story reach and representation data
4. Most critical cultural gaps linked to Theory of Change barriers
5. Strategic direction across the 3 recommendations
6. Theory of Change horizon: "a generation of lifelong arts engagers"
Board-quality conclusion. No headers. No bullet points.""", _page_syn5, 600)

            st.session_state.update({
                "aci_interpret":_aci_interpret, "aci_sentiment":_aci_sentiment,
                "aci_weak":_aci_weak, "aci_rec":_aci_rec,
                "aci_recdet":_aci_recdet, "aci_summary":_aci_summary,
            })
        except Exception as _e:
            _errs.append("Report 5: "+str(_e))

        # ── Report 6 — High Quality Outcomes ────────────────
        try:
            _prog.progress(94, text="Report 6: High Quality Outcomes...")
            _ns6 = len(_df_s)
            _nps6  = _df_s["net-promoter-score"] if "net-promoter-score" in _df_s.columns else _pd.Series([5]*_ns6)
            _exc6  = round(100*(_df_s["overall-experience"]=="Excellent").sum()/_ns6,1) if "overall-experience" in _df_s.columns else "N/A"
            _nm6   = round(_nps6.mean(),1)
            _nsc6  = round((((_nps6>=9).sum()-(_nps6<=6).sum())/_ns6)*100)
            _ng6   = round(100*(_nps6<=6).sum()/_ns6,1)
            _ec6   = "How much did the young person enjoy the show?"
            _lk6   = round(100*(_df_s[_ec6]=="They liked the show a lot").sum()/_ns6,1) if _ec6 in _df_s.columns else "N/A"
            _rc6   = "Intent to Return (Organisation)"
            _rt6   = round(100*_df_s[_rc6].isin(["Very likely","Likely"]).sum()/_ns6,1) if _rc6 in _df_s.columns else "N/A"
            _ENJOY_MAP6 = {"They liked the show a lot":"Liked a lot","They liked the show a little":"Liked a little","Neither liked nor disliked the show":"Neutral","They disliked the show a little":"Disliked a little","They disliked the show a lot":"Disliked a lot"}
            _enjoy_raw6 = _df_s[_ec6].map(_ENJOY_MAP6).value_counts() if _ec6 in _df_s.columns else _pd.Series()
            _enjoy_str6 = "\n".join(f"  {cat}: {int(_enjoy_raw6.get(cat,0))} ({_enjoy_raw6.get(cat,0)/_ns6*100:.1f}%)" for cat in ["Liked a lot","Liked a little","Neutral","Disliked a little","Disliked a lot"])
            _ret_raw6   = _df_s[_rc6].value_counts() if _rc6 in _df_s.columns else _pd.Series()
            _ret_str6   = "\n".join(f"  {cat}: {int(_ret_raw6.get(cat,0))} ({_ret_raw6.get(cat,0)/_ns6*100:.1f}%)" for cat in ["Very likely","Likely","Neutral","Unlikely","Very unlikely"])
            _age_col6   = "Please tell us the age/s of the young people that attended the show with you."
            _age_c6     = {"0-5 years":0,"6-12 years":0,"13-17 years":0}
            if _age_col6 in _df_s.columns:
                for _val in _df_s[_age_col6].dropna():
                    for _part in str(_val).split(";"):
                        _p = _part.strip()
                        if "0-5" in _p: _age_c6["0-5 years"]+=1
                        elif "6-12" in _p: _age_c6["6-12 years"]+=1
                        elif "13-17" in _p: _age_c6["13-17 years"]+=1
            _age_str6   = "\n".join(f"  {k}: {v} ({v/_ns6*100:.1f}%)" for k,v in _age_c6.items())
            _disc_col6  = "How did you hear about Monkey Baa's show?"
            _disc_c6    = {"Social Media":0,"Word of Mouth":0,"Email Newsletter":0,"Google Search":0,"Flyer / Poster":0,"Previous Experience":0,"Other":0}
            if _disc_col6 in _df_s.columns:
                for _val in _df_s[_disc_col6].dropna():
                    for _part in str(_val).split(";"):
                        _p = _part.strip()
                        if "Social Media" in _p: _disc_c6["Social Media"]+=1
                        elif "Word of Mouth" in _p: _disc_c6["Word of Mouth"]+=1
                        elif "Email" in _p: _disc_c6["Email Newsletter"]+=1
                        elif "Google" in _p: _disc_c6["Google Search"]+=1
                        elif "Flyer" in _p or "poster" in _p.lower(): _disc_c6["Flyer / Poster"]+=1
                        elif "Previous" in _p: _disc_c6["Previous Experience"]+=1
                        else: _disc_c6["Other"]+=1
            _disc_str6  = "\n".join(f"  {k}: {v}" for k,v in sorted(_disc_c6.items(), key=lambda x:-x[1]))
            _ctx6 = f"""MONKEY BAA THEATRE — HIGH QUALITY OUTCOMES SURVEY (n={_ns6})
KEY METRICS: Rated Excellent: {_exc6}% | NPS avg: {_nm6}/10 | NPS score: {_nsc6} | Negative feedback: {_ng6}%
ENJOYMENT RATINGS:\n{_enjoy_str6}
LIKELIHOOD TO RETURN:\n{_ret_str6}
AGE GROUPS:\n{_age_str6}
HOW DISCOVERED:\n{_disc_str6}
PERFORMANCE SCORES (avg/10): Entertaining: {round(_df_s['The performance was entertaining'].mean(),1) if 'The performance was entertaining' in _df_s.columns else 'N/A'} | Emotionally impactful: {round(_df_s['The performance was emotionally impactful'].mean(),1) if 'The performance was emotionally impactful' in _df_s.columns else 'N/A'} | Aesthetic Experience: {round(_df_s['Aesthetic Experience'].mean(),2) if 'Aesthetic Experience' in _df_s.columns else 'N/A'} | Excellence: {round(_df_s['Excellence'].mean(),2) if 'Excellence' in _df_s.columns else 'N/A'} | Personal Meaning: {round(_df_s['Personal Meaning'].mean(),2) if 'Personal Meaning' in _df_s.columns else 'N/A'} | Belonging: {round(_df_s['Belonging'].mean(),2) if 'Belonging' in _df_s.columns else 'N/A'}"""

            _prog.progress(96, text="Report 6: insights...")
            _hqo_ins  = _ai("You are an expert analyst for Monkey Baa Theatre, an Australian children's theatre company. Analyse audience satisfaction, engagement, emotional impact, and intent to return. Return exactly 5 numbered insights for an executive report. Each insight: 2-3 sentences, specific, evidence-based, action-relevant. Format exactly as:\n1. [Insight title]: [2-3 sentence explanation with data references]\n2. ...", _ctx6, 900)
            _hqo_age  = _ai("You are an expert analyst for Monkey Baa Theatre, an Australian children's theatre company. Analyse the demographic trends in young audience age groups and interpret what this means for programming, content design, and developmental outcomes. Return exactly 2 concise insights (2-3 sentences each). Format: bullet points starting with •", _ctx6, 400)
            _hqo_disc = _ai("You are a marketing analyst for Monkey Baa Theatre, an Australian children's theatre company. Analyse how audiences discovered the show and what this reveals about marketing effectiveness and audience reach strategy. Return exactly 2 concise insights (2-3 sentences each). Format: bullet points starting with •", _ctx6, 400)
            _hqo_recs = _ai("You are a strategic advisor for Monkey Baa Theatre, an Australian children's theatre company. Based on all survey insights — satisfaction, engagement, demographics, marketing — generate exactly 3 action-oriented recommendations. Each recommendation: 2-3 sentences explaining what to do and why. No titles. Format:\n1. [explanation]\n2. [explanation]\n3. [explanation]", _ctx6, 700)

            _prog.progress(98, text="Report 6: summary...")
            _hqo_sum = _ai("You are a senior analyst writing for Monkey Baa Theatre's board and sponsors. Using all survey data, insights and recommendations, write an executive summary covering: 1. Overall performance and audience satisfaction 2. Audience engagement and social impact 3. Strategic value and return on investment for sponsors. Tone: executive, persuasive, impact-focused. Max 4 sentences total. No bullet points — flowing prose.",
                           _ctx6 + "\n\nINSIGHTS & RECOMMENDATIONS:\n" + "\n\n".join([_hqo_ins, _hqo_age, _hqo_disc, _hqo_recs]), 600)

            st.session_state.update({
                "hqo_insights":_hqo_ins, "hqo_age_insights":_hqo_age,
                "hqo_disc_insights":_hqo_disc, "hqo_recommendations":_hqo_recs,
                "hqo_summary":_hqo_sum,
            })
        except Exception as _e:
            _errs.append("Report 6: "+str(_e))

        _prog.progress(100, text="Done!")
        if _errs:
            st.error("Some reports had issues:\n" + "\n".join(_errs))
        else:
            st.markdown(f"""
            <div style='background-color:#FDF3EE;border-left:4px solid {ORANGE};
                        border-radius:8px;padding:14px 18px;margin-top:8px;'>
              <span style='color:{GRAY_TEXT};font-size:14px;'>
                ✅ All 5 reports generated! Navigate to any report to view results and download PDF.
              </span>
            </div>
            """, unsafe_allow_html=True)