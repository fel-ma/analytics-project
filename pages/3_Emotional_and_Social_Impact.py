"""
pages/5_Emotional_and_Social_Impact.py
=======================================
Report: Emotional & Social Impact
Uses: Data_survey.csv via st.session_state["df_survey"]
Design: follows 2_Access_and_Audience_Reach.py style exactly
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from openai import OpenAI

# ── Colours (match page 2) ────────────────────────────────
ORANGE      = "#E8673A"
ORANGE_DARK = "#C4512A"
BEIGE       = "#F5F0EA"
WHITE       = "#FFFFFF"
GRAY_TEXT   = "#555555"

# ─────────────────────────────────────────────────────────
# Sidebar Title
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### AI Reporting System")
    st.divider()

# ── Styles — exact copy of page 2 pattern ────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;1,400&display=swap');
  .stApp {{ background-color: {BEIGE}; }}
  [data-testid="stSidebarCollapseButton"] {{ display: none !important; }}
  [data-testid="stHeader"] {{ display: none !important; }}
  [data-testid="stSidebar"] {{ background-color: #1F4A4E !important; }}
      [data-testid="stSidebar"] * {{ color: #ffffff !important; }}
  [data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.2) !important; }}
  .kpi-card {{ background-color:{ORANGE};border-radius:12px;padding:14px 12px;
               text-align:center;color:white; }}
  .kpi-label {{ font-size:11px;font-weight:500;opacity:.85;margin-bottom:3px; }}
  .kpi-value {{ font-size:28px;font-weight:700;line-height:1.1; }}
  .card {{ background-color:{WHITE};border-radius:12px;padding:16px 20px;margin-bottom:12px; }}
  .insight-box {{ background-color:#FDF3EE;border-radius:10px;padding:14px 16px;
                  color:#111;font-size:13px;line-height:1.6; }}
  .insight-box ul {{ margin:0;padding-left:16px; }}
  .insight-box li {{ margin-bottom:7px;color:#111; }}
  .section-title {{ font-size:14px;font-weight:600;color:{ORANGE_DARK};
                    margin-bottom:8px;text-decoration:underline; }}
  .summary-box {{ background-color:{WHITE};border-radius:12px;padding:16px 20px;
                  color:#111;font-size:13px;line-height:1.7; }}
  hr.div {{ border:none;border-top:1px solid #e0d8d0;margin:6px 0 12px 0; }}

  /* Progress bars for quality metrics */
  .progress-row {{ display:flex;align-items:center;margin-bottom:10px;gap:10px; }}
  .progress-label {{ width:150px;font-size:12px;color:#111;flex-shrink:0;font-weight:500; }}
  .progress-bar-bg {{ flex:1;background:#F0EBE3;border-radius:20px;height:12px;overflow:hidden; }}
  .progress-bar-fill {{ height:100%;border-radius:20px;
                        background:linear-gradient(90deg,{ORANGE},{ORANGE_DARK}); }}
  .progress-pct {{ width:38px;font-size:12px;color:#111;text-align:right;
                   flex-shrink:0;font-weight:600; }}

  /* Recommendation cards */
    .rec-card {{ background:{WHITE};border-radius:10px;padding:14px 18px;
               border-left:4px solid {ORANGE};margin-bottom:6px; }}
  .rec-card-title {{ font-size:13px;font-weight:700;color:{ORANGE_DARK};margin-bottom:5px; }}
  .rec-card p {{ margin:0;color:#111;font-size:12.5px;line-height:1.65; }}

  /* Override Streamlit warning/info text to black */
  [data-testid="stAlert"] {{ color: #111 !important; }}
  [data-testid="stAlert"] p {{ color: #111 !important; }}
  [data-testid="stAlert"] a {{ color: #111 !important; }}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────
df_raw  = st.session_state.get("df_survey", None)
api_key = st.session_state.get("api_key",   "")
model   = st.session_state.get("model",     "gpt-4o")

# ── Header — same pattern as page 2, NO icon ─────────────
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown("""<div style='padding:4px 0'>
      <div style='font-size:11px;color:#999;letter-spacing:1px;text-transform:uppercase;'>Monkey Baa Theatre</div>
      <div style='font-size:20px;font-weight:700;color:#333;line-height:1.3;'>
        Fostering Emotional Literacy:
        <span style='color:#E8673A;'> Emotional &amp; Social Impact</span></div>
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

