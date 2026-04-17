"""
pages/6_High_Quality_Outcomes.py
=================================
Report: High Quality Outcomes
Survey data → df_survey from session_state
"""
 
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from openai import OpenAI
 
# ── Colour palette (matches page 2) ──────────────────────────────────────────
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
 
# ── CSS (mirrors page 2 exactly) ─────────────────────────────────────────────
st.markdown(f"""
<style>
  .stApp {{ background-color: {BEIGE}; }}
  [data-testid="stSidebarCollapseButton"] {{ display: none !important; }}
 
  /* ── KPI cards ── */
  .kpi-card {{
    background-color:{ORANGE}; border-radius:12px;
    padding:14px 12px; text-align:center; color:white;
  }}
  .kpi-label {{ font-size:11px; font-weight:500; opacity:.85; margin-bottom:3px; }}
  .kpi-value {{ font-size:28px; font-weight:700; line-height:1.1; }}
 
  /* ── Generic white card ── */
  .card {{
    background-color:{WHITE}; border-radius:12px;
    padding:16px 20px; margin-bottom:12px;
  }}
 
  /* ── Insight / bullet box ── */
  .insight-box {{
    background-color:#FDF3EE; border-radius:10px;
    padding:14px 16px; color:{GRAY_TEXT};
    font-size:13px; line-height:1.6;
  }}
  .insight-box ul {{ margin:0; padding-left:16px; }}
  .insight-box li {{ margin-bottom:7px; }}
 
  /* ── Numbered insight block ── */
  .insight-block {{
    background:{WHITE}; border-radius:10px;
    padding:14px 18px; margin-bottom:10px;
    border-left:4px solid {ORANGE};
  }}
  .insight-num {{
    font-size:10px; font-weight:700; color:{ORANGE};
    text-transform:uppercase; letter-spacing:.6px; margin-bottom:4px;
  }}
  .insight-text {{
    font-size:13px; color:{GRAY_TEXT}; line-height:1.65;
  }}
 
  /* ── Section titles ── */
  .section-title {{
    font-size:14px; font-weight:600; color:{ORANGE_DARK};
    margin-bottom:8px; text-decoration:underline;
  }}
 
  /* ── Table rows ── */
  .data-table {{ width:100%; border-collapse:collapse; font-size:12.5px; color:{GRAY_TEXT}; }}
  .data-table th {{
    background:#F0E8E0; padding:6px 10px;
    text-align:left; font-weight:600;
    border-bottom:2px solid #ddd;
  }}
  .data-table td {{ padding:5px 10px; border-bottom:1px solid #eee; }}
  .pct-bar {{
    display:inline-block; height:8px; border-radius:4px;
    background:{ORANGE}; vertical-align:middle; margin-right:6px;
  }}
 
  /* ── Recommendations ── */
  .rec-card {{
    background:{WHITE}; border-radius:12px;
    padding:16px 20px; margin-bottom:10px;
    border-left:4px solid {ORANGE};
  }}
  .rec-num {{
    font-size:10px; font-weight:700; color:{ORANGE};
    text-transform:uppercase; letter-spacing:.6px; margin-bottom:4px;
  }}
  .rec-text {{ font-size:13px; color:{GRAY_TEXT}; line-height:1.65; }}
 
  /* ── Summary box ── */
  .summary-box {{
    background-color:{WHITE}; border-radius:12px;
    padding:16px 20px; color:{GRAY_TEXT};
    font-size:13px; line-height:1.7;
  }}
 
  hr.div {{ border:none; border-top:1px solid #e0d8d0; margin:6px 0 12px 0; }}
  [data-testid="stSidebar"] {{ background-color: #1F4A4E !important; }}
  [data-testid="stHeader"] {{ display: none !important; }}
</style>
""", unsafe_allow_html=True)
 
 
# ── Shared helpers ────────────────────────────────────────────────────────────
def call_ai(api_key, model, system_prompt, user_content, max_tokens=700):
    r = OpenAI(api_key=api_key).chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_content},
        ],
        temperature=0.3,
        max_tokens=max_tokens,
    )
    return r.choices[0].message.content.strip()
 
 
