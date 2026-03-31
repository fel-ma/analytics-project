"""
pages/3_Audience_Feedback.py
==============================
Report: Audience Feedback on Experience & Improvement
OWNER: Persona 1

Data: Data_survey.csv
Column used: 'Do you have any further comments or suggestions...'
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from openai import OpenAI

# ─────────────────────────────────────────────────────────
# Design — same tokens as page 2
# ─────────────────────────────────────────────────────────
ORANGE      = "#E8673A"
ORANGE_DARK = "#C4512A"
BEIGE       = "#F5F0EA"
WHITE       = "#FFFFFF"
GRAY_TEXT   = "#555555"
GREEN       = "#4CAF7D"
RED_SOFT    = "#E05252"
NEUTRAL_CLR = "#F0A500"

st.markdown(f"""
<style>
  .stApp {{ background-color:{BEIGE}; }}

  .kpi-card {{
    background-color:{ORANGE};border-radius:12px;
    padding:14px 12px;text-align:center;color:white;
  }}
  .kpi-card.green {{ background-color:{GREEN}; }}
  .kpi-card.neutral {{ background-color:{NEUTRAL_CLR}; }}
  .kpi-card.red {{ background-color:{RED_SOFT}; }}
  .kpi-label {{ font-size:11px;font-weight:500;opacity:.88;margin-bottom:3px; }}
  .kpi-value {{ font-size:28px;font-weight:700;line-height:1.1; }}
  .kpi-sub   {{ font-size:11px;opacity:.82;margin-top:2px; }}

  .card {{ background-color:{WHITE};border-radius:12px;padding:18px 22px;margin-bottom:12px; }}

  .insight-box {{
    background-color:#FDF3EE;border-radius:10px;
    padding:14px 16px;color:{GRAY_TEXT};font-size:13px;line-height:1.65;
  }}
  .insight-box ul {{ margin:0;padding-left:16px; }}
  .insight-box li {{ margin-bottom:8px; }}

  .testimonial {{
    background-color:#F9F5F2;border-left:4px solid {ORANGE};
    border-radius:0 10px 10px 0;padding:14px 18px;
    margin-bottom:10px;color:#444;font-size:13px;
    font-style:italic;line-height:1.65;
  }}
  .testimonial .author {{
    font-style:normal;font-weight:600;color:{ORANGE_DARK};
    font-size:12px;margin-top:8px;
  }}

  .improvement-card {{
    background-color:{WHITE};border:1.5px solid #e8ddd5;
    border-radius:10px;padding:14px 16px;margin-bottom:10px;
  }}
  .improvement-title {{
    font-size:13px;font-weight:700;color:{ORANGE_DARK};margin-bottom:6px;
  }}
  .improvement-quote {{
    font-style:italic;color:#666;font-size:12px;
    border-left:3px solid {ORANGE};padding-left:10px;line-height:1.6;
  }}

  .section-title {{
    font-size:13px;font-weight:600;color:#333;
    margin-bottom:8px;
  }}
  .summary-box {{
    background-color:{WHITE};border-radius:12px;
    padding:18px 22px;color:{GRAY_TEXT};font-size:13px;line-height:1.75;
  }}
  hr.div {{ border:none;border-top:1px solid #e0d8d0;margin:6px 0 14px 0; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────
COMMENTS_COL = "Do you have any further comments or suggestions on how we might be able to improve your future show experience?"

SKIP = {"no","nil","n/a","n/","none","no.","nope","na","no further suggestions",
        "no suggestions","no comment","no comments","not really","no i don't think you could make any improvements",
        "no everything was excellent","no it was brilliant","no it was wonderful",
        "no, it was excellent from all aspects."}

def load_comments(df: pd.DataFrame):
    raw = df[COMMENTS_COL].dropna()
    raw = raw[raw.str.strip().str.lower().apply(lambda x: x not in SKIP)]
    raw = raw[raw.str.len() > 15]
    # clean encoding artifacts
    clean = raw.str.replace("‚Äô","'").str.replace("‚Äù",'"').str.replace(
        "‚Ä¶","...").str.replace("‚≠ê","♥").str.replace("üòä","🩰").str.replace(
        "üôÇ","🙏").str.strip()
    return clean.tolist()

def has_kw(text, keywords):
    t = text.lower()
    return any(k in t for k in keywords)

def classify_sentiment(comments):
    pos_kw  = ["wonderful","fantastic","brilliant","excellent","loved","great","amazing",
               "superb","perfect","magical","beautiful","outstanding","fabulous","delightful",
               "enjoyed","incredible","spectacular","best","impressed","enchanting","awesome"]
    neg_kw  = ["improve","suggest","issue","problem","difficult","hard","disappoint","bad",
               "poor","parking","couldn","wasn","too long","too short","loud","muffled",
               "expensive","costly","confusing","missing","lack","better","more","less",
               "wish","would be good","unclear","didn't","could not","struggled"]
    pos, neg, neu = [], [], []
    for c in comments:
        is_pos = has_kw(c, pos_kw)
        is_neg = has_kw(c, neg_kw)
        if is_pos and not is_neg:
            pos.append(c)
        elif is_neg:
            neg.append(c)
        else:
            neu.append(c)
    return pos, neu, neg

def build_context_feedback(comments):
    sample = comments[:120]
    return f"""DATASET: Monkey Baa Theatre — Audience Feedback Survey
Total usable comments: {len(comments)}

SAMPLE COMMENTS (first 120):
""" + "\n---\n".join(sample)

def call_ai(api_key, model, system_prompt, context):
    r = OpenAI(api_key=api_key).chat.completions.create(
        model=model,
        messages=[{"role":"system","content":system_prompt},
                  {"role":"user","content":f"Data:\n{context}"}],
        temperature=0.3, max_tokens=700,
    )
    return r.choices[0].message.content.strip()

def bullets_html(text):
    lines  = [l.strip() for l in text.split("\n") if l.strip()]
    items  = [l for l in lines if l.startswith("•") or l.startswith("-")] or lines
    li     = "".join(f"<li>{b.lstrip('•- ').strip()}</li>" for b in items)
    return f"<div class='insight-box'><ul>{li}</ul></div>"

def placeholder(msg):
    return f"<div class='insight-box' style='color:#bbb;font-style:italic;'>{msg}</div>"


# ─────────────────────────────────────────────────────────
# Static data — real quotes extracted from the survey
# ─────────────────────────────────────────────────────────
POSITIVE_TESTIMONIALS = [
    {
        "quote": "No. It was a wonderful show. The acting, dancing and singing were superb and the simplistic rotating set was amazing. It was perfectly suited for young children — especially budding little ballerinas. My grand daughter's mum has now enrolled her in ballet classes due to my grand daughter's delight in wanting to be a ballerina on the stage.",
        "author": "Grandparent — Josephine Wants to Dance",
    },
    {
        "quote": "We absolutely loved the show, and will keep an eye out for future Monkey Baa productions. Our 4 year old daughter absolutely loved the show — she was mesmerised by every detail from the songs to the incredible costumes. It was her very first theatre experience.",
        "author": "Parent — Possum Magic, Newcastle",
    },
    {
        "quote": "Honestly the experience was magical. My three year old isn't one to sit for very long or be engaged in something. And she was mindblown — the whole experience had her entertained, laughing, curious. She still talks about the show and tells everyone about it.",
        "author": "Parent — Possum Magic",
    },
]

IMPROVEMENT_AREAS = [
    {
        "title": "🅿️  Parking & Wayfinding",
        "count": 12,
        "quote": "We arrived 30 minutes early but were unable to find a park and both myself and granddaughter became quite stressed and then had to run across campus to the show. Some advice on parking would have helped. We missed the first 10 minutes.",
    },
    {
        "title": "💰  Price / Value for Money",
        "count": 8,
        "quote": "It was almost $200 for our young family to attend. I don't want to devalue the actors but it was an expensive 50 minutes for us and may not be accessible for many families.",
    },
    {
        "title": "👶  Age Range Clarity",
        "count": 11,
        "quote": "The show was rated 3-8 but the magic scenes were sometimes quite frightening and my 3-year-old was quite upset. I heard a few other children a little bit scared too.",
    },
    {
        "title": "🔊  Audio / Sound Quality",
        "count": 7,
        "quote": "I could only just hear the dialogue. Noisy audience with kids and babies (understandably) so it was hard to hear. Felt like it could have been a tad louder.",
    },
    {
        "title": "🍴  Catering & Venue Amenities",
        "count": 5,
        "quote": "It would be great to have some other entertainment and activities for the children to do after the show in the big cafe area so we could enjoy and have something to eat afterwards.",
    },
]

TOPIC_DATA = {
    "Show / Performance": 195,
    "Family / Children":  152,
    "Duration / Timing":   62,
    "Venue & Access":      50,
    "Interaction":         28,
    "Costume / Design":    26,
    "Price / Value":       24,
    "Audio / Sound":       17,
    "Food & Catering":      9,
}


# ─────────────────────────────────────────────────────────
# Get shared data
# ─────────────────────────────────────────────────────────
df_survey = st.session_state.get("df_survey", None)
api_key   = st.session_state.get("api_key", "")
model     = st.session_state.get("model", "gpt-4o")


# ─────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown("""<div style='padding:4px 0'>
      <div style='font-size:11px;color:#999;letter-spacing:1px;text-transform:uppercase;'>
        Monkey Baa Theatre</div>
      <div style='font-size:20px;font-weight:700;color:#333;line-height:1.3;'>
        Audience Feedback on
        <span style='color:#E8673A;'>Experience & Improvement</span>
      </div>
    </div>""", unsafe_allow_html=True)
with h2:
    st.markdown("""<div style='text-align:right;padding-top:12px;font-size:22px;
                    font-weight:700;color:#222;font-style:italic;'>monkey baa</div>""",
                unsafe_allow_html=True)

st.markdown("<hr class='div'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# Load comments
# ─────────────────────────────────────────────────────────
if df_survey is None:
    st.warning("⬅️ Upload **Data_survey.csv** in the sidebar on the Home page first.")
    st.stop()

comments = load_comments(df_survey)
pos, neu, neg = classify_sentiment(comments)
total = len(comments)

# ─────────────────────────────────────────────────────────
# KPI CARDS — Sentiment
# ─────────────────────────────────────────────────────────
k1, k2, k3 = st.columns(3)
kpi_data = [
    (k1, "green",   "😊 Positive",              len(pos), f"{len(pos)/total*100:.0f}% of comments"),
    (k2, "neutral", "😐 Neutral",               len(neu), f"{len(neu)/total*100:.0f}% of comments"),
    (k3, "red",     "💬 Suggestions / Negative", len(neg), f"{len(neg)/total*100:.0f}% of comments"),
]
for col, css_class, label, count, sub in kpi_data:
    with col:
        st.markdown(f"""<div class='kpi-card {css_class}'>
          <div class='kpi-label'>{label}</div>
          <div class='kpi-value'>{count:,}</div>
          <div class='kpi-sub'>{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# AI button
# ─────────────────────────────────────────────────────────
run             = st.button("🚀 Generate AI Insights", type="primary")
ai_summary      = st.session_state.get("fb_summary",  None)
ai_insights     = st.session_state.get("fb_insights", None)

if run:
    if not api_key:
        st.error("Enter your OpenAI API key in the sidebar on the Home page.")
        st.stop()
    with st.spinner("Analysing feedback with AI…"):
        try:
            context = build_context_feedback(comments)

            ai_insights = call_ai(api_key, model,
                """You are an audience research analyst for an Australian children's theatre company.
Based on these survey comments, return exactly 4 bullet points (starting with •) covering:
- Overall sentiment of audience feedback
- Most praised aspects of the experience
- Most common logistical barriers (not artistic)
- One strategic opportunity to improve audience satisfaction
Be specific and data-driven. No headers, no markdown.""", context)

            ai_summary = call_ai(api_key, model,
                """You are a senior analyst writing an executive paragraph for Monkey Baa Theatre management.
Based on audience survey comments, write ONE paragraph (4-5 sentences) that:
- Opens with the overall positive sentiment and key highlights
- Acknowledges the main logistical barriers (parking, price, audio, age clarity)
- Emphasises these are operational, not artistic, issues
- Closes with a forward-looking recommendation
Professional, warm, and actionable tone. No headers or bullet points.""", context)

            st.session_state["fb_summary"]  = ai_summary
            st.session_state["fb_insights"] = ai_insights
        except Exception as e:
            st.error(f"API error: {e}")
            st.stop()


# ─────────────────────────────────────────────────────────
# SECTION 1 — Bar chart (topics) + AI insights
# ─────────────────────────────────────────────────────────
st.markdown("<div class='card'>", unsafe_allow_html=True)
c1, c2 = st.columns([5, 5])

with c1:
    topics  = list(TOPIC_DATA.keys())
    counts  = list(TOPIC_DATA.values())
    colors  = [ORANGE if c == max(counts) else "#F2B99B" for c in counts]

    sorted_pairs = sorted(zip(counts, topics, colors))
    counts_s  = [p[0] for p in sorted_pairs]
    topics_s  = [p[1] for p in sorted_pairs]
    colors_s  = [ORANGE if c == max(counts_s) else "#F2B99B" for c in counts_s]

    fig_bar = go.Figure(go.Bar(
        x=counts_s, y=topics_s,
        orientation="h",
        marker=dict(color=colors_s, line=dict(color="white", width=0.5)),
        text=counts_s,
        textposition="outside",
        textfont=dict(size=11, color="#333"),
        hovertemplate="<b>%{y}</b><br>Mentions: %{x}<extra></extra>",
    ))
    fig_bar.update_layout(
        title=dict(text="Topics Most Mentioned in Feedback",
                   font=dict(size=13, color="#333", family="Arial"), x=0.5, xanchor="center"),
        height=320,
        margin=dict(l=10, r=40, t=44, b=10),
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        xaxis=dict(showgrid=True, gridcolor="#f0f0f0", zeroline=False,
                   tickfont=dict(size=9, color="#333")),
        yaxis=dict(tickfont=dict(size=10, color="#333"), showgrid=False),
        hoverlabel=dict(bgcolor=ORANGE, font_color="white", font_size=11),
    )
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

with c2:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown(bullets_html(ai_insights) if ai_insights
                else placeholder("Click <b>Generate AI Insights</b> to load feedback analysis."),
                unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# SECTION 2 — Positive testimonials
# ─────────────────────────────────────────────────────────
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>⭐ Highlighted Positive Comments</div>",
            unsafe_allow_html=True)

t_cols = st.columns(3)
for col, t in zip(t_cols, POSITIVE_TESTIMONIALS):
    with col:
        st.markdown(f"""<div class='testimonial'>
          "{t['quote']}"
          <div class='author'>— {t['author']}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# SECTION 3 — Improvement areas with real quotes
# ─────────────────────────────────────────────────────────
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>🔧 Key Improvement Opportunities</div>",
            unsafe_allow_html=True)

col_a, col_b = st.columns(2)
for i, area in enumerate(IMPROVEMENT_AREAS):
    col = col_a if i % 2 == 0 else col_b
    with col:
        st.markdown(f"""<div class='improvement-card'>
          <div class='improvement-title'>{area['title']}
            <span style='float:right;background:{ORANGE};color:white;border-radius:20px;
                         padding:1px 9px;font-size:11px;font-weight:600;'>
              {area['count']} mentions
            </span>
          </div>
          <div class='improvement-quote'>"{area['quote']}"</div>
        </div>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────
st.markdown("<div style='font-size:15px;font-weight:600;color:#333;margin-bottom:4px;'>"
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
    md = f"""# Monkey Baa — Audience Feedback Report

**Total Comments Analysed:** {total:,}
**Positive:** {len(pos)} ({len(pos)/total*100:.0f}%) | **Neutral:** {len(neu)} ({len(neu)/total*100:.0f}%) | **Suggestions:** {len(neg)} ({len(neg)/total*100:.0f}%)

## Key Insights
{ai_insights}

## Executive Summary
{ai_summary}
"""
    st.download_button("📄 Download Report (.md)", md,
                       file_name="audience_feedback.md", mime="text/markdown")