if df_raw is None:
    st.warning("⬅️ Upload the **Survey CSV** in the sidebar on the Home page first.")
    st.stop()

# ── Prepare data ──────────────────────────────────────────
df = df_raw.copy()
df.columns = df.columns.str.strip()

EMOTION_COLS  = ["Happy", "Sad", "Surprised", "Bored", "Angry", "Confused", "Scared", "Curious"]
EMOTION_EMOJI = {
    "Happy": "😊", "Curious": "🤔", "Surprised": "😮", "Scared": "😨",
    "Sad":   "😢", "Confused": "😕", "Bored":    "😑", "Angry":   "😠",
}
QUALITY_COLS = ["Personal Meaning", "Excellence", "Aesthetic Experience",
                "Creativity", "Imagination", "Belonging"]

for col in EMOTION_COLS + QUALITY_COLS:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

for col in ["net-promoter-score", "The performance was entertaining",
            "The performance was emotionally impactful"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

n = len(df)

emotion_pcts   = {c: round(100 * df[c].sum() / n, 1) for c in EMOTION_COLS if c in df.columns}
emotion_sorted = sorted(emotion_pcts.items(), key=lambda x: x[1], reverse=True)

quality_avgs   = {c: round(df[c].mean(), 2) for c in QUALITY_COLS
                  if c in df.columns and df[c].notna().sum() > 0}
quality_sorted = sorted(quality_avgs.items(), key=lambda x: x[1], reverse=True)

nps          = round(df["net-promoter-score"].mean(), 1)                    if "net-promoter-score" in df.columns else "N/A"
ent_score    = round(df["The performance was entertaining"].mean(), 1)      if "The performance was entertaining" in df.columns else "N/A"
impact_score = round(df["The performance was emotionally impactful"].mean(), 1) if "The performance was emotionally impactful" in df.columns else "N/A"
pct_excellent = round(100 * (df["overall-experience"] == "Excellent").sum() / n, 1) if "overall-experience" in df.columns else "N/A"
pct_happy     = emotion_pcts.get("Happy", 0)

# ── AI helper ─────────────────────────────────────────────
def call_ai(prompt, context):
    client = OpenAI(api_key=api_key)
    r = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompt},
                  {"role": "user",   "content": f"Data:\n{context}"}],
        temperature=0.3, max_tokens=1000,
    )
    return r.choices[0].message.content.strip()