def placeholder(msg):
    return (f"<div class='insight-box' style='color:#bbb;font-style:italic;'>"
            f"{msg}</div>")
 
 
# ── Load data ─────────────────────────────────────────────────────────────────
df_raw  = st.session_state.get("df_survey", None)
api_key = st.session_state.get("api_key", "")
model   = st.session_state.get("model", "gpt-4o")
 
# ── HEADER (matches page 2 exactly) ──────────────────────────────────────────
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown("""
    <div style='padding:4px 0'>
      <div style='font-size:11px;color:#999;letter-spacing:1px;text-transform:uppercase;'>
        Monkey Baa Theatre
      </div>
      <div style='font-size:20px;font-weight:700;color:#333;line-height:1.3;'>
        High Quality Outcomes:
        <span style='color:#E8673A;'> Audience Satisfaction & Engagement</span>
      </div>
    </div>""", unsafe_allow_html=True)
with h2:
    st.markdown("""
    <div style='text-align:right;padding-top:12px;font-size:22px;
                font-weight:700;color:#222;font-style:italic;'>
      monkey baa
    </div>""", unsafe_allow_html=True)
 
st.markdown("<hr class='div'>", unsafe_allow_html=True)
 
if df_raw is None:
    st.warning("⬅️ Upload **Data_survey.csv** in the sidebar on the Home page first.")
    st.stop()
 
# ── Prepare data ──────────────────────────────────────────────────────────────
df = df_raw.copy()
df.columns = df.columns.str.strip()
 
NUM_COLS = [
    "net-promoter-score", "The performance was entertaining",
    "The performance was emotionally impactful",
    "Personal Meaning", "Excellence", "Aesthetic Experience",
    "Creativity", "Imagination", "Belonging",
]
for col in NUM_COLS:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
 
n = len(df)
 
# KPI values
pct_excellent = round(100 * (df["overall-experience"] == "Excellent").sum() / n, 1)
nps_raw       = df["net-promoter-score"]
nps_mean      = round(nps_raw.mean(), 1)
# NPS score (Promoters - Detractors)
promoters  = (nps_raw >= 9).sum()
detractors = (nps_raw <= 6).sum()
nps_score  = round((promoters - detractors) / n * 100)
pct_negative = round(100 * (nps_raw <= 6).sum() / n, 1)
 
# Enjoyment table
ENJOY_MAP = {
    "They liked the show a lot":         "Liked a lot",
    "They liked the show a little":      "Liked a little",
    "Neither liked nor disliked the show":"Neutral",
    "They disliked the show a little":   "Disliked a little",
    "They disliked the show a lot":      "Disliked a lot",
}
enjoy_col   = "How much did the young person enjoy the show?"
enjoy_raw   = df[enjoy_col].map(ENJOY_MAP).value_counts()
enjoy_order = ["Liked a lot","Liked a little","Neutral","Disliked a little","Disliked a lot"]
enjoy_data  = [(cat, enjoy_raw.get(cat, 0)) for cat in enjoy_order]
 
# Return intention table
RETURN_MAP = {
    "Very likely":   "Very likely",
    "Likely":        "Likely",
    "Neutral":       "Neutral",
    "Unlikely":      "Unlikely",
    "Very unlikely": "Very unlikely",
}
return_col   = "Intent to Return (Organisation)"
return_raw   = df[return_col].map(RETURN_MAP).value_counts()
return_order = ["Very likely","Likely","Neutral","Unlikely","Very unlikely"]
return_data  = [(cat, return_raw.get(cat, 0)) for cat in return_order]
 
# Age groups (multi-select cell parsing)
age_col    = "Please tell us the age/s of the young people that attended the show with you."
age_counts = {"0–5 years": 0, "6–12 years": 0, "13–17 years": 0}
NORM       = {"0-5 years": "0–5 years", "6-12 years": "6–12 years", "13-17 years": "13–17 years"}
for val in df[age_col].dropna():
    for part in str(val).split(";"):
        k = NORM.get(part.strip())
        if k:
            age_counts[k] += 1
 
