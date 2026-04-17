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
# Sidebar Title
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### AI Reporting System")
    st.divider()

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
  [data-testid="stSidebarCollapseButton"] {{ display: none !important; }}

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
  [data-testid="stSidebar"] {{ background-color: #1F4A4E !important; }}
  [data-testid="stHeader"] {{ display: none !important; }}
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

def call_ai_json(api_key, model, system_prompt, context):
    """Call AI for JSON responses — higher token limit + strips markdown fences."""
    import re as _rj
    r = OpenAI(api_key=api_key).chat.completions.create(
        model=model,
        messages=[{"role":"system","content":system_prompt},
                  {"role":"user","content":f"Data:\n{context}"}],
        temperature=0.2, max_tokens=1200,
    )
    raw = r.choices[0].message.content.strip()
    raw = _rj.sub(r"^```(?:json)?\s*", "", raw)
    raw = _rj.sub(r"\s*```\s*$", "", raw).strip()
    return raw

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
ai_insights     = st.session_state.get("fb_insights", None)
ai_weak         = st.session_state.get("fb_weak",     None)
ai_rec          = st.session_state.get("fb_rec",      None)
ai_recdet       = st.session_state.get("fb_recdet",   None)
ai_summary      = st.session_state.get("fb_summary",  None)

if run:
    if not api_key:
        st.error("Enter your OpenAI API key in the sidebar on the Home page.")
        st.stop()
    with st.spinner("Analysing feedback with AI…"):
        try:
            context = build_context_feedback(comments)

            # ── Compute topic counts from live data ──────────────
            def _count(kws): return sum(has_kw(c, kws) for c in comments)
            cnt_parking  = _count(['park','parking','car park','wayfinding','signage','navigate'])
            cnt_age      = _count(['age','too young','older','suited','3 year','toddler','range','appropriate'])
            cnt_price    = _count(['price','value','money','cost','expensive','afford','ticket'])
            cnt_audio    = _count(['sound','audio','hear','loud','muffled','volume'])
            cnt_catering = _count(['food','eat','cater','cafe','drink','snack','merch'])

            # Build a live gaps summary for prompts
            gaps_feedback = (
                f"Top barriers by mention count (of {total} usable comments):\n"
                f"  Parking/Wayfinding: {cnt_parking} mentions\n"
                f"  Age Suitability/Range: {cnt_age} mentions\n"
                f"  Price/Value: {cnt_price} mentions\n"
                f"  Audio/Sound: {cnt_audio} mentions\n"
                f"  Catering/Amenities: {cnt_catering} mentions\n"
                f"  Suggestions/Negative total: {len(neg)} of {total} comments\n"
                f"  Positive: {len(pos)} of {total} | Neutral: {len(neu)} of {total}"
            )

            # ── Prompt 1: Bar chart insights — topics distribution ──
            ai_insights = call_ai(api_key, model,
                f"""You are an audience research analyst for Monkey Baa Theatre, Australia.
Theory of Change: "We create and tour theatre productions and make it easier
for young people to see our shows."

The bar chart shows how many comments mentioned each topic.
Topic counts from {total} usable comments:
  Show/Performance: {TOPIC_DATA['Show / Performance']} mentions
  Family/Children: {TOPIC_DATA['Family / Children']} mentions
  Duration/Timing: {TOPIC_DATA['Duration / Timing']} mentions
  Venue & Access: {TOPIC_DATA['Venue & Access']} mentions
  Interaction: {TOPIC_DATA['Interaction']} mentions
  Costume/Design: {TOPIC_DATA['Costume / Design']} mentions
  Price/Value: {TOPIC_DATA['Price / Value']} mentions
  Audio/Sound: {TOPIC_DATA['Audio / Sound']} mentions
  Food & Catering: {TOPIC_DATA['Food & Catering']} mentions

Return exactly 4 bullet points (starting with •) with bold labels explaining WHAT THE CHART SHOWS:
• **Dominant Topic:** [why Show/Performance dominates and what this means for the mission]
• **Family Focus:** [what the Family/Children volume reveals about the audience profile]
• **Operational Topics:** [what the cluster of Venue/Price/Audio/Food mentions signals]
• **Engagement Gap:** [what low Interaction mentions suggest about audience expectations]

Do NOT mention weaknesses or recommendations here — only interpret the chart topics.
No headers. No markdown beyond bold labels.""",
                context)

            # ── Prompt 2: TWO Weaknesses ──────────────────────
            ai_weak = call_ai_json(api_key, model,
                f"""You are a strategic analyst for Monkey Baa Theatre, Australia.
Theory of Change: "Young people miss out due to geographic, financial or social barriers.
Limited exposure to live performing arts restricts opportunities to engage, imagine, and grow."

Based on {total} audience feedback comments, identify exactly 2 key weaknesses
that create barriers to the audience experience and undermine the Theory of Change mission.

LIVE DATA — barriers identified from the comments:
{gaps_feedback}

Derive your weaknesses from the data above. Do not invent or assume.

Return ONLY this JSON, no markdown, no preamble:
{{
  "weakness_1": {{
    "title": "Weakness title (5-7 words, specific to feedback data)",
    "points": [
      "Specific finding with mention count from the data (X of {total} comments)",
      "Why this creates a barrier as defined in the Theory of Change",
      "Which audience segment is most affected"
    ]
  }},
  "weakness_2": {{
    "title": "Weakness title (5-7 words, different focus from weakness 1)",
    "points": [
      "Specific finding with mention count from the data (X of {total} comments)",
      "Why this undermines the mission of making theatre accessible and enjoyable",
      "Risk to audience retention and repeat attendance if not addressed"
    ]
  }}
}}
Every % must include the base number.""",
                context)

            # ── Prompt 3: Primary Recommendation ─────────────
            ai_rec = call_ai_json(api_key, model,
                f"""You are a strategic analyst for Monkey Baa Theatre, Australia.
Theory of Change strategy: "We connect with young people and their communities by bringing
high-quality theatre to them. We provide targeted access to theatre to young people in need."

LIVE DATA — barriers from {total} comments:
{gaps_feedback}

Write ONE primary strategic recommendation addressing the most impactful barrier.

Return ONLY this JSON, no markdown, no preamble:
{{
  "title": "Recommendation title (5-8 words, action-oriented)",
  "description": "3-4 sentences: (1) name the specific barrier with mention count from the data,
  (2) link to Theory of Change access strategy, (3) propose one concrete operational action,
  (4) state the expected improvement in audience reach or retention."
}}
Every % must include the base number.""",
                context)

            # ── Prompt 4: THREE Recommendation Details ────────
            ai_recdet = call_ai_json(api_key, model,
                f"""You are a strategic analyst for Monkey Baa Theatre, Australia.
Theory of Change activities:
- Touring extensively to provide regular theatre experiences across regional and urban Australia
- Partnering with local organisations to connect with young people nationally
- Making it easier for young people to see shows (removing barriers)

LIVE DATA — top barriers from {total} audience comments:
{gaps_feedback}

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
Use only mention counts from the data provided. Make language strategic.""",
                context)

            # ── Prompt 5: Executive Summary (synthesises all) ─
            page_synthesis = f"""
=== FEEDBACK DATA ===
{context}

=== BAR CHART INSIGHTS ===
{ai_insights}

=== KEY WEAKNESSES ===
{ai_weak}

=== PRIMARY RECOMMENDATION ===
{ai_rec}

=== RECOMMENDATION DETAILS ===
{ai_recdet}
"""
            ai_summary = call_ai(api_key, model,
                f"""You are writing the EXECUTIVE SUMMARY for Monkey Baa Theatre's
Audience Feedback report. It appears at the bottom and synthesises ALL findings
into a board-quality strategic conclusion.

Monkey Baa's Theory of Change mission:
"To uplift young Australians by embedding the arts into their formative years.
To ensure all young people have equitable access to creative experiences."

Write ONE cohesive paragraph of 6-7 sentences that:
1. Opens with the headline sentiment result — overall positive tone with numbers
   (X of {total} comments / X% of {total})
2. Highlights what audiences praised most (artistic quality, child engagement)
3. Acknowledges the operational barriers (parking, price, audio, age clarity)
   and frames them as non-artistic — the artistic experience is strong
4. Connects the barriers to the Theory of Change access mission
5. Summarises the 3 strategic recommendations in one forward-looking sentence
6. Closes with a statement about audience loyalty and the path to broader access

Board-quality conclusion. Purposeful, warm, actionable. No headers. No bullet points.""",
                page_synthesis)

            st.session_state["fb_insights"] = ai_insights
            st.session_state["fb_weak"]     = ai_weak
            st.session_state["fb_rec"]      = ai_rec
            st.session_state["fb_recdet"]   = ai_recdet
            st.session_state["fb_summary"]  = ai_summary

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
    if ai_insights:
        import re as _re
        lines = [l.strip() for l in ai_insights.split("\n") if l.strip()]
        items = [l for l in lines if l.startswith("•") or l.startswith("-")] or lines
        li_html = ""
        for b in items:
            text = b.lstrip("•- ").strip()
            text = _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
            li_html += f"<li style='margin-bottom:10px;'>{text}</li>"
        st.markdown(
            f"<div class='insight-box'><ul style='margin:0;padding-left:16px;'>"
            f"{li_html}</ul></div>", unsafe_allow_html=True)
    else:
        st.markdown(placeholder("Click <b>Generate AI Insights</b> to load feedback analysis."),
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
# SECTION 4 — Key Findings & Recommendations (UNIFIED)
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
  .weak-card {
    background-color:#FFF8F5; border:1.5px solid #F2D0C0;
    border-radius:12px; padding:18px 20px; height:100%;
  }
  .weak-header { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
  .warn-icon {
    width:28px; height:28px; flex-shrink:0;
    background:#FFF8F5; border:1.5px solid #E8673A;
    border-radius:6px; display:flex; align-items:center;
    justify-content:center; font-size:15px;
  }
  .weak-title { font-size:13px; font-weight:700; color:#333; }
  .rec-primary {
    background:linear-gradient(135deg,#FFF8F5 0%,#FDF0E8 100%);
    border:1.5px solid #E8673A; border-radius:12px;
    padding:20px 24px; display:flex; gap:16px;
    align-items:flex-start; margin-top:12px;
  }
  .star-bg {
    background:#E8673A; color:white; border-radius:50%;
    width:34px; height:34px; flex-shrink:0;
    display:flex; align-items:center; justify-content:center; font-size:17px;
  }
  .rec-primary-title { font-size:14px; font-weight:700; color:#333; margin-bottom:8px; }
  .rec-section-title {
    font-size:15px; font-weight:700; color:#333;
    margin:4px 0 14px 0; padding-bottom:8px;
    border-bottom:2px solid #E8673A; display:inline-block;
  }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='rec-section-title'>🔍 Key Findings & Recommendations</div>",
            unsafe_allow_html=True)

if not ai_weak and not ai_rec and not ai_recdet:
    st.markdown(
        "<div style='color:#bbb;font-style:italic;font-size:13px;padding:8px 0;'>"
        "Click <b>Generate AI Insights</b> above to load findings and recommendations.</div>",
        unsafe_allow_html=True)
else:
    import json as _json
    import re as _re2

    # ── TWO Weaknesses side by side ───────────────────────
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
                Key Weakness</div>
              <div class='weak-title'>{w1_title}</div>
            </div>
          </div>
          <ul style='margin:0;padding-left:18px;color:#555;font-size:13px;line-height:1.75;'>
            {make_li(w1_points)}</ul>
        </div>""", unsafe_allow_html=True)
    with wc2:
        st.markdown(f"""
        <div class='weak-card'>
          <div class='weak-header'>
            <div class='warn-icon'>⚠️</div>
            <div>
              <div style='font-size:10px;font-weight:600;color:{ORANGE};
                          text-transform:uppercase;letter-spacing:.6px;margin-bottom:2px;'>
                Key Weakness</div>
              <div class='weak-title'>{w2_title}</div>
            </div>
          </div>
          <ul style='margin:0;padding-left:18px;color:#555;font-size:13px;line-height:1.75;'>
            {make_li(w2_points)}</ul>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

    # ── Primary Recommendation ────────────────────────────
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
            <p style='margin:0;color:#555;font-size:13px;line-height:1.75;'>{rec_desc}</p>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

    # ── THREE Recommendation Details ─────────────────────
    try:
        rd       = _json.loads(ai_recdet) if ai_recdet else {}
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
                for p in item.get("points", []))
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