def bullets_html(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    items = [l for l in lines if l.startswith(("•", "-"))] or lines
    li    = "".join(f"<li>{b.lstrip('•- ').strip()}</li>" for b in items)
    return f"<div class='insight-box'><ul>{li}</ul></div>"

def placeholder(msg):
    return f"<div class='insight-box' style='color:#bbb;font-style:italic;'>{msg}</div>"

# ── Prompts ───────────────────────────────────────────────
PROMPT_QUALITY = (
    "You are an arts analytics expert for Monkey Baa Theatre, an Australian children's theatre company. "
    "Analyse these 6 artistic quality scores rated by audience members (scale 0–10). "
    "Return exactly 3 bullet points (starting with •) for a theatre manager. "
    "Each bullet must be 30–50 words. "
    "Cover: the strongest dimension with specific score and what it signals, overall pattern across dimensions, "
    "and one concrete actionable recommendation tied to the lowest-scoring dimension."
)
PROMPT_EMOTION = (
    "You are an arts education expert for Monkey Baa Theatre, an Australian children's theatre company. "
    "These are emotions felt by young people during live performances (% of respondents). "
    "Return exactly 3 bullet points (starting with •) for a theatre manager. "
    "Each bullet must be 30–50 words. "
    "Cover: the dominant emotion and what it reveals about the audience experience, "
    "the meaning of the emotional range across all 8 emotions, "
    "and one strategic programming or marketing insight based on the emotional data."
)
PROMPT_REC = (
    "You are a strategic advisor for Monkey Baa Theatre, an Australian children's theatre company. "
    "Based on ALL the emotional and quality data provided, generate exactly 3 strategic recommendations "
    "for theatre managers. Each recommendation: action-oriented title (5–7 words) + 2 sentences of rationale. "
    "Return ONLY JSON: "
    '{\"items\":[{\"title\":\"...\",\"body\":\"...\"},{\"title\":\"...\",\"body\":\"...\"},{\"title\":\"...\",\"body\":\"...\"}]}'
)
PROMPT_SUMMARY = (
    "You are a senior analyst for Monkey Baa Theatre, an Australian children's theatre company. "
    "Write an executive summary of exactly 5 sentences in flowing prose (no bullet points) "
    "for a board-level report on Emotional & Social Impact. "
    "Structure it as follows: "
    "(1) Open with the headline satisfaction result using exact numbers. "
    "(2) Describe the emotional experience of young audiences — dominant emotions and what they signal. "
    "(3) Analyse the artistic quality dimensions — what is strong and what needs attention. "
    "(4) Connect the findings to Monkey Baa's mission of embedding arts in young Australians' lives. "
    "(5) Close with one forward-looking strategic recommendation for leadership."
)

# ── Generate button ───────────────────────────────────────
run = st.button("🚀 Generate AI Insights", type="primary")

KEY_Q   = "esi_quality_insight"
KEY_E   = "esi_emotion_insight"
KEY_REC = "esi_rec"
KEY_SUM = "esi_exec_summary"

if run:
    if not api_key:
        st.error("Enter your OpenAI API key in the sidebar on the Home page.")
        st.stop()
    with st.spinner("Generating insights…"):
        try:
            q_ctx = "\n".join([f"{c}: {v}/10" for c, v in quality_sorted])
            st.session_state[KEY_Q] = call_ai(PROMPT_QUALITY, q_ctx)

            e_ctx = "\n".join([f"{e}: {v}% of young audience members" for e, v in emotion_sorted])
            st.session_state[KEY_E] = call_ai(PROMPT_EMOTION, e_ctx)

            full_ctx = (q_ctx + "\n\n" + e_ctx +
                        f"\n\nQuality insights:\n{st.session_state[KEY_Q]}"
                        f"\n\nEmotion insights:\n{st.session_state[KEY_E]}")
            st.session_state[KEY_REC] = call_ai(PROMPT_REC, full_ctx)

            sum_ctx = (f"Survey respondents: {n}\nFelt Happy: {pct_happy}%\n"
                       f"Rated Excellent: {pct_excellent}%\nNPS: {nps}/10\n"
                       f"Emotional Impact: {impact_score}/10\n"
                       f"Top quality: {quality_sorted[0][0] if quality_sorted else 'N/A'}\n"
                       f"Lowest quality: {quality_sorted[-1][0] if quality_sorted else 'N/A'}\n"
                       f"Insights:\n{st.session_state[KEY_Q]}\n{st.session_state[KEY_E]}")
            st.session_state[KEY_SUM] = call_ai(PROMPT_SUMMARY, sum_ctx)
        except Exception as e:
            st.error(f"API error: {e}")
            st.stop()

ins_q   = st.session_state.get(KEY_Q,   None)
ins_e   = st.session_state.get(KEY_E,   None)
ins_rec = st.session_state.get(KEY_REC, None)
ins_sum = st.session_state.get(KEY_SUM, None)

# ════════════════════════════════════════════════════════════
# KPI ROW
# ════════════════════════════════════════════════════════════
k1, k2, k3 = st.columns(3)
for col, label, value, sub in [
    (k1, "Young People Felt Happy",    f"{pct_happy}%",    f"Top emotional response · n={n:,}"),
    (k2, "Rated Experience Excellent", f"{pct_excellent}%","Overall satisfaction"),
    (k3, "Emotional Impact Score",     f"{impact_score}/10",f"Entertainment: {ent_score}/10"),
]:
    with col:
        st.markdown(f"""<div class='kpi-card'>
          <div class='kpi-label'>{label}</div>
          <div class='kpi-value'>{value}</div>
          <div style='font-size:11px;opacity:.82;margin-top:3px;'>{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# SECTION 1 — Artistic Quality Metrics
# ════════════════════════════════════════════════════════════
st.markdown(f"<div class='section-title'>Artistic Quality Metrics — Audience Perception</div>",
            unsafe_allow_html=True)

c1, c2 = st.columns([5, 5])

with c1:
    # Progress bars — NO icons, NO ranking title, black text
    for col, val in quality_sorted:
        pct_w = round(100 * val / 10, 1)
        st.markdown(f"""<div class='progress-row'>
          <div class='progress-label'>{col}</div>
          <div class='progress-bar-bg'>
            <div class='progress-bar-fill' style='width:{pct_w}%;'></div>
          </div>
          <div class='progress-pct'>{val}</div>
        </div>""", unsafe_allow_html=True)

with c2:
    if ins_q:
        st.markdown(bullets_html(ins_q), unsafe_allow_html=True)
    else:
        st.markdown(placeholder("Click <b>🚀 Generate AI Insights</b> to load quality insights."),
                    unsafe_allow_html=True)

st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# SECTION 2 — Emotional Responses During Performance
# ════════════════════════════════════════════════════════════
st.markdown(f"<div class='section-title'>Emotional Responses During Performance</div>",
            unsafe_allow_html=True)

c3, c4 = st.columns([5, 5])

with c3:
    # Vertical bar chart — emoji ON TOP, label BELOW in small font
    # Using customdata + ticktext trick: emoji as tick, name as second line small
    emotions_list = [e for e, _ in emotion_sorted]
    values_list   = [v for _, v in emotion_sorted]
    colors        = ["#E8673A" if i == 0 else "#F4A57A" if i < 3 else "#F9C9A8"
                     for i in range(len(values_list))]

    # Build x-axis labels: emoji line + small name below using <br>
    x_labels = [
        f"{EMOTION_EMOJI.get(e, '')}<br><span style='font-size:9px'>{e}</span>"
        for e in emotions_list
    ]
    # Plotly doesn't render HTML in tick labels — use two-line approach with \n
    # and set large font for emoji + small separately via ticktext
    tick_labels = [f"{EMOTION_EMOJI.get(e,'')}" for e in emotions_list]
    tick_names  = [e for e in emotions_list]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(range(len(emotions_list))),
        y=values_list,
        marker_color=colors,
        text=[f"{v}%" for v in values_list],
        textposition="outside",
        textfont=dict(size=12, color="#333"),
        hovertemplate="<b>%{customdata}</b><br>%{y}% of respondents<extra></extra>",
        customdata=emotions_list,
    ))
    fig.update_layout(
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        margin=dict(l=10, r=10, t=30, b=60),
        yaxis=dict(
            title="% of Respondents",
            range=[0, max(values_list) * 1.18],
            gridcolor="#F0EBE3",
            tickfont=dict(color="#555", size=11),
        ),
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(len(emotions_list))),
            # Two-line tick: large emoji on first line, small name on second
            ticktext=[f"{EMOTION_EMOJI.get(e,'')}  {e}" for e in emotions_list],
            tickfont=dict(size=13, color="#222"),
            tickangle=0,
        ),
        height=400,
        bargap=0.35,
        showlegend=False,
    )
    # Override: render emoji large and name small using annotations per bar
    for i, e in enumerate(emotions_list):
        fig.add_annotation(
            x=i, y=-8,          # below x-axis in data coords won't work in plotly easily
            xref="x", yref="paper",
            text=f"<b style='font-size:18px'>{EMOTION_EMOJI.get(e,'')}</b>",
            showarrow=False,
            yanchor="top",
            font=dict(size=18),
            xanchor="center",
        )

    # Simplest reliable approach: emoji big + name small in ticktext using unicode trick
    # Use ticktext with two separate font size lines — plotly supports partial HTML in ticktext
    fig.update_xaxes(
        tickmode="array",
        tickvals=list(range(len(emotions_list))),
        ticktext=[EMOTION_EMOJI.get(e, "") for e in emotions_list],
        tickfont=dict(size=22, color="#222"),   # emoji large
        tickangle=0,
    )
    # Add name annotations below emoji ticks
    for i, e in enumerate(emotions_list):
        fig.add_annotation(
            x=i,
            y=-0.12,
            xref="x",
            yref="paper",
            text=f"<span style='font-size:9px;color:#444;'>{e}</span>",
            showarrow=False,
            font=dict(size=9, color="#444"),
            xanchor="center",
            yanchor="top",
        )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with c4:
    if ins_e:
        st.markdown(bullets_html(ins_e), unsafe_allow_html=True)
    else:
        st.markdown(placeholder("Click <b>🚀 Generate AI Insights</b> to load emotion insights."),
                    unsafe_allow_html=True)

st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# SECTION 3 — Strategic Recommendations (3 cards)
# ════════════════════════════════════════════════════════════
st.markdown("<div style='font-size:15px;font-weight:600;color:#333;margin-bottom:4px;'>Strategic Recommendations</div>",
            unsafe_allow_html=True)
st.markdown("<hr class='div'>", unsafe_allow_html=True)

if ins_rec:
    import json, re as _re
    try:
        _clean    = _re.sub(r"```(?:json)?", "", ins_rec).strip().rstrip("`").strip()
        rec_data  = json.loads(_clean)
        rec_items = rec_data.get("items", [])
    except Exception:
        rec_items = []

    if rec_items:
        rc1, rc2, rc3 = st.columns(3)
        for col, item in zip([rc1, rc2, rc3], rec_items[:3]):
            with col:
                st.markdown(f"""<div class='rec-card'>
                  <div class='rec-card-title'>{item.get("title","")}</div>
                  <p>{item.get("body","")}</p>
                </div>""", unsafe_allow_html=True)
    else:
        st.markdown(bullets_html(ins_rec), unsafe_allow_html=True)
else:
    st.markdown(placeholder("Click <b>🚀 Generate AI Insights</b> to load strategic recommendations."),
                unsafe_allow_html=True)

st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# SECTION 4 — Executive Summary
# ════════════════════════════════════════════════════════════
st.markdown("<div style='font-size:15px;font-weight:600;color:#333;margin-bottom:4px;'>Summary</div>",
            unsafe_allow_html=True)
st.markdown("<hr class='div'>", unsafe_allow_html=True)

low_dim = quality_sorted[-1] if quality_sorted else ("Belonging", 5.67)

st.markdown(
    f"<div class='summary-box'>{ins_sum}</div>" if ins_sum
    else placeholder("Click <b>🚀 Generate AI Insights</b> to load the executive summary."),
    unsafe_allow_html=True
)

# ── Download PDF ──────────────────────────────────────────
if ins_sum:
    st.divider()

    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    def fig_to_bytes(fig):
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        return buf

    def generate_esi_pdf(pct_happy, pct_excellent, impact_score, ent_score, n,
                         quality_sorted, emotion_sorted, EMOTION_EMOJI,
                         ins_q, ins_e, ins_rec, ins_sum):

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                                topMargin=0.4*inch, bottomMargin=0.4*inch,
                                leftMargin=0.6*inch, rightMargin=0.6*inch)
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22,
                                     textColor=colors.HexColor('#222222'), spaceAfter=2,
                                     spaceBefore=0, fontName='Helvetica-Bold')
        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Heading2'], fontSize=14,
                                        textColor=colors.HexColor('#E8673A'), spaceAfter=8,
                                        spaceBefore=0, fontName='Helvetica-Bold')
        heading_style = ParagraphStyle('Heading', parent=styles['Heading3'], fontSize=12,
                                       textColor=colors.HexColor('#333333'), spaceAfter=6,
                                       spaceBefore=8, fontName='Helvetica-Bold')
        body_style = ParagraphStyle('Body', parent=styles['BodyText'], fontSize=9,
                                    textColor=colors.HexColor('#555555'), spaceAfter=4,
                                    leading=11, alignment=TA_JUSTIFY)
        bullet_style = ParagraphStyle('Bullet', parent=styles['BodyText'], fontSize=9,
                                      textColor=colors.HexColor('#555555'), spaceAfter=3,
                                      leftIndent=18, leading=11, bulletIndent=8)
        kpi_style = ParagraphStyle('KPI', parent=styles['Normal'], fontSize=11,
                                   textColor=colors.white, alignment=TA_CENTER,
                                   fontName='Helvetica-Bold', leading=14)

        # ── PÁGINA 1: Header + KPIs + Quality Metrics + Quality Insights ──
        story.append(Paragraph("MONKEY BAA THEATRE", title_style))
        story.append(Paragraph(
            "Fostering Emotional Literacy: <font color='#E8673A'>Emotional &amp; Social Impact</font>",
            subtitle_style))
        story.append(Spacer(1, 0.08*inch))

        # KPI Cards
        kpi_data = [[
            Paragraph(f"<b>Young People Felt Happy</b><br/>{pct_happy}%<br/><font size='8'>Top emotional response · n={n:,}</font>", kpi_style),
            Paragraph(f"<b>Rated Experience Excellent</b><br/>{pct_excellent}%<br/><font size='8'>Overall satisfaction</font>", kpi_style),
            Paragraph(f"<b>Emotional Impact Score</b><br/>{impact_score}/10<br/><font size='8'>Entertainment: {ent_score}/10</font>", kpi_style),
        ]]
        kpi_table = Table(kpi_data, colWidths=[2*inch, 2*inch, 2*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E8673A')),
            ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
            ('TOPPADDING',    (0, 0), (-1, -1), 14),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 0.14*inch))

        # Section 1 title
        story.append(Paragraph("Artistic Quality Metrics — Audience Perception", heading_style))
        story.append(Spacer(1, 0.06*inch))

        # Quality progress bars as a matplotlib chart
        try:
            labels = [c for c, _ in quality_sorted]
            vals   = [v for _, v in quality_sorted]
            bar_colors = ['#E8673A' if i == 0 else '#F4A57A' if i < 3 else '#F9C9A8'
                          for i in range(len(vals))]

            fig_q, ax_q = plt.subplots(figsize=(6.5, 2.2))
            bars = ax_q.barh(labels[::-1], [v/10*100 for v in vals[::-1]],
                             color=bar_colors[::-1], height=0.55)
            for bar, val in zip(bars, vals[::-1]):
                ax_q.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height()/2,
                          f"{val}", va='center', fontsize=9, color='#333', fontweight='bold')
            ax_q.set_xlim(0, 110)
            ax_q.set_xlabel("Score (out of 10)", fontsize=8, color='#555')
            ax_q.tick_params(axis='y', labelsize=9, colors='#333')
            ax_q.tick_params(axis='x', labelsize=8, colors='#555')
            ax_q.set_facecolor('#F5F0EA')
            fig_q.patch.set_facecolor('white')
            ax_q.grid(True, axis='x', alpha=0.2)
            ax_q.spines['top'].set_visible(False)
            ax_q.spines['right'].set_visible(False)
            plt.tight_layout()
            story.append(Image(fig_to_bytes(fig_q), width=6.5*inch, height=2.2*inch))
            plt.close(fig_q)
        except:
            story.append(Paragraph("<i>Quality chart generation failed</i>", body_style))

        story.append(Spacer(1, 0.08*inch))

        # Quality Insights bullets
        if ins_q:
            for line in ins_q.split('\n'):
                if line.strip().startswith(('•', '-')):
                    story.append(Paragraph(line.strip(), bullet_style))

        story.append(PageBreak())

        # ── PÁGINA 2: Emotion Bar Chart + Emotion Insights ──
        story.append(Paragraph("Emotional Responses During Performance", heading_style))
        story.append(Spacer(1, 0.06*inch))

        try:
            em_labels = [f"{EMOTION_EMOJI.get(e,'')} {e}" for e, _ in emotion_sorted]
            em_vals   = [v for _, v in emotion_sorted]
            em_colors = ['#E8673A' if i == 0 else '#F4A57A' if i < 3 else '#F9C9A8'
                         for i in range(len(em_vals))]

            fig_e, ax_e = plt.subplots(figsize=(6.5, 2.8))
            bar_e = ax_e.bar(range(len(em_labels)), em_vals, color=em_colors, width=0.6)
            for bar, val in zip(bar_e, em_vals):
                ax_e.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                          f"{val}%", ha='center', va='bottom', fontsize=8, color='#333')
            ax_e.set_xticks(range(len(em_labels)))
            ax_e.set_xticklabels(em_labels, fontsize=8, color='#333')
            ax_e.set_ylabel("% of Respondents", fontsize=8, color='#555')
            ax_e.set_facecolor('#F5F0EA')
            fig_e.patch.set_facecolor('white')
            ax_e.grid(True, axis='y', alpha=0.2)
            ax_e.spines['top'].set_visible(False)
            ax_e.spines['right'].set_visible(False)
            plt.tight_layout()
            story.append(Image(fig_to_bytes(fig_e), width=6.5*inch, height=2.8*inch))
            plt.close(fig_e)
        except:
            story.append(Paragraph("<i>Emotion chart generation failed</i>", body_style))

        story.append(Spacer(1, 0.08*inch))

        # Emotion Insights bullets
        if ins_e:
            for line in ins_e.split('\n'):
                if line.strip().startswith(('•', '-')):
                    story.append(Paragraph(line.strip(), bullet_style))

        story.append(PageBreak())

        # ── PÁGINA 3: Strategic Recommendations ──
        story.append(Paragraph("Strategic Recommendations", heading_style))
        story.append(Spacer(1, 0.08*inch))

        if ins_rec:
            import json as _json, re as _re
            try:
                _clean    = _re.sub(r"```(?:json)?", "", ins_rec).strip().rstrip("`").strip()
                rec_data  = _json.loads(_clean)
                rec_items = rec_data.get("items", [])
            except Exception:
                rec_items = []

            for i, item in enumerate(rec_items[:3], 1):
                title = item.get("title", "")
                body  = item.get("body",  "")
                story.append(Paragraph(f"<b>{i}. {title}</b>", body_style))
                story.append(Paragraph(body, bullet_style))
                story.append(Spacer(1, 0.08*inch))

        story.append(Spacer(1, 0.1*inch))

        # ── Summary ──
        story.append(Paragraph("Summary", heading_style))
        story.append(Spacer(1, 0.05*inch))
        story.append(Paragraph(ins_sum, body_style))

        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            "Report generated by Monkey Baa Theatre AI Reporting System",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7,
                           textColor=colors.HexColor('#999999'), alignment=TA_CENTER)))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    pdf_bytes = generate_esi_pdf(
        pct_happy, pct_excellent, impact_score, ent_score, n,
        quality_sorted, emotion_sorted, EMOTION_EMOJI,
        ins_q, ins_e, ins_rec, ins_sum
    )
    st.download_button(
        "📄 Download Report (.pdf)",
        data=pdf_bytes,
        file_name="emotional_social_impact.pdf",
        mime="application/pdf"
    )