# Discovery (multi-select)
disc_col    = "How did you hear about Monkey Baa's show?"
disc_counts = {
    "Social Media": 0, "Word of Mouth": 0, "Email Newsletter": 0,
    "Google Search": 0, "Flyer / Poster": 0, "Previous Experience": 0, "Other": 0,
}
for val in df[disc_col].dropna():
    for part in str(val).split(";"):
        p = part.strip()
        if "Social Media" in p:        disc_counts["Social Media"] += 1
        elif "Word of Mouth" in p:     disc_counts["Word of Mouth"] += 1
        elif "Email" in p:             disc_counts["Email Newsletter"] += 1
        elif "Google" in p:            disc_counts["Google Search"] += 1
        elif "Flyer" in p or "poster" in p.lower(): disc_counts["Flyer / Poster"] += 1
        elif "Previous" in p:          disc_counts["Previous Experience"] += 1
        else:                          disc_counts["Other"] += 1
 
# ── Build AI context string ───────────────────────────────────────────────────
def build_context():
    enjoy_str  = "\n".join(f"  {cat}: {cnt} ({cnt/n*100:.1f}%)" for cat, cnt in enjoy_data)
    return_str = "\n".join(f"  {cat}: {cnt} ({cnt/n*100:.1f}%)" for cat, cnt in return_data)
    age_str    = "\n".join(f"  {k}: {v} ({v/n*100:.1f}%)" for k, v in age_counts.items())
    disc_str   = "\n".join(f"  {k}: {v}" for k, v in sorted(disc_counts.items(), key=lambda x: -x[1]))
    return f"""
MONKEY BAA THEATRE — HIGH QUALITY OUTCOMES SURVEY (n={n})
 
KEY METRICS:
  Rated Excellent: {pct_excellent}%
  Net Promoter Score (0-10 avg): {nps_mean}
  Calculated NPS score: {nps_score}
  Negative feedback (score ≤ 6): {pct_negative}%
 
ENJOYMENT RATINGS:
{enjoy_str}
 
LIKELIHOOD TO RETURN:
{return_str}
 
AGE GROUPS OF YOUNG PEOPLE ATTENDING:
{age_str}
 
HOW AUDIENCES DISCOVERED MONKEY BAA:
{disc_str}
 
PERFORMANCE SCORES (avg out of 10):
  Entertaining: {round(df['The performance was entertaining'].mean(),1) if 'The performance was entertaining' in df.columns else 'N/A'}
  Emotionally impactful: {round(df['The performance was emotionally impactful'].mean(),1) if 'The performance was emotionally impactful' in df.columns else 'N/A'}
  Aesthetic Experience: {round(df['Aesthetic Experience'].mean(),2) if 'Aesthetic Experience' in df.columns else 'N/A'}
  Excellence: {round(df['Excellence'].mean(),2) if 'Excellence' in df.columns else 'N/A'}
  Personal Meaning: {round(df['Personal Meaning'].mean(),2) if 'Personal Meaning' in df.columns else 'N/A'}
  Belonging: {round(df['Belonging'].mean(),2) if 'Belonging' in df.columns else 'N/A'}
"""
 
CTX = build_context()
 
# ── Session state keys ────────────────────────────────────────────────────────
KEY_INSIGHTS  = "hqo_insights"
KEY_AGE       = "hqo_age_insights"
KEY_DISC      = "hqo_disc_insights"
KEY_RECS      = "hqo_recommendations"
KEY_SUMMARY   = "hqo_summary"
 
# ── Prompts ───────────────────────────────────────────────────────────────────
PROMPT_INSIGHTS = """You are an expert analyst for Monkey Baa Theatre, an Australian children's theatre company.
Analyse audience satisfaction, engagement, emotional impact, and intent to return.
Return exactly 5 numbered insights for an executive report.
Each insight: 2-3 sentences, specific, evidence-based, action-relevant.
Format exactly as:
1. [Insight title]: [2-3 sentence explanation with data references]
2. ...
"""
PROMPT_AGE = """You are an expert analyst for Monkey Baa Theatre, an Australian children's theatre company.
Analyse the demographic trends in young audience age groups and interpret what this means for programming, content design, and developmental outcomes.
Return exactly 2 concise insights (2-3 sentences each).
Format: bullet points starting with •"""

