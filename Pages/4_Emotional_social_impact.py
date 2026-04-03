import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Emotional & Social Impact – Monkey Baa",
    page_icon="🎭",
    layout="wide",
)

# ── Global styles ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #F5F0EA; }
  [data-testid="stSidebar"]          { background: #FDFAF6; }
  .page-header {
    display: flex; align-items: center; justify-content: space-between;
    background: white; border-radius: 14px; padding: 22px 32px;
    margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }
  .page-header h1 { margin:0; font-size:1.9rem; color:#333; }
  .page-header .subtitle { color:#777; font-size:.95rem; margin-top:4px; }
  .logo-circle {
    width:60px; height:60px; border-radius:50%;
    background:#E8673A; display:flex; align-items:center; justify-content:center;
    font-size:1.8rem;
  }
  .kpi-card {
    background:#E8673A; color:white; border-radius:14px;
    padding:22px 20px; text-align:center;
    box-shadow: 0 4px 12px rgba(232,103,58,0.25);
  }
  .kpi-value { font-size:2.2rem; font-weight:700; line-height:1.1; }
  .kpi-label { font-size:.82rem; opacity:.9; margin-top:6px; text-transform:uppercase; letter-spacing:.04em; }
  .kpi-delta { font-size:.78rem; margin-top:8px; background:rgba(255,255,255,.2);
               border-radius:20px; padding:2px 10px; display:inline-block; }
  .card { background:white; border-radius:14px; padding:24px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.05); height: 100%; }
  .card-title { font-size:1.05rem; font-weight:600; color:#333; margin-bottom:16px; }
  .insight-box { background:#FDF3EE; border-radius:12px; padding:20px 24px;
                 border-left:4px solid #E8673A; }
  .insight-box ul { margin:0; padding-left:18px; color:#555; }
  .insight-box li { margin-bottom:8px; line-height:1.55; }
  .progress-row { display:flex; align-items:center; margin-bottom:11px; gap:10px; }
  .progress-emotion { width:130px; font-size:.85rem; color:#444; flex-shrink:0; }
  .progress-bar-bg { flex:1; background:#F0EBE3; border-radius:20px; height:14px; overflow:hidden; }
  .progress-bar-fill { height:100%; border-radius:20px;
                       background: linear-gradient(90deg, #E8673A, #F4A57A); }
  .progress-pct { width:44px; font-size:.82rem; color:#777; text-align:right; flex-shrink:0; }
  .footer-box { background:white; border-radius:14px; padding:24px 32px;
                margin-top:24px; box-shadow:0 2px 8px rgba(0,0,0,0.05);
                border-top: 4px solid #E8673A; }
  .footer-box h3 { color:#333; font-size:1.05rem; margin:0 0 10px 0; }
  .footer-box p  { color:#555; line-height:1.65; margin:0; font-size:.93rem; }
  .section-title { font-size:1.15rem; font-weight:600; color:#333;
                   margin: 24px 0 14px 0; padding-bottom:8px; border-bottom:2px solid #E8673A; }
</style>
""", unsafe_allow_html=True)

# ── Read shared state set by app.py — NO sidebar uploader on this page ────────
api_key = st.session_state.get("api_key", "")
model   = st.session_state.get("model", "gpt-4o")
df_raw  = st.session_state.get("df_survey", None)

# ── Header (always visible) ───────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <div>
    <h1>💛 Fostering Emotional Literacy</h1>
    <div class="subtitle">Emotional &amp; Social Impact · Monkey Baa Theatre Survey Analysis</div>
  </div>
  <div class="logo-circle">🎭</div>
</div>
""", unsafe_allow_html=True)

# ── Guard ─────────────────────────────────────────────────────────────────────
if df_raw is None:
    st.warning("⬅️  Please upload the **Survey CSV** in the sidebar on the Home page first.")
    st.stop()

# ── Prepare data ──────────────────────────────────────────────────────────────
df = df_raw.copy()
df.columns = df.columns.str.strip()

EMOTION_COLS  = ["Happy", "Sad", "Surprised", "Bored", "Angry", "Confused", "Scared", "Curious"]
EMOTION_EMOJI = {"Happy":"😊","Curious":"🤔","Surprised":"😮","Scared":"😨",
                 "Sad":"😢","Confused":"😕","Bored":"😑","Angry":"😠"}
QUALITY_COLS  = ["Personal Meaning","Excellence","Aesthetic Experience",
                 "Creativity","Imagination","Belonging"]
QUALITY_ICONS = {"Personal Meaning":"🧠","Excellence":"⭐","Aesthetic Experience":"🎨",
                 "Creativity":"✨","Imagination":"💡","Belonging":"🤝"}

for col in EMOTION_COLS + QUALITY_COLS:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

for col in ["net-promoter-score","The performance was entertaining",
            "The performance was emotionally impactful"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

n = len(df)

emotion_pcts   = {c: round(100*df[c].sum()/n,1) for c in EMOTION_COLS if c in df.columns}
emotion_sorted = sorted(emotion_pcts.items(), key=lambda x: x[1], reverse=True)

quality_avgs   = {c: round(df[c].mean(),2) for c in QUALITY_COLS
                  if c in df.columns and df[c].notna().sum() > 0}
quality_sorted = sorted(quality_avgs.items(), key=lambda x: x[1], reverse=True)

nps          = round(df["net-promoter-score"].mean(), 1)               if "net-promoter-score" in df.columns else "N/A"
ent_score    = round(df["The performance was entertaining"].mean(), 1) if "The performance was entertaining" in df.columns else "N/A"
impact_score = round(df["The performance was emotionally impactful"].mean(), 1) if "The performance was emotionally impactful" in df.columns else "N/A"
pct_excellent = round(100*(df["overall-experience"]=="Excellent").sum()/n,1) if "overall-experience" in df.columns else "N/A"
pct_happy     = emotion_pcts.get("Happy", 0)

BEHAVIOR_MAP = {
    "Ask questions":        "Ask questions about the story or characters",
    "Imaginative play":     "Engage in imaginative play related to the show",
    "Made connections":     "Make connections to their own life or experiences",
    "Wanted to learn more": "Express a desire to learn more about the subject",
    "Cultural awareness":   "Become more aware of different cultures or viewpoints",
}
behavior_pcts  = {s: round(100*pd.to_numeric(df[c],errors="coerce").mean(),1)
                  for s,c in BEHAVIOR_MAP.items() if c in df.columns}
beh_sorted     = sorted(behavior_pcts.items(), key=lambda x: x[1], reverse=True)

# ── AI helper ─────────────────────────────────────────────────────────────────
def call_ai(key, mdl, prompt, context):
    from openai import OpenAI
    client = OpenAI(api_key=key)
    r = client.chat.completions.create(
        model=mdl,
        messages=[{"role":"system","content":prompt},
                  {"role":"user","content":f"Dataset summary:\n\n{context}"}],
        temperature=0.3, max_tokens=600,
    )
    return r.choices[0].message.content.strip()

# ─────────────────────────────────────────────────────────────────────────────
# KPI ROW
# ─────────────────────────────────────────────────────────────────────────────
k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(f"""<div class="kpi-card">
      <div class="kpi-value">{pct_happy}%</div>
      <div class="kpi-label">😊 Young People Felt Happy</div>
      <div class="kpi-delta">Top emotional response · n={n:,}</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-card">
      <div class="kpi-value">{pct_excellent}%</div>
      <div class="kpi-label">⭐ Rated Experience Excellent</div>
      <div class="kpi-delta">Overall satisfaction</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-card">
      <div class="kpi-value">{impact_score}/10</div>
      <div class="kpi-label">💫 Emotional Impact Score</div>
      <div class="kpi-delta">Entertainment: {ent_score}/10</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — Quality Metrics + AI Insight
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Artistic Quality Metrics — Audience Perception</div>',
            unsafe_allow_html=True)
c1, c2 = st.columns([1, 1], gap="large")

with c1:
    st.markdown('<div class="card"><div class="card-title">Ranking · 6 Quality Dimensions (avg / 10)</div>',
                unsafe_allow_html=True)
    for col, val in quality_sorted:
        icon  = QUALITY_ICONS.get(col, "")
        pct_w = round(100 * val / 10, 1)
        st.markdown(f"""<div class="progress-row">
          <div class="progress-emotion">{icon} {col}</div>
          <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{pct_w}%;"></div></div>
          <div class="progress-pct">{val}</div></div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="insight-box"><div class="card-title">🔍 Insight Interpretation</div>',
                unsafe_allow_html=True)
    KEY_Q = "esi_quality_insight"
    if st.button("✨ Generate AI Insights", key="btn_quality"):
        if not api_key:
            st.warning("Enter your OpenAI API key in the sidebar on the Home page.")
        else:
            ctx    = "\n".join([f"{c}: {v}/10" for c,v in quality_sorted])
            prompt = ("You are an arts analytics expert for Monkey Baa Theatre, an Australian children's theatre company. "
                      "Analyse these 6 artistic quality scores rated by audience members (scale 0-10). "
                      "Return exactly 3 bullet points for a theatre manager — each max 25 words. "
                      "Focus on strengths, gaps, and one actionable recommendation. Start each bullet with '•'.")
            with st.spinner("Analysing…"):
                st.session_state[KEY_Q] = call_ai(api_key, model, prompt, ctx)

    if KEY_Q in st.session_state:
        bullets = [b.strip() for b in st.session_state[KEY_Q].split("\n") if b.strip()]
        st.markdown("<ul>" + "".join(f"<li>{b.lstrip('•').strip()}</li>" for b in bullets) + "</ul>",
                    unsafe_allow_html=True)
    else:
        top = quality_sorted[0]  if quality_sorted else ("Aesthetic Experience", 8.3)
        low = quality_sorted[-1] if quality_sorted else ("Belonging", 7.0)
        st.markdown(f"""<ul>
          <li><b>{top[0]}</b> leads at {top[1]}/10 — audiences respond strongly to this artistic dimension.</li>
          <li>Most dimensions score above 7/10, reflecting consistently strong artistic delivery.</li>
          <li><b>{low[0]}</b> ({low[1]}/10) is the lowest — consider community engagement initiatives to strengthen it.</li>
        </ul>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — Emotions Bar Chart + AI Bullets
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">😊 Emotional Responses During Performance</div>',
            unsafe_allow_html=True)
c3, c4 = st.columns([1.1, 0.9], gap="large")

with c3:
    labels = [f"{EMOTION_EMOJI.get(e,'')} {e}" for e,_ in emotion_sorted]
    values = [v for _,v in emotion_sorted]
    colors = ["#E8673A" if i==0 else "#F4A57A" if i<3 else "#F9C9A8" for i in range(len(values))]
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker_color=colors,
        text=[f"{v}%" for v in values], textposition="outside",
        textfont=dict(size=12, color="#555"),
    ))
    fig.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        margin=dict(l=10, r=60, t=20, b=30),
        xaxis=dict(title="% of Respondents", range=[0, max(values)*1.2],
                   gridcolor="#F0EBE3", tickfont=dict(color="#777")),
        yaxis=dict(autorange="reversed", tickfont=dict(size=13, color="#444")),
        height=340, bargap=0.3,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with c4:
    st.markdown('<div class="insight-box" style="height:100%;"><div class="card-title">🧠 Top 3 Manager Insights</div>',
                unsafe_allow_html=True)
    KEY_E = "esi_emotion_insight"
    if st.button("✨ Generate Emotion Insights", key="btn_emotion"):
        if not api_key:
            st.warning("Enter your OpenAI API key in the sidebar on the Home page.")
        else:
            ctx    = "\n".join([f"{e}: {v}% of young audience members" for e,v in emotion_sorted])
            prompt = ("You are an arts education expert for Monkey Baa Theatre, an Australian children's theatre company. "
                      "These are emotions felt by young people during live performances (% of respondents). "
                      "Return exactly 3 sharp bullet points for a theatre manager. Max 28 words each. "
                      "Cover: dominant emotion takeaway, emotional range meaning, and one strategic insight. "
                      "Start each bullet with '•'.")
            with st.spinner("Generating…"):
                st.session_state[KEY_E] = call_ai(api_key, model, prompt, ctx)

    if KEY_E in st.session_state:
        bullets = [b.strip() for b in st.session_state[KEY_E].split("\n") if b.strip()]
        st.markdown("<ul style='color:#555;'>" + "".join(f"<li>{b.lstrip('•').strip()}</li>" for b in bullets) + "</ul>",
                    unsafe_allow_html=True)
    else:
        top_e = emotion_sorted[0] if emotion_sorted else ("Happy", 91.9)
        st.markdown(f"""<ul style="color:#555;">
          <li><b>{top_e[0]}</b> ({top_e[1]}%) dominates — performances consistently create positive emotional experiences.</li>
          <li>Curiosity and Surprise appear frequently, signalling strong narrative engagement with young audiences.</li>
          <li>Low negative emotions suggest content is emotionally safe while remaining stimulating for children.</li>
        </ul>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — Post-Show Behaviours + Enjoyment Donut
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🌱 Post-Show Behaviours &amp; Social Learning</div>',
            unsafe_allow_html=True)
c5, c6 = st.columns([1, 1], gap="large")

with c5:
    st.markdown('<div class="card"><div class="card-title">What did young people do after the show?</div>',
                unsafe_allow_html=True)
    for label, pct in beh_sorted:
        st.markdown(f"""<div class="progress-row">
          <div class="progress-emotion" style="width:160px;">{label}</div>
          <div class="progress-bar-bg">
            <div class="progress-bar-fill"
                 style="width:{pct}%; background:linear-gradient(90deg,#4A90D9,#7AB8F5);"></div>
          </div>
          <div class="progress-pct">{pct}%</div></div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c6:
    st.markdown('<div class="card"><div class="card-title">📈 Enjoyment &amp; Satisfaction Snapshot</div>',
                unsafe_allow_html=True)
    enjoy_col = "How much did the young person enjoy the show?"
    if enjoy_col in df.columns:
        enjoy_counts = df[enjoy_col].value_counts()
        fig2 = go.Figure(go.Pie(
            labels=enjoy_counts.index, values=enjoy_counts.values,
            hole=0.55,
            marker_colors=["#E8673A","#F4A57A","#F9C9A8","#D0C4B8","#AAA"],
            textinfo="percent+label", textfont=dict(size=12),
        ))
        fig2.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            margin=dict(l=10,r=10,t=20,b=20), height=260, showlegend=False,
            annotations=[dict(text=f"NPS<br><b>{nps}</b>", x=0.5, y=0.5,
                              font_size=16, showarrow=False, font_color="#333")],
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER — Executive Summary
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📋 Executive Summary</div>', unsafe_allow_html=True)

KEY_S = "esi_exec_summary"
if st.button("✨ Generate Executive Summary", key="btn_summary"):
    if not api_key:
        st.warning("Enter your OpenAI API key in the sidebar on the Home page.")
    else:
        top_q   = quality_sorted[0]  if quality_sorted else ("N/A", "")
        low_q   = quality_sorted[-1] if quality_sorted else ("N/A", "")
        top_b   = beh_sorted[0]      if beh_sorted      else ("N/A", "")
        ctx = (f"Survey respondents: {n}\nFelt Happy: {pct_happy}%\n"
               f"Felt Curious: {emotion_pcts.get('Curious','N/A')}%\n"
               f"Felt Surprised: {emotion_pcts.get('Surprised','N/A')}%\n"
               f"Rated Excellent: {pct_excellent}%\nNPS: {nps}/10\n"
               f"Emotional Impact: {impact_score}/10\nEntertainment: {ent_score}/10\n"
               f"Top quality metric: {top_q[0]} {top_q[1]}/10\n"
               f"Lowest quality metric: {low_q[0]} {low_q[1]}/10\n"
               f"Top post-show behaviour: {top_b[0]} {top_b[1]}%\n")
        prompt = ("You are a senior analyst for Monkey Baa Theatre, an Australian children's theatre company. "
                  "Write a concise executive summary (max 4 lines, no bullet points, flowing prose) "
                  "for a board-level report on Emotional & Social Impact. "
                  "Highlight strengths, key findings, and one strategic recommendation.")
        with st.spinner("Writing summary…"):
            st.session_state[KEY_S] = call_ai(api_key, model, prompt, ctx)

low_dim  = quality_sorted[-1] if quality_sorted else ("belonging", 0)
top_beh  = beh_sorted[0]      if beh_sorted      else ("asking questions", 0)
default  = (f"Monkey Baa Theatre's productions generated strong emotional engagement across {n:,} survey "
            f"respondents, with {pct_happy}% of young audience members reporting happiness and {pct_excellent}% "
            f"rating their experience as Excellent. An emotional impact score of {impact_score}/10 and NPS of "
            f"{nps} confirm the company's ability to connect meaningfully with young audiences. Post-show "
            f"behaviours — particularly {top_beh[0].lower()} ({top_beh[1]}%) — demonstrate lasting educational "
            f"and social value; strengthening {low_dim[0].lower()} (currently {low_dim[1]}/10) represents the "
            f"clearest opportunity for future programming focus.")

st.markdown(f"""<div class="footer-box">
  <h3>📋 Executive Summary</h3>
  <p>{st.session_state.get(KEY_S, default)}</p>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)