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

# ── Styles — exact copy of page 2 pattern ────────────────
st.markdown(f"""
<style>
  .stApp {{ background-color: {BEIGE}; }}
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
    import json
    try:
        rec_data  = json.loads(ins_rec)
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

# ── Download ──────────────────────────────────────────────
if ins_sum:
    st.divider()
    md = f"""# Monkey Baa — Emotional & Social Impact
**Happy:** {pct_happy}% | **Excellent:** {pct_excellent}% | **Impact:** {impact_score}/10

## Quality Insights
{ins_q}

## Emotion Insights
{ins_e}

## Summary
{ins_sum}
"""
    st.download_button("📄 Download Report (.md)", md,
                       file_name="emotional_social_impact.md", mime="text/markdown")