"""
pages/1_Overview.py
====================
Executive Overview — summary of all 5 reports
Uses: df_audience + df_survey from session_state (loaded once in app.py)
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import streamlit as st

# ── Colour palette (matches all other pages) ─────────────────────────────────
ORANGE      = "#E8673A"
ORANGE_DARK = "#C4512A"
BEIGE       = "#F5F0EA"
WHITE       = "#FFFFFF"
GRAY_TEXT   = "#555555"
TEAL_DARK   = "#1F4A4E"

# ── CSS — exact copy of page 2 pattern ───────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;1,400&display=swap');
  .stApp {{ background-color: {BEIGE}; }}
  [data-testid="stSidebar"] {{ background-color: {TEAL_DARK} !important; }}
  [data-testid="stSidebar"] * {{ color: #ffffff !important; }}
  [data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.2) !important; }}

  /* KPI cards */
  .kpi-card {{
    background-color:{ORANGE}; border-radius:12px;
    padding:14px 12px; text-align:center; color:white;
    height:100%;
  }}
  .kpi-label {{ font-size:11px; font-weight:500; opacity:.85; margin-bottom:3px; }}
  .kpi-value {{ font-size:26px; font-weight:700; line-height:1.1; }}
  .kpi-sub   {{ font-size:10px; opacity:.82; margin-top:3px; }}

  /* White cards */
  .card {{
    background-color:{WHITE}; border-radius:12px;
    padding:16px 20px; margin-bottom:12px;
  }}

  /* Insight / summary box */
  .insight-box {{
    background-color:#FDF3EE; border-radius:10px;
    padding:14px 16px; color:{GRAY_TEXT};
    font-size:13px; line-height:1.7;
  }}
  .insight-box ul {{ margin:0; padding-left:16px; }}
  .insight-box li {{ margin-bottom:6px; }}

  /* Summary text box */
  .summary-box {{
    background-color:{WHITE}; border-radius:10px;
    padding:14px 18px; color:{GRAY_TEXT};
    font-size:13px; line-height:1.7;
    border-left:4px solid {ORANGE};
  }}

  /* Section heading with orange underline — same as page 2 section-title */
  .section-title {{
    font-size:14px; font-weight:600; color:{ORANGE_DARK};
    margin-bottom:8px; text-decoration:underline;
  }}

  /* Report section block title */
  .report-block-title {{
    font-size:16px; font-weight:700; color:#222;
    margin-bottom:2px;
  }}
  .report-block-sub {{
    font-size:11px; color:#999; letter-spacing:.8px;
    text-transform:uppercase; margin-bottom:12px;
  }}

  /* Divider */
  hr.div {{ border:none; border-top:1px solid #e0d8d0; margin:6px 0 16px 0; }}
  hr.section-div {{
    border:none; border-top:1px solid #e0d8d0;
    margin:28px 0 22px 0;
  }}

  /* Placeholder */
  .ph {{ color:#bbb; font-style:italic; font-size:13px; }}

  /* Override Streamlit warning/info text to black */
  [data-testid="stAlert"] {{ color: #111 !important; }}
  [data-testid="stAlert"] p {{ color: #111 !important; }}
  [data-testid="stAlert"] a {{ color: #111 !important; }}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
df_aud  = st.session_state.get("df_audience", None)
df_surv = st.session_state.get("df_survey",   None)

# ── Header ────────────────────────────────────────────────────────────────────
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown("""
    <div style='padding:4px 0'>
      <div style='font-size:11px;color:#999;letter-spacing:1px;text-transform:uppercase;'>
        Monkey Baa Theatre
      </div>
      <div style='font-size:20px;font-weight:700;color:#333;line-height:1.3;'>
        Executive Overview:
        <span style='color:#E8673A;'> Program Impact Summary </span>
      </div>
    </div>""", unsafe_allow_html=True)
with h2:
    st.markdown("""<div style='text-align:right;padding-top:8px;font-size:24px;
                    font-weight:400;color:#000000;font-style:normal !important;
                    font-family:"Playfair Display",Georgia,serif;
                    letter-spacing:0.5px;white-space:nowrap;'>
                    <span style='font-style:normal !important;'>monkey baa</span>
                    </div>""",
                unsafe_allow_html=True)

st.markdown("<hr class='div'>", unsafe_allow_html=True)

# ── Guard ─────────────────────────────────────────────────────────────────────
missing = []
if df_aud  is None: missing.append("**Audience_final_data.csv**")
if df_surv is None: missing.append("**Survey CSV**")
if missing:
    st.warning(f"⬅️ Please upload {' and '.join(missing)} in the sidebar on the Home page first.")
    st.stop()

# ── Prepare audience data ─────────────────────────────────────────────────────
df_a = df_aud.copy()
df_a.columns = df_a.columns.str.strip()
df_a["Audience_n"] = pd.to_numeric(df_a["Audience_n"], errors="coerce")

total_audience = int(df_a["Audience_n"].sum())
total_events   = int(pd.to_numeric(df_a["# of events"], errors="coerce").sum())
regional_n     = int(df_a[df_a["Regional II"] == "Regional"]["Audience_n"].sum())
regional_pct   = round(regional_n / total_audience * 100, 1) if total_audience else 0
remote_n       = int(df_a[df_a["Regional II"] == "Remote"]["Audience_n"].sum())
remote_pct     = round(remote_n / total_audience * 100, 1)   if total_audience else 0
top_state      = df_a.groupby("State")["Audience_n"].sum().idxmax()
top_state_n    = int(df_a.groupby("State")["Audience_n"].sum().max())
n_states       = df_a["State"].nunique()
yearly         = df_a.groupby("Year")["Audience_n"].sum()
peak_year      = int(yearly.idxmax())
peak_n         = int(yearly.max())

# ── Prepare survey data ───────────────────────────────────────────────────────
df_s = df_surv.copy()
df_s.columns = df_s.columns.str.strip()
ns = len(df_s)

for col in ["net-promoter-score", "The performance was entertaining",
            "The performance was emotionally impactful",
            "Personal Meaning", "Excellence", "Aesthetic Experience",
            "Creativity", "Imagination", "Belonging"]:
    if col in df_s.columns:
        df_s[col] = pd.to_numeric(df_s[col], errors="coerce")

# Satisfaction
pct_excellent  = round(100 * (df_s["overall-experience"] == "Excellent").sum() / ns, 1) if "overall-experience" in df_s.columns else "N/A"
nps_raw        = df_s["net-promoter-score"] if "net-promoter-score" in df_s.columns else None
nps_mean       = round(nps_raw.mean(), 1)   if nps_raw is not None else "N/A"
pct_negative   = round(100 * (nps_raw <= 6).sum() / ns, 1) if nps_raw is not None else "N/A"

# Emotional
EMOTION_COLS = ["Happy","Sad","Surprised","Bored","Angry","Confused","Scared","Curious"]
for c in EMOTION_COLS:
    if c in df_s.columns:
        df_s[c] = pd.to_numeric(df_s[c], errors="coerce").fillna(0)
pct_happy      = round(100 * df_s["Happy"].sum() / ns, 1) if "Happy" in df_s.columns else "N/A"
impact_score   = round(df_s["The performance was emotionally impactful"].mean(), 1) if "The performance was emotionally impactful" in df_s.columns else "N/A"
ent_score      = round(df_s["The performance was entertaining"].mean(), 1)          if "The performance was entertaining" in df_s.columns else "N/A"

# Quality metrics
QUALITY_COLS = ["Personal Meaning","Excellence","Aesthetic Experience","Creativity","Imagination","Belonging"]
quality_avgs = {c: round(df_s[c].mean(), 2) for c in QUALITY_COLS if c in df_s.columns and df_s[c].notna().sum() > 0}
quality_sorted = sorted(quality_avgs.items(), key=lambda x: x[1], reverse=True)
top_quality = quality_sorted[0]  if quality_sorted else ("N/A", 0)
low_quality = quality_sorted[-1] if quality_sorted else ("N/A", 0)

# Return intent
return_col = "Intent to Return (Organisation)"
pct_return = round(100 * df_s[return_col].isin(["Very likely","Likely"]).sum() / ns, 1) if return_col in df_s.columns else "N/A"

# Age groups
age_col    = "Please tell us the age/s of the young people that attended the show with you."
age_counts = {"0-5 years": 0, "6-12 years": 0, "13-17 years": 0}
if age_col in df_s.columns:
    for val in df_s[age_col].dropna():
        for part in str(val).split(";"):
            part = part.strip()
            if "0-5"   in part: age_counts["0-5 years"]   += 1
            if "6-12"  in part: age_counts["6-12 years"]  += 1
            if "13-17" in part: age_counts["13-17 years"] += 1
top_age = max(age_counts, key=age_counts.get)
top_age_n = age_counts[top_age]

# Discovery
disc_col = "How did you hear about Monkey Baa's show?"
social_n = 0
if disc_col in df_s.columns:
    for val in df_s[disc_col].dropna():
        if "Social Media" in str(val) or "Facebook" in str(val) or "Instagram" in str(val):
            social_n += 1
social_pct = round(100 * social_n / ns, 1) if ns else 0

# Enjoyment
enjoy_col   = "How much did the young person enjoy the show?"
pct_liked   = round(100 * (df_s[enjoy_col] == "They liked the show a lot").sum() / ns, 1) if enjoy_col in df_s.columns else "N/A"

def ph(msg):
    return f"<div class='ph'>{msg}</div>"

# ── Session keys from each individual report ──────────────────────────────────
# These match the exact keys each report stores its summary under
REPORT_KEYS = {
    "aar": "ar_summary",        # 2_Access_and_Audience_Reach.py
    "af":  "fb_summary",         # 3_Audience_Feedback.py
    "esi": "esi_exec_summary",  # 5_Emotional_and_Social_Impact.py
    "aci": "aci_summary",       # 5_Arts_Cultural_Impact.py
    "hqo": "hqo_summary",       # 6_High_Quality_Outcomes.py
}

# ── Retrieve summaries generated by each report ───────────────────────────────
sum_aar = st.session_state.get(REPORT_KEYS["aar"], None)
sum_af  = st.session_state.get(REPORT_KEYS["af"],  None)
sum_esi = st.session_state.get(REPORT_KEYS["esi"], None)
sum_aci = st.session_state.get(REPORT_KEYS["aci"], None)
sum_hqo = st.session_state.get(REPORT_KEYS["hqo"], None)

# ── Check which reports have been run ────────────────────────────────────────
reports_done  = [k for k, v in REPORT_KEYS.items() if st.session_state.get(v)]
reports_total = len(REPORT_KEYS)
reports_pending = [
    ("Access & Audience Reach",   REPORT_KEYS["aar"], sum_aar),
    ("Audience Feedback",         REPORT_KEYS["af"],  sum_af),
    ("Emotional & Social Impact", REPORT_KEYS["esi"], sum_esi),
    ("Arts & Cultural Impact",    REPORT_KEYS["aci"], sum_aci),
    ("High Quality Outcomes",     REPORT_KEYS["hqo"], sum_hqo),
]

# ── Status banner ─────────────────────────────────────────────────────────────
if len(reports_done) == reports_total:
    st.success(f"✅ All {reports_total} reports have been run — summaries loaded below.")
elif len(reports_done) == 0:
    st.warning(
        "⬅️ No report summaries found yet. "
        "Please open and run **Generate AI Insights** on each of the 5 reports first, "
        "then return to this page."
    )
else:
    missing_names = [name for name, key, val in reports_pending if not val]
    st.info(
        f"📊 {len(reports_done)} of {reports_total} reports completed. "
        f"Still pending: **{', '.join(missing_names)}**. "
        f"Run those reports first to see their summaries here."
    )

PH_TEXT = "Run this report first — open it from the left menu and click <b>Generate AI Insights</b>."

# ── Helper: render a KPI row ──────────────────────────────────────────────────
def kpi_row(items):
    cols = st.columns(3)
    for col, (label, value, sub) in zip(cols, items):
        with col:
            st.markdown(f"""
            <div class='kpi-card'>
              <div class='kpi-label'>{label}</div>
              <div class='kpi-value'>{value}</div>
              <div class='kpi-sub'>{sub}</div>
            </div>""", unsafe_allow_html=True)

# ── Helper: render section header ─────────────────────────────────────────────
def section_header(number, title, subtitle):
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:14px;margin-bottom:6px;'>
      <div style='background:{ORANGE};color:white;border-radius:10px;width:34px;height:34px;
                  display:flex;align-items:center;justify-content:center;
                  font-size:14px;font-weight:700;flex-shrink:0;'>{number}</div>
      <div>
        <div class='report-block-title'>{title}</div>
        <div class='report-block-sub'>{subtitle}</div>
      </div>
    </div>""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Access & Audience Reach
# ═════════════════════════════════════════════════════════════════════════════
section_header("1", "Access & Audience Reach", "Geographic reach · Audience scale · Regional equity")

kpi_row([
    ("Total Young People Reached",  f"{total_audience:,}",      f"across {total_events:,} performances"),
    ("Regional Audience",           f"{regional_pct:.0f}%",     f"{regional_n:,} of {total_audience:,}"),
    ("Peak Year Audience",          f"{peak_n:,}",              f"in {peak_year} · {n_states} states covered"),
])

st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Summary</div>", unsafe_allow_html=True)
st.markdown(
    f"<div class='summary-box'>{sum_aar}</div>" if sum_aar
    else f"<div class='summary-box'><span class='ph'>{PH_TEXT}</span></div>",
    unsafe_allow_html=True
)

st.markdown("<hr class='section-div'>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Audience Feedback
# ═════════════════════════════════════════════════════════════════════════════
section_header("2", "Audience Feedback", "Satisfaction · NPS · Intent to return")

kpi_row([
    ("Rated Experience Excellent", f"{pct_excellent}%",  f"n = {ns:,} respondents"),
    ("Net Promoter Score",         f"{nps_mean}/10",     "average score"),
    ("Intent to Return",           f"{pct_return}%",     "Very likely + Likely"),
])

st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Summary</div>", unsafe_allow_html=True)
st.markdown(
    f"<div class='summary-box'>{sum_af}</div>" if sum_af
    else f"<div class='summary-box'><span class='ph'>{PH_TEXT}</span></div>",
    unsafe_allow_html=True
)

st.markdown("<hr class='section-div'>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Emotional & Social Impact
# ═════════════════════════════════════════════════════════════════════════════
section_header("3", "Emotional & Social Impact", "Emotional responses · Artistic quality · Social value")

kpi_row([
    ("Young People Felt Happy",    f"{pct_happy}%",           "Top emotional response"),
    ("Emotional Impact Score",     f"{impact_score}/10",      f"Entertainment: {ent_score}/10"),
    ("Top Quality Dimension",      f"{top_quality[1]}/10",    top_quality[0]),
])

st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Summary</div>", unsafe_allow_html=True)
st.markdown(
    f"<div class='summary-box'>{sum_esi}</div>" if sum_esi
    else f"<div class='summary-box'><span class='ph'>{PH_TEXT}</span></div>",
    unsafe_allow_html=True
)

st.markdown("<hr class='section-div'>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Arts & Cultural Impact
# ═════════════════════════════════════════════════════════════════════════════
section_header("4", "Arts & Cultural Impact", "Cultural reach · Age demographics · Artistic depth")

kpi_row([
    ("Top Artistic Dimension",     f"{top_quality[1]}/10",    top_quality[0]),
    ("Lowest Artistic Dimension",  f"{low_quality[1]}/10",    low_quality[0]),
    ("Primary Age Group",          top_age,                   f"{top_age_n:,} mentions in survey"),
])

st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Summary</div>", unsafe_allow_html=True)
st.markdown(
    f"<div class='summary-box'>{sum_aci}</div>" if sum_aci
    else f"<div class='summary-box'><span class='ph'>{PH_TEXT}</span></div>",
    unsafe_allow_html=True
)

st.markdown("<hr class='section-div'>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 5 — High Quality Outcomes
# ═════════════════════════════════════════════════════════════════════════════
section_header("5", "High Quality Outcomes", "Satisfaction · Engagement · Sponsor value")

promoters  = int((df_s["net-promoter-score"] >= 9).sum()) if nps_raw is not None else 0
detractors = int((df_s["net-promoter-score"] <= 6).sum()) if nps_raw is not None else 0
nps_score  = round((promoters - detractors) / ns * 100)   if ns else 0

kpi_row([
    ("Rated the Show Excellent",   f"{pct_excellent}%",        f"n = {ns:,} respondents"),
    ("NPS Score",                  f"{nps_score}",             f"avg {nps_mean}/10"),
    ("Social Media Discovery",     f"{social_pct}%",           "primary discovery channel"),
])

st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Summary</div>", unsafe_allow_html=True)
st.markdown(
    f"<div class='summary-box'>{sum_hqo}</div>" if sum_hqo
    else f"<div class='summary-box'><span class='ph'>{PH_TEXT}</span></div>",
    unsafe_allow_html=True
)

st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# DOWNLOAD PDF
# ═════════════════════════════════════════════════════════════════════════════
if any([sum_aar, sum_af, sum_esi, sum_aci, sum_hqo]):
    st.divider()

    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, HRFlowable
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

    def generate_overview_pdf(
        total_audience, total_events, regional_pct, regional_n,
        peak_n, peak_year, n_states,
        pct_excellent, ns, nps_mean, pct_return,
        pct_happy, impact_score, ent_score, top_quality,
        top_quality_val, low_quality, low_quality_val, top_age, top_age_n,
        nps_score, social_pct,
        sum_aar, sum_af, sum_esi, sum_aci, sum_hqo,
    ):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                                topMargin=0.4*inch, bottomMargin=0.4*inch,
                                leftMargin=0.6*inch, rightMargin=0.6*inch)
        story = []
        styles = getSampleStyleSheet()

        # ── Styles ──────────────────────────────────────────────────────────
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22,
                                     textColor=colors.HexColor('#222222'), spaceAfter=2,
                                     spaceBefore=0, fontName='Helvetica-Bold')
        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Heading2'], fontSize=13,
                                        textColor=colors.HexColor('#E8673A'), spaceAfter=8,
                                        spaceBefore=0, fontName='Helvetica-Bold')
        section_num_style = ParagraphStyle('SecNum', parent=styles['Normal'], fontSize=13,
                                           textColor=colors.white, alignment=TA_CENTER,
                                           fontName='Helvetica-Bold')
        section_title_style = ParagraphStyle('SecTitle', parent=styles['Normal'], fontSize=13,
                                             textColor=colors.HexColor('#222222'),
                                             fontName='Helvetica-Bold', spaceAfter=1)
        section_sub_style = ParagraphStyle('SecSub', parent=styles['Normal'], fontSize=8,
                                           textColor=colors.HexColor('#999999'),
                                           spaceAfter=6)
        kpi_style = ParagraphStyle('KPI', parent=styles['Normal'], fontSize=10,
                                   textColor=colors.white, alignment=TA_CENTER,
                                   fontName='Helvetica-Bold', leading=14)
        label_style = ParagraphStyle('Label', parent=styles['Normal'], fontSize=9,
                                     textColor=colors.HexColor('#333333'),
                                     fontName='Helvetica-Bold', spaceAfter=3)
        body_style = ParagraphStyle('Body', parent=styles['BodyText'], fontSize=9,
                                    textColor=colors.HexColor('#555555'), spaceAfter=4,
                                    leading=12, alignment=TA_JUSTIFY)
        footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7,
                                      textColor=colors.HexColor('#999999'),
                                      alignment=TA_CENTER)

        PH = "Run this report first to see its summary."

        # ── Helper: section header row ───────────────────────────────────────
        def section_header_pdf(number, title, subtitle):
            num_cell = Paragraph(number, section_num_style)
            num_tbl  = Table([[num_cell]], colWidths=[0.34*inch], rowHeights=[0.34*inch])
            num_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,0), colors.HexColor('#E8673A')),
                ('ALIGN',      (0,0), (0,0), 'CENTER'),
                ('VALIGN',     (0,0), (0,0), 'MIDDLE'),
                ('ROUNDEDCORNERS', [5]),
            ]))
            title_cell = [
                Paragraph(title,    section_title_style),
                Paragraph(subtitle, section_sub_style),
            ]
            hdr_tbl = Table([[num_tbl, title_cell]], colWidths=[0.5*inch, 6.3*inch])
            hdr_tbl.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING',  (1,0), (1,0), 10),
                ('BOTTOMPADDING',(0,0),(-1,-1), 0),
                ('TOPPADDING',   (0,0),(-1,-1), 0),
            ]))
            return hdr_tbl

        # ── Helper: KPI row ──────────────────────────────────────────────────
        def kpi_row_pdf(items):
            cells = []
            for label, value, sub in items:
                cells.append(Paragraph(
                    f"<b>{label}</b><br/>{value}<br/><font size='7'>{sub}</font>",
                    kpi_style))
            tbl = Table([cells], colWidths=[2*inch, 2*inch, 2*inch])
            tbl.setStyle(TableStyle([
                ('BACKGROUND',    (0,0), (-1,-1), colors.HexColor('#E8673A')),
                ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
                ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 12),
                ('TOPPADDING',    (0,0), (-1,-1), 12),
                ('INNERGRID',     (0,0), (-1,-1), 0.5, colors.HexColor('#C4512A')),
            ]))
            return tbl

        # ── Helper: summary box ──────────────────────────────────────────────
        def summary_box_pdf(text):
            clean = text.replace("<br>", " ").replace("<br/>", " ").replace("&amp;", "&") if text else PH
            p = Paragraph(clean, body_style)
            tbl = Table([[p]], colWidths=[6.3*inch])
            tbl.setStyle(TableStyle([
                ('BACKGROUND',   (0,0), (0,0), colors.HexColor('#FFFFFF')),
                ('LEFTPADDING',  (0,0), (0,0), 10),
                ('RIGHTPADDING', (0,0), (0,0), 10),
                ('TOPPADDING',   (0,0), (0,0), 10),
                ('BOTTOMPADDING',(0,0), (0,0), 10),
                ('LINEBEFORE',   (0,0), (0,0), 3, colors.HexColor('#E8673A')),
                ('BOX',          (0,0), (0,0), 0.5, colors.HexColor('#e0d8d0')),
                ('ROUNDEDCORNERS', [4]),
            ]))
            return tbl

        # ── HEADER ──────────────────────────────────────────────────────────
        story.append(Paragraph("MONKEY BAA THEATRE", title_style))
        story.append(Paragraph(
            "Executive Overview: <font color='#E8673A'>Program Impact Summary 2021–2025</font>",
            subtitle_style))
        story.append(Spacer(1, 0.1*inch))

        # ── SECTION 1 ────────────────────────────────────────────────────────
        story.append(section_header_pdf("1", "Access & Audience Reach",
                                        "Geographic reach · Audience scale · Regional equity"))
        story.append(Spacer(1, 0.1*inch))
        story.append(kpi_row_pdf([
            ("Total Young People Reached", f"{total_audience:,}",   f"across {total_events:,} performances"),
            ("Regional Audience",          f"{regional_pct:.0f}%",  f"{regional_n:,} of {total_audience:,}"),
            ("Peak Year Audience",         f"{peak_n:,}",           f"in {peak_year} · {n_states} states covered"),
        ]))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("Summary", label_style))
        story.append(summary_box_pdf(sum_aar))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e0d8d0'),
                                spaceAfter=12, spaceBefore=16))

        # ── SECTION 2 ────────────────────────────────────────────────────────
        story.append(section_header_pdf("2", "Audience Feedback",
                                        "Satisfaction · NPS · Intent to return"))
        story.append(Spacer(1, 0.1*inch))
        story.append(kpi_row_pdf([
            ("Rated Experience Excellent", f"{pct_excellent}%", f"n = {ns:,} respondents"),
            ("Net Promoter Score",         f"{nps_mean}/10",    "average score"),
            ("Intent to Return",           f"{pct_return}%",    "Very likely + Likely"),
        ]))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("Summary", label_style))
        story.append(summary_box_pdf(sum_af))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e0d8d0'),
                                spaceAfter=12, spaceBefore=16))

        # ── SECTION 3 ────────────────────────────────────────────────────────
        story.append(section_header_pdf("3", "Emotional & Social Impact",
                                        "Emotional responses · Artistic quality · Social value"))
        story.append(Spacer(1, 0.1*inch))
        story.append(kpi_row_pdf([
            ("Young People Felt Happy",  f"{pct_happy}%",        "Top emotional response"),
            ("Emotional Impact Score",   f"{impact_score}/10",   f"Entertainment: {ent_score}/10"),
            ("Top Quality Dimension",    f"{top_quality_val}/10", top_quality),
        ]))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("Summary", label_style))
        story.append(summary_box_pdf(sum_esi))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e0d8d0'),
                                spaceAfter=12, spaceBefore=16))

        # ── SECTION 4 ────────────────────────────────────────────────────────
        story.append(section_header_pdf("4", "Arts & Cultural Impact",
                                        "Cultural reach · Age demographics · Artistic depth"))
        story.append(Spacer(1, 0.1*inch))
        story.append(kpi_row_pdf([
            ("Top Artistic Dimension",    f"{top_quality_val}/10", top_quality),
            ("Lowest Artistic Dimension", f"{low_quality_val}/10", low_quality),
            ("Primary Age Group",         top_age,                 f"{top_age_n:,} mentions in survey"),
        ]))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("Summary", label_style))
        story.append(summary_box_pdf(sum_aci))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e0d8d0'),
                                spaceAfter=12, spaceBefore=16))

        # ── SECTION 5 ────────────────────────────────────────────────────────
        story.append(section_header_pdf("5", "High Quality Outcomes",
                                        "Satisfaction · Engagement · Sponsor value"))
        story.append(Spacer(1, 0.1*inch))
        story.append(kpi_row_pdf([
            ("Rated the Show Excellent", f"{pct_excellent}%",  f"n = {ns:,} respondents"),
            ("NPS Score",                f"{nps_score}",       f"avg {nps_mean}/10"),
            ("Social Media Discovery",   f"{social_pct}%",     "primary discovery channel"),
        ]))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("Summary", label_style))
        story.append(summary_box_pdf(sum_hqo))

        # ── FOOTER ───────────────────────────────────────────────────────────
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            "Report generated by Monkey Baa Theatre AI Reporting System",
            footer_style))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    pdf_bytes = generate_overview_pdf(
        total_audience, total_events, regional_pct, regional_n,
        peak_n, peak_year, n_states,
        pct_excellent, ns, nps_mean, pct_return,
        pct_happy, impact_score, ent_score,
        top_quality[0], top_quality[1],
        low_quality[0], low_quality[1],
        top_age, top_age_n,
        nps_score, social_pct,
        sum_aar, sum_af, sum_esi, sum_aci, sum_hqo,
    )
    st.download_button(
        "📄 Download Report (.pdf)",
        data=pdf_bytes,
        file_name="overview_impact_summary.pdf",
        mime="application/pdf"
    )