PROMPT_DISC = """You are a marketing analyst for Monkey Baa Theatre, an Australian children's theatre company.
Analyse how audiences discovered the show and what this reveals about marketing effectiveness and audience reach strategy.
Return exactly 2 concise insights (2-3 sentences each).
Format: bullet points starting with •"""

PROMPT_RECS = """You are a strategic advisor for Monkey Baa Theatre, an Australian children's theatre company.
Based on all survey insights — satisfaction, engagement, demographics, marketing — generate exactly 3 action-oriented recommendations.
Each recommendation: 2-3 sentences explaining what to do and why. No titles.
Format:
1. [explanation]
2. [explanation]
3. [explanation]"""

PROMPT_SUMMARY = """You are a senior analyst writing for Monkey Baa Theatre's board and sponsors.
Using all survey data, insights and recommendations, write an executive summary covering:
1. Overall performance and audience satisfaction
2. Audience engagement and social impact
3. Strategic value and return on investment for sponsors
Tone: executive, persuasive, impact-focused. Max 4 sentences total. No bullet points — flowing prose."""

# ── Generate button ───────────────────────────────────────────────────────────
run = st.button("🚀 Generate AI Insights", type="primary")

if run:
    if not api_key:
        st.error("Enter your OpenAI API key in the sidebar on the Home page.")
        st.stop()
    with st.spinner("Generating insights…"):
        try:
            st.session_state[KEY_INSIGHTS] = call_ai(api_key, model, PROMPT_INSIGHTS, CTX, 900)
            st.session_state[KEY_AGE]      = call_ai(api_key, model, PROMPT_AGE,      CTX, 400)
            st.session_state[KEY_DISC]     = call_ai(api_key, model, PROMPT_DISC,     CTX, 400)
            st.session_state[KEY_RECS]     = call_ai(api_key, model, PROMPT_RECS,     CTX, 700)
            insights_so_far = "\n\n".join([
                st.session_state[KEY_INSIGHTS],
                st.session_state[KEY_AGE],
                st.session_state[KEY_DISC],
                st.session_state[KEY_RECS],
            ])
            st.session_state[KEY_SUMMARY] = call_ai(
                api_key, model, PROMPT_SUMMARY,
                CTX + "\n\nINSIGHTS & RECOMMENDATIONS:\n" + insights_so_far, 600
            )
        except Exception as e:
            st.error(f"API error: {e}")
            st.stop()

# ── Retrieve AI results ───────────────────────────────────────────────────────
insights_main = st.session_state.get(KEY_INSIGHTS, "")
insights_age  = st.session_state.get(KEY_AGE, "")
insights_disc = st.session_state.get(KEY_DISC, "")
insights_recs = st.session_state.get(KEY_RECS, "")
insights_sum  = st.session_state.get(KEY_SUMMARY, "")
 
# ═════════════════════════════════════════════════════════════════════════════
# 2. KPI ROW
# ═════════════════════════════════════════════════════════════════════════════
k1, k2, k3 = st.columns(3)
 
def kpi_card(col, label, value, sub=""):
    with col:
        st.markdown(f"""
        <div class='kpi-card'>
          <div class='kpi-label'>{label}</div>
          <div class='kpi-value'>{value}</div>
          {"<div style='font-size:11px;opacity:.8;margin-top:4px;'>"+sub+"</div>" if sub else ""}
        </div>""", unsafe_allow_html=True)
 
kpi_card(k1, "Rated the Show Excellent",    f"{pct_excellent}%",  f"n = {n:,} respondents")
kpi_card(k2, "Net Promoter Score",          f"{nps_score}",       f"avg score {nps_mean}/10")
kpi_card(k3, "Negative Feedback",           f"{pct_negative}%",   "score ≤ 6 / 10")
 
st.markdown("<div style='margin-top:18px'></div>", unsafe_allow_html=True)
 
