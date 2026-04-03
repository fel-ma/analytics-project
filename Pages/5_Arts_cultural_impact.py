"""
pages/6_Arts_and_Cultural_Impact.py
=====================================
Report: Arts & Cultural Impact
OWNER: Persona 2

Data: Data_survey.csv (df_survey from session_state)
Theory of Change: Cultural Outcomes — Spark and Growth
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from openai import OpenAI

# ─────────────────────────────────────────────────────────
# Design tokens — same as all pages
# ─────────────────────────────────────────────────────────
ORANGE      = "#E8673A"
ORANGE_DARK = "#C4512A"
BEIGE       = "#F5F0EA"
WHITE       = "#FFFFFF"
GRAY_TEXT   = "#555555"
GREEN       = "#4CAF7D"
YELLOW      = "#F0A500"

st.markdown(f"""
<style>
  .stApp {{ background-color:{BEIGE}; }}

  .kpi-card {{
    background-color:{ORANGE}; border-radius:12px;
    padding:14px 12px; text-align:center; color:white;
  }}
  .kpi-label {{ font-size:11px; font-weight:500; opacity:.88; margin-bottom:3px; }}
  .kpi-value {{ font-size:28px; font-weight:700; line-height:1.1; }}
  .kpi-sub   {{ font-size:11px; opacity:.82; margin-top:3px; }}

  .card {{
    background-color:{WHITE}; border-radius:12px;
    padding:18px 22px; margin-bottom:12px;
  }}
  .insight-box {{
    background-color:#FDF3EE; border-radius:10px;
    padding:14px 16px; color:{GRAY_TEXT};
    font-size:13px; line-height:1.65;
  }}
  .insight-box ul {{ margin:0; padding-left:16px; }}
  .insight-box li {{ margin-bottom:8px; }}

  .section-label {{
    font-size:11px; font-weight:600; color:{ORANGE};
    text-transform:uppercase; letter-spacing:.7px; margin-bottom:3px;
  }}
  .section-title {{
    font-size:15px; font-weight:700; color:#333;
    margin-bottom:12px; padding-bottom:6px;
    border-bottom:2px solid {ORANGE}; display:inline-block;
  }}

  .summary-box {{
    background-color:{WHITE}; border-radius:12px;
    padding:18px 22px; color:{GRAY_TEXT};
    font-size:13px; line-height:1.78;
  }}

  hr.div {{ border:none; border-top:1px solid #e0d8d0; margin:6px 0 14px 0; }}

  /* Sentiment table */
  table.sent-table {{
    width:100%; border-collapse:collapse;
    font-size:12.5px; color:{GRAY_TEXT};
  }}
  table.sent-table th {{
    background-color:{ORANGE}; color:white;
    padding:8px 12px; text-align:left; font-weight:600;
  }}
  table.sent-table td {{ padding:8px 12px; border-bottom:1px solid #eee; }}
  table.sent-table tr.top-row td {{ background:#E8F5EE; font-weight:600; color:#2d6a4f; }}
  table.sent-table tr.low-row td {{ background:#FFF8E1; color:#7a5800; }}

  /* Weakness + rec cards */
  .weak-card {{
    background:#FFF8F5; border:1.5px solid #F2D0C0;
    border-radius:12px; padding:18px 20px;
  }}
  .weak-header {{
    display:flex; align-items:center; gap:10px; margin-bottom:10px;
  }}
  .warn-icon {{
    width:28px; height:28px; flex-shrink:0;
    background:#FFF8F5; border:1.5px solid {ORANGE};
    border-radius:6px; display:flex; align-items:center;
    justify-content:center; font-size:15px;
  }}
  .weak-title {{ font-size:13px; font-weight:700; color:#333; }}
  .weak-card ul {{
    margin:0; padding-left:18px;
    color:#555; font-size:13px; line-height:1.75;
  }}
  .weak-card li {{ margin-bottom:5px; }}

  .rec-primary {{
    background:linear-gradient(135deg,#FFF8F5 0%,#FDF0E8 100%);
    border:1.5px solid {ORANGE}; border-radius:12px;
    padding:20px 24px; display:flex; gap:16px; align-items:flex-start;
    margin-top:12px;
  }}
  .star-bg {{
    background:{ORANGE}; color:white; border-radius:50%;
    width:34px; height:34px; flex-shrink:0;
    display:flex; align-items:center; justify-content:center; font-size:17px;
  }}
  .rec-primary-title {{ font-size:14px; font-weight:700; color:#333; margin-bottom:8px; }}
  .rec-primary p {{ margin:0; color:#555; font-size:13px; line-height:1.75; }}

  .rec-section-title {{
    font-size:15px; font-weight:700; color:#333;
    margin:4px 0 14px 0; padding-bottom:8px;
    border-bottom:2px solid {ORANGE}; display:inline-block;
  }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# Data helpers
# ─────────────────────────────────────────────────────────
def compute_metrics(df):
    n = len(df)
    ae     = pd.to_numeric(df["Aesthetic Experience"], errors="coerce")
    cr     = pd.to_numeric(df["Creativity"],           errors="coerce")
    im     = pd.to_numeric(df["Imagination"],          errors="coerce")
    bl     = pd.to_numeric(df["Belonging"],            errors="coerce")
    pm     = pd.to_numeric(df["Personal Meaning"],     errors="coerce")

    happy       = pd.to_numeric(df["Happy"],   errors="coerce").fillna(0)
    curious     = pd.to_numeric(df["Curious"], errors="coerce").fillna(0)
    cult_aware  = pd.to_numeric(df["Become more aware of different cultures or viewpoints"], errors="coerce").fillna(0)
    ask_q       = pd.to_numeric(df["Ask questions about the story or characters"],          errors="coerce").fillna(0)
    desire_lrn  = pd.to_numeric(df["Express a desire to learn more about the subject"],    errors="coerce").fillna(0)
    connections = pd.to_numeric(df["Make connections to their own life or experiences"],   errors="coerce").fillna(0)
    imag_play   = pd.to_numeric(df["Engage in imaginative play related to the show"],      errors="coerce").fillna(0)

    prior_yes   = (df["Prior to attending, had the young person heard of the story before?"] == "Yes").sum()
    enjoyed_lot = (df["How much did the young person enjoy the show?"] == "They liked the show a lot").sum()

    ent = pd.to_numeric(df["The performance was entertaining"],        errors="coerce")
    emp = pd.to_numeric(df["The performance was emotionally impactful"], errors="coerce")

    return {
        "n": n,
        # KPIs
        "cultural_learning_n":    int((ae >= 7).sum()),
        "cultural_learning_pct":  round((ae >= 7).sum() / n * 100),
        "confidence_n":           int(connections.sum()),
        "confidence_pct":         round(connections.sum() / n * 100),
        "aus_stories_n":          int(prior_yes),
        "aus_stories_pct":        round(prior_yes / n * 100),
        # Sentiment categories
        "cat_cultural_learning":  int(((cult_aware == 1) | (ask_q == 1) | (desire_lrn == 1)).sum()),
        "cat_confidence":         int(((cr >= 7) | (im >= 7)).sum()),
        "cat_emotional":          int(((happy == 1) | (bl >= 7)).sum()),
        "cat_curiosity":          int(((curious == 1) | (connections == 1)).sum()),
        "cat_positive":           int(enjoyed_lot),
        # Extra
        "happy_n":                int((happy == 1).sum()),
        "curious_n":              int((curious == 1).sum()),
        "imaginative_play_n":     int((imag_play == 1).sum()),
        "entertaining_high_n":    int((ent >= 8).sum()),
        "emotionally_high_n":     int((emp >= 7).sum()),
        "ae_mean":                round(ae.mean(), 1),
        "cr_mean":                round(cr.mean(), 1),
        "im_mean":                round(im.mean(), 1),
        "bl_mean":                round(bl.mean(), 1),
    }


def build_context(m, df):
    n = m["n"]
    shows = df["What Monkey Baa show did you recently attend?"].value_counts().to_dict()
    shows_str = " | ".join(f"{k}: {v}" for k,v in shows.items())
    return f"""=== MONKEY BAA THEATRE — ARTS & CULTURAL IMPACT SURVEY ===
Total survey responses: {n}
Shows: {shows_str}

THEORY OF CHANGE — CULTURAL OUTCOMES:
"Young people see themselves in stories and feel validated."
"Young people develop curiosity and engagement with theatre."
"Young people develop a growing appreciation for theatre and the arts."
"Young people build increased cultural literacy and openness."
"A generation of lifelong arts engagers is cultivated."
"Australian storytelling is enriched and diversified."

CULTURAL IMPACT METRICS (of {n} respondents):

KPI 1 — Cultural Learning (Aesthetic Experience score >=7):
  {m['cultural_learning_n']} respondents ({m['cultural_learning_pct']}% of {n}) rated aesthetic experience >=7/10
  Mean aesthetic experience score: {m['ae_mean']}/10

KPI 2 — Confidence & Self-Expression (made connections to own life):
  {m['confidence_n']} ({m['confidence_pct']}% of {n}) reported the young person made connections to their own life

KPI 3 — Australian Stories Known:
  {m['aus_stories_n']} ({m['aus_stories_pct']}% of {n}) already knew the story before attending
  (indicator of Australian cultural story reach)

SENTIMENT CATEGORIES:
  Cultural Learning & Awareness (cultural awareness + questions + desire to learn):
    {m['cat_cultural_learning']} ({round(m['cat_cultural_learning']/n*100)}% of {n})
  Confidence & Self-Expression (Creativity or Imagination score >=7):
    {m['cat_confidence']} ({round(m['cat_confidence']/n*100)}% of {n})
  Emotional & Social Wellbeing (Happy or Belonging >=7):
    {m['cat_emotional']} ({round(m['cat_emotional']/n*100)}% of {n})
  Curiosity & Critical Thinking (Curious emotion or made life connections):
    {m['cat_curiosity']} ({round(m['cat_curiosity']/n*100)}% of {n})
  General Positive Engagement (liked the show a lot):
    {m['cat_positive']} ({round(m['cat_positive']/n*100)}% of {n})

ADDITIONAL CULTURAL INDICATORS:
  Happy emotion: {m['happy_n']} ({round(m['happy_n']/n*100)}% of {n})
  Curious emotion: {m['curious_n']} ({round(m['curious_n']/n*100)}% of {n})
  Engaged in imaginative play after show: {m['imaginative_play_n']} ({round(m['imaginative_play_n']/n*100)}% of {n})
  Rated performance highly entertaining (>=8/10): {m['entertaining_high_n']} ({round(m['entertaining_high_n']/n*100)}% of {n})
  Rated emotionally impactful (>=7/10): {m['emotionally_high_n']} ({round(m['emotionally_high_n']/n*100)}% of {n})
  Mean Creativity score: {m['cr_mean']}/10
  Mean Imagination score: {m['im_mean']}/10
  Mean Belonging score: {m['bl_mean']}/10

GAP INDICATORS (Theory of Change gaps):
  Only {5}% became more aware of different cultures/viewpoints (32 of {n})
  Only {m['confidence_pct']}% made explicit connections to their own life ({m['confidence_n']} of {n})
  Cultural learning is experiential but not always explicitly articulated by respondents
"""


def call_ai(api_key, model, system_prompt, context, max_tokens=800):
    r = OpenAI(api_key=api_key).chat.completions.create(
        model=model,
        messages=[{"role":"system","content":system_prompt},
                  {"role":"user","content":f"Data:\n{context}"}],
        temperature=0.3, max_tokens=max_tokens,
    )
    return r.choices[0].message.content.strip()


def bullets_html(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    items = [l for l in lines if l.startswith("•") or l.startswith("-")] or lines
    li    = "".join(f"<li>{b.lstrip('•- ').strip()}</li>" for b in items)
    return f"<div class='insight-box'><ul>{li}</ul></div>"

def placeholder(msg):
    return (f"<div class='insight-box' style='color:#bbb;font-style:italic;'>"
            f"{msg}</div>")


# ─────────────────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────────────────
df_survey = st.session_state.get("df_survey", None)
api_key   = st.session_state.get("api_key", "")
model     = st.session_state.get("model", "gpt-4o")

# ─────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown(f"""<div style='padding:4px 0'>
      <div style='font-size:11px;color:#999;letter-spacing:1px;
                  text-transform:uppercase;'>Monkey Baa Theatre</div>
      <div style='font-size:20px;font-weight:700;color:{ORANGE};
                  line-height:1.1;'>Arts & Cultural Impact</div>
      <div style='font-size:14px;font-weight:600;color:#333;
                  line-height:1.4;margin-top:2px;'>
        Daring and Inclusive Australian Stories:<br>
        <span style='color:#555;font-weight:500;'>
          Cultural Outcomes Impact (Spark and Growth)
        </span>
      </div>
    </div>""", unsafe_allow_html=True)
with h2:
    st.markdown("""<div style='text-align:right;padding-top:12px;font-size:22px;
                    font-weight:700;color:#222;font-style:italic;'>
      monkey baa</div>""", unsafe_allow_html=True)

st.markdown("<hr class='div'>", unsafe_allow_html=True)

if df_survey is None:
    st.warning("⬅️ Upload **Data_survey.csv** in the sidebar on the Home page first.")
    st.stop()

# ─────────────────────────────────────────────────────────
# Compute metrics
# ─────────────────────────────────────────────────────────
m   = compute_metrics(df_survey)
n   = m["n"]
ctx = build_context(m, df_survey)

# ─────────────────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────────────────
k1, k2, k3 = st.columns(3)
kpi_data = [
    (k1, "Cultural Learning",
     f"{m['cultural_learning_pct']}%",
     f"{m['cultural_learning_n']} of {n} — Aesthetic Experience ≥7"),
    (k2, "Confidence & Expression",
     f"{m['confidence_pct']}%",
     f"{m['confidence_n']} of {n} — Connected to own life"),
    (k3, "Australian Stories Known",
     f"YES {m['aus_stories_pct']}%",
     f"{m['aus_stories_n']} of {n} — Recognised the story"),
]
for col, label, value, sub in kpi_data:
    with col:
        st.markdown(f"""<div class='kpi-card'>
          <div class='kpi-label'>{label}</div>
          <div class='kpi-value'>{value}</div>
          <div class='kpi-sub'>{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# AI button + session state
# ─────────────────────────────────────────────────────────
run            = st.button("🚀 Generate AI Insights", type="primary")
ai_interpret   = st.session_state.get("aci_interpret",  None)
ai_sentiment   = st.session_state.get("aci_sentiment",  None)
ai_weak        = st.session_state.get("aci_weak",       None)
ai_rec         = st.session_state.get("aci_rec",        None)
ai_recdet      = st.session_state.get("aci_recdet",     None)
ai_summary     = st.session_state.get("aci_summary",    None)

if run:
    if not api_key:
        st.error("Enter your OpenAI API key in the sidebar on the Home page.")
        st.stop()
    with st.spinner("Generating cultural impact insights…"):
        try:
            # 1 — Insight Interpretation (5 bullets)
            ai_interpret = call_ai(api_key, model,
                f"""You are a cultural impact analyst for Monkey Baa Theatre, Australia.
Monkey Baa's Theory of Change — Cultural Outcomes (Spark):
"Young people see themselves in stories and feel validated."
"Young people develop curiosity and engagement with theatre."
Cultural Outcomes (Growth):
"Young people develop a growing appreciation for theatre and the arts."
"Young people build increased cultural literacy and openness."

You are writing the INSIGHT INTERPRETATION section — interpret WHAT THE KPIs MEAN
culturally. Do NOT repeat numbers mechanically — explain the significance.

Key data points to interpret:
- {m['cultural_learning_pct']}% ({m['cultural_learning_n']} of {n}) rated Aesthetic Experience ≥7
- {m['confidence_pct']}% ({m['confidence_n']} of {n}) made connections to their own life
- {m['aus_stories_pct']}% ({m['aus_stories_n']} of {n}) already knew the Australian story
- 92% (592 of {n}) felt Happy | 39% (249 of {n}) felt Curious
- Only 5% (32 of {n}) became more aware of different cultures/viewpoints

Return exactly 5 bullet points (starting with •). Each bullet must:
- Start with a bold label in this format: **Label:** then the insight text
- Be 1-2 sentences that explain cultural significance, not just restate numbers
- Reference a Theory of Change outcome explicitly

Structure:
• **Strong Cultural Reach:** [interpret aesthetic experience score culturally]
• **Identity & Belonging:** [interpret connections to own life + belonging score]
• **Australian Story Recognition:** [interpret prior knowledge culturally]
• **Emotional Engagement:** [interpret Happy + Curious emotions as cultural outcomes]
• **Cultural Gap:** [identify what is NOT yet being achieved — use the 5% stat]

RULE: Every % must show base — write "X% (N of {n})". Start with •.""",
                ctx)

            # 2 — AI-Generated Sentiment Table
            ai_sentiment = call_ai(api_key, model,
                f"""You are a cultural impact analyst for Monkey Baa Theatre, Australia.
Based on the survey data, create a Sentiment Analysis table for Cultural Outcomes.

Return ONLY this JSON, no markdown, no preamble:
{{
  "rows": [
    {{
      "category": "Cultural Learning & Awareness",
      "description": "1-sentence description of what this measures culturally",
      "count": {m['cat_cultural_learning']},
      "pct": {round(m['cat_cultural_learning']/n*100)},
      "highlight": "top"
    }},
    {{
      "category": "Confidence & Self-Expression",
      "description": "1-sentence description of what this measures culturally",
      "count": {m['cat_confidence']},
      "pct": {round(m['cat_confidence']/n*100)},
      "highlight": "normal"
    }},
    {{
      "category": "Emotional & Social Wellbeing",
      "description": "1-sentence description of what this measures culturally",
      "count": {m['cat_emotional']},
      "pct": {round(m['cat_emotional']/n*100)},
      "highlight": "normal"
    }},
    {{
      "category": "Curiosity & Critical Thinking",
      "description": "1-sentence description of what this measures culturally",
      "count": {m['cat_curiosity']},
      "pct": {round(m['cat_curiosity']/n*100)},
      "highlight": "normal"
    }},
    {{
      "category": "General Positive Engagement",
      "description": "1-sentence description of what this measures culturally",
      "count": {m['cat_positive']},
      "pct": {round(m['cat_positive']/n*100)},
      "highlight": "low"
    }}
  ],
  "insight": "1-2 sentence interpretation of what this table reveals about cultural outcomes overall"
}}
The descriptions must explain CULTURAL significance, not just restate what was measured.
Total responses = {n}.""",
                ctx)

            # 3 — TWO Weaknesses
            ai_weak = call_ai(api_key, model,
                f"""You are a strategic analyst for Monkey Baa Theatre, Australia.
Theory of Change cultural gap: "Young people do not see their diverse experiences
reflected in stories. A lack of representation diminishes their sense of belonging."

Based on the cultural impact survey data, identify exactly 2 key weaknesses.

Return ONLY this JSON, no markdown, no preamble:
{{
  "weakness_1": {{
    "title": "Weakness title (5-7 words, data-specific)",
    "points": [
      "Specific finding with number (X of {n} / X% of {n})",
      "Why this undermines the Theory of Change cultural outcomes goal",
      "Which audience segment or cultural outcome is most at risk"
    ]
  }},
  "weakness_2": {{
    "title": "Weakness title (5-7 words, different focus from weakness 1)",
    "points": [
      "Specific finding with number (X of {n} / X% of {n})",
      "Why this represents a barrier as defined in the Theory of Change",
      "Risk to long-term cultural mission if not addressed"
    ]
  }}
}}
Key gaps: only 5% (32 of {n}) became more aware of different cultures/viewpoints.
Only {m['confidence_pct']}% ({m['confidence_n']} of {n}) made explicit life connections.
Mean Creativity {m['cr_mean']}/10 and Imagination {m['im_mean']}/10 — room for improvement.
Every % must include the base number.""",
                ctx)

            # 4 — Primary Recommendation
            ai_rec = call_ai(api_key, model,
                f"""You are a strategic analyst for Monkey Baa Theatre, Australia.
Theory of Change cultural strategy: "We create theatre experiences that support emotional growth.
We develop and present original Australian theatre that reflects the diversity of young audiences.
We ensure our stories reflect a broad range of young people's lived experiences."

Based on the cultural impact data gaps, write ONE primary strategic recommendation.

Return ONLY this JSON, no markdown, no preamble:
{{
  "title": "Recommendation title (5-8 words, action-oriented)",
  "description": "3-4 sentences: (1) name the specific data gap with numbers (X of {n}),
  (2) link to Theory of Change cultural strategy, (3) propose concrete action,
  (4) state expected cultural outcome for young people."
}}
Every % must include the base number.""",
                ctx)

            # 5 — THREE Recommendation Details
            ai_recdet = call_ai(api_key, model,
                f"""You are a strategic analyst for Monkey Baa Theatre, Australia.
Theory of Change cultural activities:
- Creating theatre experiences that foster empathy through shared emotional storytelling
- Developing original Australian theatre reflecting diversity of young audiences
- Making young people feel seen and respected as legitimate participants in cultural life
- Building a generation of lifelong arts engagers

Provide exactly 3 detailed actionable recommendations addressing cultural impact gaps.

Return ONLY this JSON, no markdown, no preamble:
{{
  "items": [
    {{
      "title": "Embed Cultural Reflection Moments",
      "points": [
        "Specific action with current baseline (only 5% (32 of {n}) became culturally aware)",
        "How guided prompts during/after performances make cultural learning intentional"
      ]
    }},
    {{
      "title": "Reinforce Through Creative Expression",
      "points": [
        "Activities like role-play, drawing, storytelling linked to current gap ({m['confidence_pct']}% of {n} made life connections)",
        "How this strengthens confidence, self-expression and makes cultural outcomes visible"
      ]
    }},
    {{
      "title": "Strengthen Australian Story Representation",
      "points": [
        "Build on {m['aus_stories_pct']}% ({m['aus_stories_n']} of {n}) prior story recognition — deepen cultural diversity",
        "How this advances the Theory of Change goal of enriched and diversified Australian storytelling"
      ]
    }}
  ]
}}
Rewrite each point in your own words — use the baseline numbers but make the language strategic.""",
                ctx)

            # 6 — Summary (synthesises everything — called last)
            page_synthesis = f"""
=== RAW DATA ===
{ctx}

=== INSIGHT INTERPRETATION ===
{ai_interpret}

=== SENTIMENT TABLE INSIGHT ===
{ai_sentiment}

=== KEY WEAKNESSES (2) ===
{ai_weak}

=== PRIMARY RECOMMENDATION ===
{ai_rec}

=== RECOMMENDATION DETAILS (3) ===
{ai_recdet}
"""
            ai_summary = call_ai(api_key, model,
                f"""You are writing the EXECUTIVE SUMMARY for Monkey Baa Theatre's
Arts & Cultural Impact report. It appears at the bottom and must synthesise ALL
page findings into a strategic board-level conclusion.

Monkey Baa's Theory of Change cultural mission:
"Australian storytelling is enriched and diversified."
"A generation of lifelong arts engagers is cultivated."
"Young people build increased cultural literacy and openness."

Write ONE cohesive paragraph of 6-7 sentences that:
1. Opens with the headline cultural achievement (use exact numbers: X% (N of {n}))
2. Captures the emotional and social cultural impact (Happy, Curious, Belonging)
3. Addresses Australian story reach and representation data
4. Names the most critical cultural gaps and links to Theory of Change barriers
5. Summarises the strategic direction across the 3 recommendations in one sentence
6. Closes with the Theory of Change horizon: "a generation of lifelong arts engagers"

Board-quality conclusion. No headers. No bullet points.""",
                page_synthesis, max_tokens=600)

            st.session_state["aci_interpret"] = ai_interpret
            st.session_state["aci_sentiment"] = ai_sentiment
            st.session_state["aci_weak"]      = ai_weak
            st.session_state["aci_rec"]       = ai_rec
            st.session_state["aci_recdet"]    = ai_recdet
            st.session_state["aci_summary"]   = ai_summary

        except Exception as e:
            st.error(f"API error: {e}")
            st.stop()


# ─────────────────────────────────────────────────────────
# SECTION 2 — Insight Interpretation (card)
# ─────────────────────────────────────────────────────────
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Insight Interpretation</div>",
            unsafe_allow_html=True)
if ai_interpret:
    # Render bullets with bold label support
    lines = [l.strip() for l in ai_interpret.split("\n") if l.strip()]
    items = [l for l in lines if l.startswith("•") or l.startswith("-")] or lines
    li_html = ""
    for b in items:
        text = b.lstrip("•- ").strip()
        # Convert **Label:** to <strong>Label:</strong>
        import re
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        li_html += f"<li style='margin-bottom:10px;'>{text}</li>"
    st.markdown(
        f"<div class='insight-box'><ul style='margin:0;padding-left:16px;'>"
        f"{li_html}</ul></div>",
        unsafe_allow_html=True)
else:
    st.markdown(placeholder("Click <b>Generate AI Insights</b> to load interpretation."),
                unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# SECTION 3 — Sentiment Analysis Table (AI-generated) + Bar Chart
# ─────────────────────────────────────────────────────────
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Sentiment Analysis on Cultural Outcomes Impact</div>",
            unsafe_allow_html=True)

import json as _json_sent
import re as _re

# Parse AI sentiment or fall back to computed data
sent_rows = None
sent_insight = ""
if ai_sentiment:
    try:
        sd = _json_sent.loads(ai_sentiment)
        sent_rows    = sd.get("rows", [])
        sent_insight = sd.get("insight", "")
    except Exception:
        sent_rows = None

# Fallback rows if AI hasn't run or failed
if not sent_rows:
    sent_rows = [
        {"category": "Cultural Learning & Awareness",  "description": "Became culturally aware, asked questions, or desired to learn more",         "count": m["cat_cultural_learning"], "pct": round(m["cat_cultural_learning"]/n*100), "highlight": "top"},
        {"category": "Confidence & Self-Expression",   "description": "Rated Creativity or Imagination ≥7 — creative confidence indicators",        "count": m["cat_confidence"],         "pct": round(m["cat_confidence"]/n*100),         "highlight": "normal"},
        {"category": "Emotional & Social Wellbeing",   "description": "Felt Happy during show or rated Belonging ≥7 — social connection outcomes",   "count": m["cat_emotional"],          "pct": round(m["cat_emotional"]/n*100),          "highlight": "normal"},
        {"category": "Curiosity & Critical Thinking",  "description": "Felt Curious or made connections to their own life — reflective engagement",  "count": m["cat_curiosity"],          "pct": round(m["cat_curiosity"]/n*100),          "highlight": "normal"},
        {"category": "General Positive Engagement",    "description": "Reported the young person liked the show a lot — baseline satisfaction",      "count": m["cat_positive"],           "pct": round(m["cat_positive"]/n*100),           "highlight": "low"},
    ]

col_table, col_chart = st.columns([5, 5])

with col_table:
    rows_html = ""
    for row in sent_rows:
        name  = row.get("category", "")
        desc  = row.get("description", "")
        count = row.get("count", 0)
        pct   = row.get("pct", 0)
        hl    = row.get("highlight", "normal")
        if hl == "top":
            bg = "#E8F5EE"; tc = "#2d6a4f"; fw = "600"
        elif hl == "low":
            bg = "#FFF8E1"; tc = "#7a5800"; fw = "500"
        else:
            bg = "white"; tc = GRAY_TEXT; fw = "400"
        rows_html += f"""<tr style='background:{bg};'>
          <td style='font-weight:{fw};color:{tc};padding:8px 12px;
                     border-bottom:1px solid #eee;'>{name}</td>
          <td style='font-size:11px;color:#777;padding:8px 12px;
                     border-bottom:1px solid #eee;'>{desc}</td>
          <td style='font-weight:600;color:{tc};padding:8px 12px;
                     border-bottom:1px solid #eee;white-space:nowrap;'>
            {pct}%<br>
            <span style='font-size:10px;color:#aaa;font-weight:400;'>
              {count} of {n}
            </span>
          </td>
        </tr>"""
    st.markdown(f"""
    <table style='width:100%;border-collapse:collapse;font-size:12.5px;'>
      <thead><tr>
        <th style='background:{ORANGE};color:white;padding:8px 12px;
                   text-align:left;font-weight:600;'>Category</th>
        <th style='background:{ORANGE};color:white;padding:8px 12px;
                   text-align:left;font-weight:600;'>Cultural Significance</th>
        <th style='background:{ORANGE};color:white;padding:8px 12px;
                   text-align:left;font-weight:600;'>Share</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>""", unsafe_allow_html=True)

    if sent_insight:
        st.markdown(
            f"<div style='margin-top:10px;font-size:12px;color:#777;"
            f"font-style:italic;line-height:1.6;'>{sent_insight}</div>",
            unsafe_allow_html=True)

with col_chart:
    names_c  = [r.get("category","") for r in sent_rows]
    values_c = [r.get("pct", 0) for r in sent_rows]
    counts_c = [r.get("count",0) for r in sent_rows]
    colors_c = [
        GREEN  if r.get("highlight") == "top"  else
        YELLOW if r.get("highlight") == "low"  else
        "#F2B99B"
        for r in sent_rows
    ]
    short_names = [nm[:22]+"…" if len(nm)>22 else nm for nm in names_c]

    fig = go.Figure(go.Bar(
        x=values_c, y=short_names,
        orientation="h",
        marker=dict(color=colors_c, line=dict(color="white", width=0.5)),
        text=[f"{v}%" for v in values_c],
        textposition="outside",
        textfont=dict(size=11, color="#333"),
        hovertemplate="<b>%{y}</b><br>%{x}% (%{customdata} of "
                      + str(n) + ")<extra></extra>",
        customdata=counts_c,
    ))
    fig.update_layout(
        title=dict(text="Cultural Outcomes Distribution",
                   font=dict(size=13, color="#333", family="Arial"),
                   x=0.5, xanchor="center"),
        height=290,
        margin=dict(l=10, r=55, t=44, b=10),
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        xaxis=dict(ticksuffix="%", tickfont=dict(size=10, color="#333"),
                   showgrid=True, gridcolor="#f0f0f0", zeroline=False),
        yaxis=dict(tickfont=dict(size=10, color="#333"), showgrid=False),
        hoverlabel=dict(bgcolor=ORANGE, font_color="white", font_size=11),
    )
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})

st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# SECTION 4 — Key Findings & Recommendations (UNIFIED)
# ─────────────────────────────────────────────────────────
st.markdown("<div class='rec-section-title'>🔍 Key Findings & Recommendations</div>",
            unsafe_allow_html=True)

if not ai_weak and not ai_rec and not ai_recdet:
    st.markdown(
        "<div style='color:#bbb;font-style:italic;font-size:13px;padding:8px 0;'>"
        "Click <b>Generate AI Insights</b> above to load findings and recommendations.</div>",
        unsafe_allow_html=True)
else:
    import json as _json

    # ── TWO Weaknesses side by side ──────────────────────
    try:
        w = _json.loads(ai_weak) if ai_weak else {}
        w1_title  = w.get("weakness_1", {}).get("title",  "Key Weakness 1")
        w1_points = w.get("weakness_1", {}).get("points", [])
        w2_title  = w.get("weakness_2", {}).get("title",  "Key Weakness 2")
        w2_points = w.get("weakness_2", {}).get("points", [])
    except Exception:
        w1_title, w1_points = "Key Weakness 1", []
        w2_title, w2_points = "Key Weakness 2", []

    def make_li(points):
        return "".join(
            f"<li style='margin-bottom:5px;'>{p}</li>" for p in points)

    wc1, wc2 = st.columns(2)
    with wc1:
        st.markdown(f"""
        <div class='weak-card'>
          <div class='weak-header'>
            <div class='warn-icon'>⚠️</div>
            <div>
              <div style='font-size:10px;font-weight:600;color:{ORANGE};
                          text-transform:uppercase;letter-spacing:.6px;margin-bottom:2px;'>
                Key Weakness
              </div>
              <div class='weak-title'>{w1_title}</div>
            </div>
          </div>
          <ul style='margin:0;padding-left:18px;color:#555;
                     font-size:13px;line-height:1.75;'>
            {make_li(w1_points)}
          </ul>
        </div>""", unsafe_allow_html=True)
    with wc2:
        st.markdown(f"""
        <div class='weak-card'>
          <div class='weak-header'>
            <div class='warn-icon'>⚠️</div>
            <div>
              <div style='font-size:10px;font-weight:600;color:{ORANGE};
                          text-transform:uppercase;letter-spacing:.6px;margin-bottom:2px;'>
                Key Weakness
              </div>
              <div class='weak-title'>{w2_title}</div>
            </div>
          </div>
          <ul style='margin:0;padding-left:18px;color:#555;
                     font-size:13px;line-height:1.75;'>
            {make_li(w2_points)}
          </ul>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

    # ── Primary Recommendation ──────────────────────────
    try:
        r = _json.loads(ai_rec) if ai_rec else {}
        rec_title = r.get("title",       "Primary Recommendation")
        rec_desc  = r.get("description", "")
    except Exception:
        rec_title, rec_desc = "Primary Recommendation", ""

    if rec_desc:
        st.markdown(f"""
        <div class='rec-primary'>
          <div class='star-bg'>★</div>
          <div>
            <div class='rec-primary-title'>{rec_title}</div>
            <p>{rec_desc}</p>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

    # ── Recommendation Details ───────────────────────────
    try:
        rd = _json.loads(ai_recdet) if ai_recdet else {}
        rd_items = rd.get("items", [])
    except Exception:
        rd_items = []

    if rd_items:
        st.markdown("""
        <div style='background:#F7F4F1;border-radius:12px;padding:22px 24px;'>
          <div style='font-size:14px;font-weight:700;color:#333;
                      margin-bottom:16px;display:flex;align-items:center;gap:8px;'>
            <span style='color:#E8673A;font-size:16px;'>★</span>
            Recommendation Details
          </div>
        </div>""", unsafe_allow_html=True)

        for i, item in enumerate(rd_items):
            if i > 0:
                st.markdown(
                    "<div style='color:#E8673A;font-size:16px;"
                    "padding-left:18px;margin:2px 0 4px;'>↓</div>",
                    unsafe_allow_html=True)
            bullets = "".join(
                f"<li style='margin-bottom:4px;'>{p}</li>"
                for p in item.get("points", [])
            )
            st.markdown(f"""
            <div style='background:white;border-radius:10px;padding:14px 20px;
                        border-left:4px solid {ORANGE};margin-bottom:4px;'>
              <div style='font-size:13px;font-weight:700;color:{ORANGE_DARK};
                          margin-bottom:8px;'>
                {i+1} · {item.get('title','')}
              </div>
              <ul style='margin:0;padding-left:18px;color:#555;
                         font-size:12.5px;line-height:1.72;'>
                {bullets}
              </ul>
            </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────
st.markdown(
    "<div style='font-size:15px;font-weight:600;color:#333;margin-bottom:4px;'>"
    "Executive Summary</div>", unsafe_allow_html=True)
st.markdown("<hr class='div'>", unsafe_allow_html=True)
st.markdown(
    f"<div class='summary-box'>{ai_summary}</div>" if ai_summary
    else "<div class='summary-box' style='color:#bbb;font-style:italic;'>"
         "Click <b>Generate AI Insights</b> to generate the executive summary.</div>",
    unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# Download
# ─────────────────────────────────────────────────────────
if ai_summary:
    st.divider()
    md_report = f"""# Monkey Baa — Arts & Cultural Impact

**Cultural Learning:** {m['cultural_learning_pct']}% ({m['cultural_learning_n']} of {n}) |
**Confidence:** {m['confidence_pct']}% ({m['confidence_n']} of {n}) |
**Australian Stories:** {m['aus_stories_pct']}% ({m['aus_stories_n']} of {n})

## Insight Interpretation
{ai_interpret}

## Weakness
{ai_weak}

## Recommendation
{ai_rec}

## Recommendation Details
{ai_recdet}

## Executive Summary
{ai_summary}
"""
    st.download_button("📄 Download Report (.md)", md_report,
                       file_name="arts_cultural_impact.md",
                       mime="text/markdown")