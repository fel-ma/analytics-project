"""
pages/4_High_Quality_Outcomes.py
=================================
Report: High Quality Outcomes (Spark)
Uses: Data_survey.csv via st.session_state["df_survey"]
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
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

# ── Styles (exact copy of page 2 pattern) ────────────────
st.markdown(f"""
<style>
  .stApp {{ background-color: {BEIGE}; }}
  .kpi-card {{ background-color:{ORANGE};border-radius:12px;padding:14px 12px;
               text-align:center;color:white; }}
  .kpi-label {{ font-size:11px;font-weight:500;opacity:.85;margin-bottom:3px; }}
  .kpi-value {{ font-size:28px;font-weight:700;line-height:1.1; }}
  .card {{ background-color:{WHITE};border-radius:12px;padding:16px 20px;margin-bottom:12px; }}
  .insight-box {{ background-color:#FDF3EE;border-radius:10px;padding:14px 16px;
                  color:{GRAY_TEXT};font-size:13px;line-height:1.6; }}
  .insight-box ul {{ margin:0;padding-left:16px; }}
  .insight-box li {{ margin-bottom:7px; }}
  .section-title {{ font-size:14px;font-weight:600;color:{ORANGE_DARK};
                    margin-bottom:8px;text-decoration:underline; }}
  .summary-box {{ background-color:{WHITE};border-radius:12px;padding:16px 20px;
                  color:{GRAY_TEXT};font-size:13px;line-height:1.7; }}
  hr.div {{ border:none;border-top:1px solid #e0d8d0;margin:6px 0 12px 0; }}

  /* Table panel */
  .panel-table {{ width:100%;border-collapse:collapse;font-size:12px;color:#333; }}
  .panel-table th {{ background-color:{ORANGE};color:white;padding:7px 10px;
                     text-align:left;border:1px solid {ORANGE_DARK}; }}
  .panel-table td {{ padding:5px 10px;border:1px solid #ddd; }}
  .panel-table tr:nth-child(even) {{ background-color:#fdf6f2; }}
  .panel-table tr:hover {{ background-color:#fce8dc; }}

  /* Numbered insight blocks */
  .insight-num {{ display:flex;gap:12px;margin-bottom:12px;align-items:flex-start; }}
  .insight-num-badge {{
    background:{ORANGE};color:white;border-radius:50%;
    width:26px;height:26px;min-width:26px;
    display:flex;align-items:center;justify-content:center;
    font-size:13px;font-weight:700;
  }}
  .insight-num-text {{ color:{GRAY_TEXT};font-size:13px;line-height:1.65; }}

  /* Rec / Summary cards */
  .rec-card {{
    background:white;border-radius:10px;padding:14px 20px;
    margin-bottom:8px;border-left:4px solid {ORANGE};
  }}
  .rec-card-title {{ font-size:13px;font-weight:700;color:{ORANGE_DARK};margin-bottom:6px; }}
  .rec-card p {{ margin:0;color:{GRAY_TEXT};font-size:13px;line-height:1.7; }}
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────
df_raw  = st.session_state.get("df_survey",  None)
api_key = st.session_state.get("api_key",    "")
model   = st.session_state.get("model",      "gpt-4o")


# ── Header (same pattern as page 2) ──────────────────────
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown("""<div style='padding:4px 0'>
      <div style='font-size:11px;color:#999;letter-spacing:1px;text-transform:uppercase;'>Monkey Baa Theatre</div>
      <div style='font-size:20px;font-weight:700;color:#333;line-height:1.3;'>
        Expanding Youth Theatre Access:
        <span style='color:#E8673A;'> Social Outcomes Impact (Spark)</span></div>
    </div>""", unsafe_allow_html=True)
with h2:
    st.markdown("""<div style='text-align:right;padding-top:12px;font-size:22px;
                    font-weight:700;color:#222;font-style:italic;'>monkey baa</div>""",
                unsafe_allow_html=True)

st.markdown("<hr class='div'>", unsafe_allow_html=True)

if df_raw is None:
    st.warning("⬅️ Upload the **Survey CSV** in the sidebar on the Home page first.")
    st.stop()


# ── Prepare data ──────────────────────────────────────────
df = df_raw.copy()
df.columns = df.columns.str.strip()
n = len(df)

# Numeric cols
for col in ["net-promoter-score", "The performance was entertaining",
            "The performance was emotionally impactful"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# KPIs
pct_excellent = round(100 * (df["overall-experience"] == "Excellent").sum() / n, 1)
nps_val       = round(df["net-promoter-score"].mean(), 1)
pct_negative  = round(100 * df["overall-experience"].isin(["Poor", "Neutral"]).sum() / n, 1)

# Enjoyment ratings
enjoy_col    = "How much did the young person enjoy the show?"
enjoy_counts = df[enjoy_col].value_counts() if enjoy_col in df.columns else pd.Series(dtype=int)
ENJOY_ORDER  = ["They liked the show a lot", "They liked the show a little",
                "Neither liked nor disliked the show",
                "They disliked the show a little", "They disliked the show a lot"]
ENJOY_LABELS = {
    "They liked the show a lot":         "Liked a lot",
    "They liked the show a little":      "Liked a little",
    "Neither liked nor disliked the show":"Neutral",
    "They disliked the show a little":   "Disliked a little",
    "They disliked the show a lot":      "Disliked a lot",
}

# Intent to return
return_col    = "Intent to Return (Organisation)"
return_counts = df[return_col].value_counts() if return_col in df.columns else pd.Series(dtype=int)
RETURN_ORDER  = ["Very likely", "Likely", "Neutral", "Unlikely", "Very unlikely"]

# Age groups — expand multi-select rows
age_col = "Please tell us the age/s of the young people that attended the show with you."
age_counts = {"0-5 years": 0, "6-12 years": 0, "13-17 years": 0}
if age_col in df.columns:
    for val in df[age_col].dropna():
        for part in str(val).split(";"):
            part = part.strip()
            if part in age_counts:
                age_counts[part] += 1

# Discovery — expand multi-select
disc_col = "How did you hear about Monkey Baa's show?"
disc_map  = {
    "Social Media":       0,
    "Word of Mouth":      0,
    "Email Newsletter":   0,
    "Google Search":      0,
    "Flyer / Poster":     0,
    "Other":              0,
}
if disc_col in df.columns:
    for val in df[disc_col].dropna():
        val_lower = val.lower()
        if "social media" in val_lower or "facebook" in val_lower or "instagram" in val_lower:
            disc_map["Social Media"] += 1
        if "word of mouth" in val_lower:
            disc_map["Word of Mouth"] += 1
        if "email" in val_lower or "newsletter" in val_lower:
            disc_map["Email Newsletter"] += 1
        if "google" in val_lower:
            disc_map["Google Search"] += 1
        if "flyer" in val_lower or "poster" in val_lower:
            disc_map["Flyer / Poster"] += 1
        if "other" in val_lower or "parenting" in val_lower or "review" in val_lower or "child" in val_lower or "previous" in val_lower:
            disc_map["Other"] += 1
disc_series = pd.Series(disc_map).sort_values(ascending=False)


# ── Context builder for AI ────────────────────────────────
def build_context():
    buf = [
        "=== MONKEY BAA THEATRE — SPARK SURVEY DATA ===",
        f"Total respondents: {n}",
        "",
        "OVERALL SATISFACTION:",
        f"  Rated Excellent: {pct_excellent}%",
        f"  Negative (Poor/Neutral): {pct_negative}%",
        f"  Net Promoter Score (avg): {nps_val}/10",
        "",
        "ENJOYMENT RATINGS:",
    ]
    for k in ENJOY_ORDER:
        v = enjoy_counts.get(k, 0)
        buf.append(f"  {ENJOY_LABELS.get(k, k)}: {v} ({round(100*v/n,1)}%)")
    buf.append("")
    buf.append("INTENT TO RETURN:")
    for k in RETURN_ORDER:
        v = return_counts.get(k, 0)
        buf.append(f"  {k}: {v} ({round(100*v/n,1)}%)")
    buf.append("")
    buf.append("AGE GROUPS:")
    for k, v in age_counts.items():
        buf.append(f"  {k}: {v} mentions")
    buf.append("")
    buf.append("AUDIENCE DISCOVERY CHANNELS:")
    for k, v in disc_map.items():
        buf.append(f"  {k}: {v} mentions")
    return "\n".join(buf)


ctx = build_context()


# ── AI call helper ────────────────────────────────────────
def call_ai(system_prompt, context):
    r = OpenAI(api_key=api_key).chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user",   "content": f"Data:\n{context}"}],
        temperature=0.3, max_tokens=900,
    )
    return r.choices[0].message.content.strip()


# ── Render helpers ────────────────────────────────────────
def bullets_html(text, numbered=False):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    items = [l for l in lines if l.startswith(("•", "-", "1", "2", "3", "4", "5"))] or lines
    if numbered:
        html = ""
        for i, b in enumerate(items, 1):
            clean = b.lstrip("•-0123456789. ").strip()
            html += f"""<div class='insight-num'>
              <div class='insight-num-badge'>{i}</div>
              <div class='insight-num-text'>{clean}</div>
            </div>"""
        return f"<div>{html}</div>"
    li = "".join(f"<li>{b.lstrip('•- ').strip()}</li>" for b in items)
    return f"<div class='insight-box'><ul>{li}</ul></div>"

def placeholder(msg):
    return f"<div class='insight-box' style='color:#bbb;font-style:italic;'>{msg}</div>"

def pct_color(pct):
    """Return a soft colour based on % value for table cells."""
    if pct >= 60:  return f"color:{ORANGE};font-weight:700;"
    if pct >= 30:  return f"color:#E8A03A;font-weight:600;"
    return f"color:{GRAY_TEXT};"

def make_panel_table(order, counts, label_map=None, total=None):
    total = total or n
    rows  = ""
    for k in order:
        v     = counts.get(k, 0)
        label = label_map.get(k, k) if label_map else k
        pct   = round(100 * v / total, 1) if total else 0
        style = pct_color(pct)
        rows += (f"<tr>"
                 f"<td>{label}</td>"
                 f"<td style='text-align:center;'>{v:,}</td>"
                 f"<td style='text-align:center;{style}'>{pct}%</td>"
                 f"</tr>")
    return f"""<table class='panel-table'>
      <thead><tr>
        <th>Category</th><th style='text-align:center;'>Count</th>
        <th style='text-align:center;'>%</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>"""


# ── AI Prompts (stored as constants — visible here) ───────
PROMPT_MAIN_INSIGHTS = """You are an impact analyst for Monkey Baa Theatre, an Australian children's theatre company.
Analyse the survey data covering satisfaction, engagement, emotional impact, and intent to return.

Return exactly 5 numbered insights (start each with the number and a period, e.g. "1. ")
for a theatre executive. Each insight: 2–3 sentences. Cover:
1. Overall satisfaction headline with exact numbers
2. Enjoyment distribution and what it signals about production quality
3. Intent to return — loyalty and repeat attendance story
4. Net Promoter Score interpretation and what it means for word-of-mouth growth
5. One strategic tension or opportunity revealed by the data

No headers. No markdown bold. Plain sentences only."""

PROMPT_DEMO_INSIGHTS = """You are a demographic analyst for Monkey Baa Theatre, an Australian children's theatre company.
Analyse the age group distribution data for young people attending shows.

Return exactly 2 bullet points (starting with •) covering:
1. Which age group dominates and what this means for programming and content design
2. An underserved age segment opportunity and one concrete recommendation

Keep each bullet to 2–3 sentences. Use exact numbers from the data."""

PROMPT_MARKETING_INSIGHTS = """You are a marketing strategist for Monkey Baa Theatre, an Australian children's theatre company.
Analyse how audiences discovered the show — focus on marketing effectiveness and audience reach.

Return exactly 2 bullet points (starting with •) covering:
1. The dominant discovery channel with exact numbers and what it means for budget allocation
2. An underutilised channel or missed opportunity with a concrete action to grow reach

Keep each bullet to 2–3 sentences. Use exact numbers from the data."""

PROMPT_RECOMMENDATIONS = """You are a strategic advisor for Monkey Baa Theatre, an Australian children's theatre company.
Based on all survey data — satisfaction, enjoyment, return intent, age demographics, and discovery channels —
generate exactly 3 action-oriented recommendations for the theatre leadership team.

Return ONLY this JSON, no markdown, no preamble:
{
  "items": [
    {
      "title": "Recommendation title (5–8 words, action verb first)",
      "body": "2–3 sentences: what to do, why the data supports it, expected outcome."
    },
    {
      "title": "Recommendation title (5–8 words, action verb first)",
      "body": "2–3 sentences: what to do, why the data supports it, expected outcome."
    },
    {
      "title": "Recommendation title (5–8 words, action verb first)",
      "body": "2–3 sentences: what to do, why the data supports it, expected outcome."
    }
  ]
}"""

PROMPT_SUMMARY = """You are writing the executive summary for Monkey Baa Theatre's High Quality Outcomes report.
Synthesise all survey findings: satisfaction, enjoyment, intent to return, age demographics,
discovery channels, insights, and recommendations.

Write ONE cohesive paragraph of 5–6 sentences that:
1. Opens with the headline achievement (use exact KPI numbers)
2. Covers audience satisfaction and enjoyment quality
3. Addresses strategic value for sponsors and funders
4. References the demographic opportunity
5. Closes with a forward-looking statement about growth and impact

Tone: executive, persuasive, impact-focused. No bullet points. No headers."""


# ── Generate button ───────────────────────────────────────
run = st.button("🚀 Generate AI Insights", type="primary")

# Session keys
KEY_MAIN  = "hqo_main"
KEY_DEMO  = "hqo_demo"
KEY_MKT   = "hqo_mkt"
KEY_REC   = "hqo_rec"
KEY_SUM   = "hqo_sum"

if run:
    if not api_key:
        st.error("Enter your OpenAI API key in the sidebar on the Home page.")
        st.stop()
    with st.spinner("Generating insights…"):
        try:
            st.session_state[KEY_MAIN] = call_ai(PROMPT_MAIN_INSIGHTS,   ctx)
            st.session_state[KEY_DEMO] = call_ai(PROMPT_DEMO_INSIGHTS,   ctx)
            st.session_state[KEY_MKT]  = call_ai(PROMPT_MARKETING_INSIGHTS, ctx)
            st.session_state[KEY_REC]  = call_ai(PROMPT_RECOMMENDATIONS, ctx)

            # Summary gets all context + all insights
            full_ctx = ctx + "\n\n=== INSIGHTS ===\n" + st.session_state[KEY_MAIN]
            full_ctx += "\n\n=== DEMO INSIGHTS ===\n" + st.session_state[KEY_DEMO]
            full_ctx += "\n\n=== MARKETING INSIGHTS ===\n" + st.session_state[KEY_MKT]
            full_ctx += "\n\n=== RECOMMENDATIONS ===\n"    + st.session_state[KEY_REC]
            st.session_state[KEY_SUM] = call_ai(PROMPT_SUMMARY, full_ctx)
        except Exception as e:
            st.error(f"API error: {e}")
            st.stop()

# Retrieve
ins_main = st.session_state.get(KEY_MAIN, None)
ins_demo = st.session_state.get(KEY_DEMO, None)
ins_mkt  = st.session_state.get(KEY_MKT,  None)
ins_rec  = st.session_state.get(KEY_REC,  None)
ins_sum  = st.session_state.get(KEY_SUM,  None)


# ════════════════════════════════════════════════════════════
# SECTION 1 — KPI ROW
# ════════════════════════════════════════════════════════════
k1, k2, k3 = st.columns(3)
kpi_items = [
    (k1, "Rated the Show Excellent",  f"{pct_excellent}%",  f"n = {n:,} respondents"),
    (k2, "Net Promoter Score",         f"{nps_val}",         "avg score out of 10"),
    (k3, "Negative Feedback",          f"{pct_negative}%",   "Poor or Neutral responses"),
]
for col, label, value, sub in kpi_items:
    with col:
        st.markdown(f"""<div class='kpi-card'>
          <div class='kpi-label'>{label}</div>
          <div class='kpi-value'>{value}</div>
          <div style='font-size:11px;opacity:.82;margin-top:3px;'>{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# SECTION 2 — INSIGHTS (left) + DATA PANELS (right)
# ════════════════════════════════════════════════════════════
st.markdown("<div class='card'>", unsafe_allow_html=True)
c1, c2 = st.columns([5, 5])

with c1:
    st.markdown(f"<div class='section-title'>Insights</div>", unsafe_allow_html=True)
    if ins_main:
        st.markdown(bullets_html(ins_main, numbered=True), unsafe_allow_html=True)
    else:
        st.markdown(placeholder("Click <b>Generate AI Insights</b> to load insights."),
                    unsafe_allow_html=True)

with c2:
    # Panel A — Enjoyment Ratings
    st.markdown(f"<div class='section-title'>Enjoyment Ratings</div>", unsafe_allow_html=True)
    st.markdown(
        make_panel_table(ENJOY_ORDER, enjoy_counts, ENJOY_LABELS),
        unsafe_allow_html=True
    )

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

    # Panel B — Likelihood to Return
    st.markdown(f"<div class='section-title'>Likelihood to Return</div>", unsafe_allow_html=True)
    st.markdown(
        make_panel_table(RETURN_ORDER, return_counts),
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# SECTION 3 — AGE GROUPS + DISCOVERY
# ════════════════════════════════════════════════════════════
st.markdown("<div class='card'>", unsafe_allow_html=True)
c3, c4 = st.columns([5, 5])

with c3:
    # Age group bar chart (horizontal)
    age_labels = list(age_counts.keys())
    age_values = list(age_counts.values())
    age_colors = [ORANGE if i == 0 else "#F4A57A" if i == 1 else "#F9C9A8"
                  for i in range(len(age_values))]

    fig_age = go.Figure(go.Bar(
        x=age_values,
        y=age_labels,
        orientation="h",
        marker_color=age_colors,
        text=[f"{v:,}" for v in age_values],
        textposition="outside",
        textfont=dict(size=11, color="#555"),
    ))
    fig_age.update_layout(
        title=dict(
            text="Young people age groups attending",
            font=dict(size=13, color="#333", family="Arial"),
            x=0, xanchor="left",
        ),
        height=220,
        margin=dict(l=10, r=50, t=40, b=20),
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        xaxis=dict(gridcolor="#f0f0f0", tickfont=dict(size=10, color="#555"), title=None),
        yaxis=dict(tickfont=dict(size=12, color="#333"), title=None),
        bargap=0.35,
        showlegend=False,
    )
    st.plotly_chart(fig_age, use_container_width=True, config={"displayModeBar": False})

    # Discovery bar chart (horizontal) — bottom left
    st.markdown("<div style='margin-top:4px'></div>", unsafe_allow_html=True)
    disc_labels = list(disc_series.index)
    disc_values = list(disc_series.values)
    disc_colors = [ORANGE if i == 0 else "#F4A57A" if i == 1 else "#F9C9A8"
                   for i in range(len(disc_values))]

    fig_disc = go.Figure(go.Bar(
        x=disc_values,
        y=disc_labels,
        orientation="h",
        marker_color=disc_colors,
        text=[f"{v:,}" for v in disc_values],
        textposition="outside",
        textfont=dict(size=11, color="#555"),
    ))
    fig_disc.update_layout(
        title=dict(
            text="How audiences discovered Monkey Baa",
            font=dict(size=13, color="#333", family="Arial"),
            x=0, xanchor="left",
        ),
        height=280,
        margin=dict(l=10, r=60, t=40, b=20),
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        xaxis=dict(gridcolor="#f0f0f0", tickfont=dict(size=10, color="#555"), title=None),
        yaxis=dict(tickfont=dict(size=12, color="#333"), autorange="reversed", title=None),
        bargap=0.3,
        showlegend=False,
    )
    st.plotly_chart(fig_disc, use_container_width=True, config={"displayModeBar": False})

with c4:
    # Demo insights — top right
    st.markdown(f"<div class='section-title'>Age Group Insights</div>", unsafe_allow_html=True)
    if ins_demo:
        st.markdown(bullets_html(ins_demo), unsafe_allow_html=True)
    else:
        st.markdown(placeholder("Age group insights will appear after generation."),
                    unsafe_allow_html=True)

    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

    # Marketing insights — bottom right
    st.markdown(f"<div class='section-title'>Marketing & Discovery Insights</div>",
                unsafe_allow_html=True)
    if ins_mkt:
        st.markdown(bullets_html(ins_mkt), unsafe_allow_html=True)
    else:
        st.markdown(placeholder("Marketing insights will appear after generation."),
                    unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# SECTION 4 — RECOMMENDATIONS
# ════════════════════════════════════════════════════════════
st.markdown("<div style='font-size:15px;font-weight:600;color:#333;margin-bottom:4px;'>Recommendations</div>",
            unsafe_allow_html=True)
st.markdown("<hr class='div'>", unsafe_allow_html=True)

if ins_rec:
    try:
        rec_data  = json.loads(ins_rec)
        rec_items = rec_data.get("items", [])
    except Exception:
        rec_items = []

    if rec_items:
        rc1, rc2, rc3 = st.columns(3)
        cols = [rc1, rc2, rc3]
        for i, (col, item) in enumerate(zip(cols, rec_items[:3])):
            with col:
                st.markdown(f"""<div class='rec-card'>
                  <div class='rec-card-title'>{i+1}. {item.get("title","")}</div>
                  <p>{item.get("body","")}</p>
                </div>""", unsafe_allow_html=True)
    else:
        # fallback if JSON parse fails — render as bullets
        st.markdown(bullets_html(ins_rec), unsafe_allow_html=True)
else:
    st.markdown(placeholder("Recommendations will appear after generation."),
                unsafe_allow_html=True)

st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# SECTION 5 — SUMMARY
# ════════════════════════════════════════════════════════════
st.markdown("<div style='font-size:15px;font-weight:600;color:#333;margin-bottom:4px;'>Summary</div>",
            unsafe_allow_html=True)
st.markdown("<hr class='div'>", unsafe_allow_html=True)
st.markdown(
    f"<div class='summary-box'>{ins_sum}</div>" if ins_sum
    else "<div class='summary-box' style='color:#bbb;font-style:italic;'>"
         "Click <b>Generate AI Insights</b> to generate an executive summary.</div>",
    unsafe_allow_html=True
)

# ── Download ──────────────────────────────────────────────
if ins_sum:
    st.divider()
    md = f"""# Monkey Baa — High Quality Outcomes (Spark)
**Excellent:** {pct_excellent}% | **NPS:** {nps_val} | **Negative Feedback:** {pct_negative}%

## Insights
{ins_main}

## Age Group Insights
{ins_demo}

## Marketing Insights
{ins_mkt}

## Summary
{ins_sum}
"""
    st.download_button("📄 Download Report (.md)", md,
                       file_name="high_quality_outcomes.md", mime="text/markdown")