# ═════════════════════════════════════════════════════════════════════════════
# 3. MAIN CONTENT — Insights (left) + Tables (right)
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='section-title'>Satisfaction & Engagement Analysis</div>",
            unsafe_allow_html=True)
 
left, right = st.columns([1.1, 0.9], gap="large")
 
# ── LEFT: numbered insight blocks ────────────────────────────────────────────
with left:
    if insights_main:
        lines  = [l.strip() for l in insights_main.split("\n") if l.strip()]
        blocks = []
        current = ""
        for line in lines:
            if line and line[0].isdigit() and ". " in line[:4]:
                if current:
                    blocks.append(current.strip())
                current = line
            else:
                current += " " + line
        if current:
            blocks.append(current.strip())

        for i, block in enumerate(blocks[:5], 1):
            text = block.lstrip("0123456789. ").strip()
            # Strip title if present (everything before first ": ")
            if ": " in text[:80]:
                _, body = text.split(": ", 1)
            else:
                body = text
            st.markdown(f"""
            <div style='padding:10px 0 10px 14px;border-left:3px solid {ORANGE};
                        margin-bottom:12px;'>
              <div class='insight-text'>{body}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown(placeholder("Click <b>🚀 Generate AI Insights</b> to load insights."),
                    unsafe_allow_html=True)
 
# ── RIGHT: two data tables ────────────────────────────────────────────────────
with right:
 
    def data_table(title, rows, total):
        max_count = max(c for _, c in rows) if rows else 1
        header = "<tr><th>Category</th><th>Count</th><th>%</th></tr>"
        body   = ""
        for cat, cnt in rows:
            pct   = cnt / total * 100 if total else 0
            bar_w = int(pct / max_count * 100 * (max_count / total))
            color = ORANGE if pct > 50 else "#F4A57A" if pct > 20 else "#F9C9A8"
            bar_w_px = int(pct)
            body += (f"<tr>"
                     f"<td>{cat}</td>"
                     f"<td style='text-align:right;'>{cnt:,}</td>"
                     f"<td><span class='pct-bar' style='width:{bar_w_px}px;"
                     f"background:{color};'></span>{pct:.1f}%</td>"
                     f"</tr>")
        st.markdown(f"""
        <div class='card'>
          <div class='section-title'>{title}</div>
          <table class='data-table'><thead>{header}</thead><tbody>{body}</tbody></table>
        </div>""", unsafe_allow_html=True)
 
    data_table("Enjoyment Ratings",      enjoy_data,  n)
    data_table("Likelihood to Return",   return_data, n)
 
st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
 
# ═════════════════════════════════════════════════════════════════════════════
# 4. SECOND SECTION — Age Groups + Discovery
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("<hr class='div'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Audience Demographics & Discovery</div>",
            unsafe_allow_html=True)
 
row2_left, row2_right = st.columns([1, 1], gap="large")
 
# ── TOP LEFT: Age bar chart ───────────────────────────────────────────────────
with row2_left:
    age_labels = list(age_counts.keys())
    age_vals   = list(age_counts.values())
    age_colors = [ORANGE, "#F4A57A", "#F9C9A8"]
 
    fig_age = go.Figure(go.Bar(
        x=age_vals,
        y=age_labels,
        orientation="h",
        marker_color=age_colors,
        text=[f"{v:,}  ({v/n*100:.1f}%)" for v in age_vals],
        textposition="outside",
        textfont=dict(size=11, color="#555"),
    ))
    fig_age.update_layout(
        title=dict(text="Young people age groups attending",
                   font=dict(size=13, color="#333"), x=0),
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        margin=dict(l=10, r=80, t=40, b=20),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(tickfont=dict(size=12, color="#444")),
        height=220, bargap=0.35, showlegend=False,
    )
    st.plotly_chart(fig_age, use_container_width=True, config={"displayModeBar": False})
 
    # ── BOTTOM LEFT: Discovery chart ─────────────────────────────────────────
    disc_sorted = sorted(disc_counts.items(), key=lambda x: x[1], reverse=True)
    disc_labels = [d[0] for d in disc_sorted]
    disc_vals   = [d[1] for d in disc_sorted]
    disc_colors = [ORANGE if i == 0 else "#F4A57A" if i < 2 else "#F9C9A8"
                   for i in range(len(disc_vals))]
 
    fig_disc = go.Figure(go.Bar(
        x=disc_vals,
        y=disc_labels,
        orientation="h",
        marker_color=disc_colors,
        text=[f"{v:,}" for v in disc_vals],
        textposition="outside",
        textfont=dict(size=11, color="#555"),
    ))
    fig_disc.update_layout(
        title=dict(text="How audiences discovered Monkey Baa",
                   font=dict(size=13, color="#333"), x=0),
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        margin=dict(l=10, r=60, t=40, b=20),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(tickfont=dict(size=12, color="#444"), autorange="reversed"),
        height=300, bargap=0.3, showlegend=False,
    )
    st.plotly_chart(fig_disc, use_container_width=True, config={"displayModeBar": False})
 
# ── RIGHT column: age insights + discovery insights ───────────────────────────
with row2_right:
    if insights_age:
        lines = [l.strip() for l in insights_age.split("\n") if l.strip()]
        items = [l.lstrip("•- ").strip() for l in lines if l.startswith(("•", "-")) or l]
        li    = "".join(f"<li>{b}</li>" for b in items[:2])
        st.markdown(f"<div class='insight-box'><ul>{li}</ul></div>",
                    unsafe_allow_html=True)
    else:
        st.markdown(placeholder("Click <b>🚀 Generate AI Insights</b> to load demographic insights."),
                    unsafe_allow_html=True)

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
 
    if insights_disc:
        lines = [l.strip() for l in insights_disc.split("\n") if l.strip()]
        items = [l.lstrip("•- ").strip() for l in lines if l.startswith(("•", "-")) or l]
        li    = "".join(f"<li>{b}</li>" for b in items[:2])
        st.markdown(f"<div class='insight-box'><ul>{li}</ul></div>",
                    unsafe_allow_html=True)
    else:
        st.markdown(placeholder("Click <b>🚀 Generate AI Insights</b> to load marketing insights."),
                    unsafe_allow_html=True)
 
st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
 
# ═════════════════════════════════════════════════════════════════════════════
# 5. RECOMMENDATIONS
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("<hr class='div'>", unsafe_allow_html=True)
st.markdown("<div style='font-size:15px;font-weight:600;color:#333;"
            "margin-bottom:4px;'>Recommendations</div>", unsafe_allow_html=True)
st.markdown("<hr class='div'>", unsafe_allow_html=True)
 
if insights_recs:
    lines   = [l.strip() for l in insights_recs.split("\n") if l.strip()]
    rblocks = []
    current = ""
    for line in lines:
        if line and line[0].isdigit() and ". " in line[:4]:
            if current:
                rblocks.append(current.strip())
            current = line
        else:
            current += " " + line
    if current:
        rblocks.append(current.strip())

    for block in rblocks[:3]:
        text = block.lstrip("0123456789. ").strip()
        # Strip title if present
        if ": " in text[:80]:
            _, body = text.split(": ", 1)
        else:
            body = text
        # Also strip any **bold** markdown titles the model may add
        body = body.lstrip("*").strip()
        st.markdown(f"""
        <div class='rec-card'>
          <div class='rec-text'>{body}</div>
        </div>""", unsafe_allow_html=True)
else:
    st.markdown(placeholder("Click <b>🚀 Generate AI Insights</b> to load recommendations."),
                unsafe_allow_html=True)
 
st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
 
# ═════════════════════════════════════════════════════════════════════════════
# 6. SUMMARY
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("<hr class='div'>", unsafe_allow_html=True)
st.markdown("<div style='font-size:15px;font-weight:600;color:#333;"
            "margin-bottom:4px;'>Summary</div>", unsafe_allow_html=True)
st.markdown("<hr class='div'>", unsafe_allow_html=True)
 
if insights_sum:
    st.markdown(f"<div class='summary-box'>{insights_sum}</div>",
                unsafe_allow_html=True)
else:
    st.markdown(placeholder("Click <b>🚀 Generate AI Insights</b> to load the executive summary."),
                unsafe_allow_html=True)
 
st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)