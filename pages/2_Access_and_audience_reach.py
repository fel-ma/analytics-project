"""
pages/2_Access_and_Audience_Reach.py
======================================
Report: Access & Audience Reach
OWNER: Persona 1
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from openai import OpenAI
from utils.styles import apply_styles

ORANGE      = "#E8673A"
ORANGE_DARK = "#C4512A"
BEIGE       = "#F5F0EA"
WHITE       = "#FFFFFF"
GRAY_TEXT   = "#555555"

apply_styles()


# ── Helpers ──────────────────────────────────────────────
def build_context(df):
    total     = df["Audience_n"].sum()
    total_ev  = pd.to_numeric(df["# of events"], errors="coerce").sum()
    total_v   = len(df)

    buf = [
        "=== MONKEY BAA THEATRE — AUDIENCE DATA 2021-2025 ===",
        f"Total young people reached: {int(total):,}",
        f"Total performances delivered: {int(total_ev):,}",
        f"Total venue visits: {total_v}",
        f"States/territories covered: {df['State'].nunique()} of 8",
        "",
        "THEORY OF CHANGE CONTEXT:",
        "Monkey Baa's mission is to expand access to live theatre for young people,",
        "especially those facing geographic, financial or social barriers.",
        "Key outputs tracked: # performances, # regional/remote venues,",
        "# young people attending, # communities reached.",
        "Goal: equity in cultural access across Australia.",
    ]

    # Year-on-year with growth rates
    buf.append("\nAUDIENCE BY YEAR (with growth):")
    yearly = df.groupby("Year")["Audience_n"].sum()
    yearly_ev = df.groupby("Year").apply(lambda x: pd.to_numeric(x["# of events"], errors="coerce").sum())
    prev = None
    for y, v in yearly.items():
        ev = int(yearly_ev[y])
        if prev:
            growth = (v - prev[1]) / prev[1] * 100
            buf.append(f"  {int(y)}: {int(v):,} young people | {ev} performances | growth: {growth:+.0f}% vs {int(prev[0])}")
        else:
            buf.append(f"  {int(y)}: {int(v):,} young people | {ev} performances")
        prev = (y, v)

    # State with full context
    buf.append(f"\nAUDIENCE BY STATE (of {int(total):,} total):")
    state_aud = df.groupby("State")["Audience_n"].sum().sort_values(ascending=False)
    state_ev  = df.groupby("State").apply(lambda x: pd.to_numeric(x["# of events"], errors="coerce").sum())
    for s, v in state_aud.items():
        buf.append(f"  {s}: {int(v):,} ({v/total*100:.1f}% of {int(total):,}) | {int(state_ev[s])} performances")

    # Region with full context — ToC critical metric
    buf.append(f"\nGEOGRAPHIC REACH — ToC metric (of {int(total):,} total audience):")
    for r, v in df.groupby("Regional II")["Audience_n"].sum().items():
        ev  = pd.to_numeric(df[df["Regional II"]==r]["# of events"], errors="coerce").sum()
        ven = len(df[df["Regional II"]==r])
        buf.append(f"  {r}: {int(v):,} young people ({v/total*100:.1f}% of {int(total):,}) | {int(ev)} performances | {ven} venues")

    # School vs community — ToC access indicator
    buf.append(f"\nACCESS TYPE — school vs community (of {int(total):,} total):")
    for s, v in df.groupby("school")["Audience_n"].sum().items():
        ev = pd.to_numeric(df[df["school"]==s]["# of events"], errors="coerce").sum()
        buf.append(f"  {s}: {int(v):,} young people ({v/total*100:.1f}% of {int(total):,}) | {int(ev)} performances")

    # Event types
    buf.append(f"\nEVENT TYPES (of {int(total_ev):,} total performances):")
    for t, v in df.groupby("Type")["Audience_n"].sum().sort_values(ascending=False).items():
        ev = pd.to_numeric(df[df["Type"]==t]["# of events"], errors="coerce").sum()
        buf.append(f"  {t}: {int(v):,} young people | {int(ev)} performances ({ev/total_ev*100:.1f}% of all performances)")

    # Gaps — explicit for AI
    buf.append("\nKEY GAPS (ToC access barriers):")
    remote_v = int(df[df["Regional II"]=="Remote"]["Audience_n"].sum())
    remote_pct = remote_v / total * 100
    school_v = int(df[df["school"]=="School"]["Audience_n"].sum())
    school_pct = school_v / total * 100
    low_states = ["TAS", "SA", "NT", "ACT"]
    low_total = int(state_aud[low_states].sum())
    buf.append(f"  Remote reach: only {remote_v:,} young people ({remote_pct:.1f}% of {int(total):,}) — critical gap")
    buf.append(f"  School engagement: only {school_v:,} young people ({school_pct:.1f}% of {int(total):,}) via schools")
    buf.append(f"  Low-coverage states (TAS+SA+NT+ACT): {low_total:,} combined ({low_total/total*100:.1f}% of {int(total):,})")

    return "\n".join(buf)

def call_ai(api_key, model, system_prompt, context, max_tokens=800):
    r = OpenAI(api_key=api_key).chat.completions.create(
        model=model,
        messages=[{"role":"system","content":system_prompt},
                  {"role":"user","content":f"Data:\n{context}"}],
        temperature=0.1, max_tokens=max_tokens,
    )
    return r.choices[0].message.content.strip()

def call_ai_json(api_key, model, system_prompt, context, max_tokens=1200):
    """Call AI for JSON responses — strips markdown fences + higher token limit."""
    import re as _rj
    r = OpenAI(api_key=api_key).chat.completions.create(
        model=model,
        messages=[{"role":"system","content":system_prompt},
                  {"role":"user","content":f"Data:\n{context}"}],
        temperature=0.1, max_tokens=max_tokens,
    )
    raw = r.choices[0].message.content.strip()
    raw = _rj.sub(r"^```(?:json)?\s*", "", raw)
    raw = _rj.sub(r"\s*```\s*$", "", raw).strip()
    return raw

def bullets_html(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    items = [l for l in lines if l.startswith("•") or l.startswith("-")] or lines
    li    = "".join(f"<li>{b.lstrip('•- ').strip()}</li>" for b in items)
    return f"<div class='insight-box'><ul>{li}</ul></div>"

def placeholder(msg):
    return f"<div class='insight-box' style='color:#bbb;font-style:italic;'>{msg}</div>"


# ── Data from session_state (loaded once in app.py) ──────
df      = st.session_state.get("df_audience", None)
api_key = st.session_state.get("api_key", "")
model   = st.session_state.get("model", "gpt-4o")

# ── Header ───────────────────────────────────────────────
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown("""<div style='padding:4px 0'>
      <div style='font-size:11px;color:#999;letter-spacing:1px;text-transform:uppercase;'>Monkey Baa Theatre</div>
      <div style='font-size:20px;font-weight:700;color:#333;line-height:1.3;'>
        Expanding Youth Theatre Access:
        <span style='color:#E8673A;'> Social Outcomes Impact</span></div>
    </div>""", unsafe_allow_html=True)
with h2:
    st.markdown("""<div style='text-align:right;padding-top:12px;font-size:22px;
                    font-weight:700;color:#222;font-style:italic;'>monkey baa</div>""",
                unsafe_allow_html=True)

st.markdown("<hr class='div'>", unsafe_allow_html=True)

if df is None:
    st.warning("⬅️ Upload **Audience_final_data.csv** in the sidebar on the Home page first.")
    st.stop()

# ── KPIs ─────────────────────────────────────────────────
total_audience  = int(df["Audience_n"].sum())
total_events    = int(pd.to_numeric(df["# of events"], errors="coerce").sum())
top_state       = df.groupby("State")["Audience_n"].sum().idxmax()
top_state_n     = int(df.groupby("State")["Audience_n"].sum().max())
regional_n      = int(df[df["Regional II"]=="Regional"]["Audience_n"].sum())
regional_pct    = regional_n / df["Audience_n"].sum() * 100
remote_n        = int(df[df["Regional II"]=="Remote"]["Audience_n"].sum())
remote_pct      = remote_n / df["Audience_n"].sum() * 100

k1, k2, k3 = st.columns(3)
kpi_items = [
    (k1, "Young People Reached",
     f"{total_audience:,}",
     f"across {total_events:,} performances"),
    (k2, "% Regional Audience",
     f"{regional_pct:.0f}%",
     f"{regional_n:,} of {total_audience:,}"),
    (k3, "Top Performing State",
     top_state,
     f"{top_state_n:,} young people"),
]
for col, label, value, sub in kpi_items:
    with col:
        st.markdown(f"""<div class='kpi-card'>
          <div class='kpi-label'>{label}</div>
          <div class='kpi-value'>{value}</div>
          <div style='font-size:11px;opacity:.82;margin-top:3px;'>{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)

# ── AI button ────────────────────────────────────────────
run              = st.button("🚀 Generate AI Insights", type="primary")
context          = build_context(df)
insights_main    = st.session_state.get("ar_main",      None)
insights_states  = st.session_state.get("ar_states",    None)
insights_region  = st.session_state.get("ar_region",    None)
insights_summary = st.session_state.get("ar_summary",   None)
insights_weak    = st.session_state.get("ar_weak",      None)
insights_rec     = st.session_state.get("ar_rec",       None)
insights_recdet  = st.session_state.get("ar_recdet",    None)

if run:
    if not api_key:
        st.error("Enter your OpenAI API key in the sidebar on the Home page.")
        st.stop()
    with st.spinner("Generating insights…"):
        try:
            # ── Pre-compute all key numbers from live data ──────
            total      = int(df["Audience_n"].sum())
            remote_n_  = int(df[df["Regional II"]=="Remote"]["Audience_n"].sum())
            remote_pct_= round(remote_n_ / total * 100, 1)
            reg_n_     = int(df[df["Regional II"]=="Regional"]["Audience_n"].sum())
            reg_pct_   = round(reg_n_ / total * 100, 1)
            metro_n_   = int(df[df["Regional II"]=="Metro"]["Audience_n"].sum())
            metro_pct_ = round(metro_n_ / total * 100, 1)
            school_n_  = int(df[df["school"]=="School"]["Audience_n"].sum()) if "school" in df.columns else 0
            school_pct_= round(school_n_ / total * 100, 1) if total else 0
            state_aud  = df.groupby("State")["Audience_n"].sum().sort_values(ascending=False)
            top2_states = list(state_aud.head(2).items())
            bot3_states = list(state_aud.tail(3).items())
            top_state_  = state_aud.idxmax()
            top_state_n_= int(state_aud.max())
            top_state_pct_ = round(top_state_n_ / total * 100, 1)
            yearly     = df.groupby("Year")["Audience_n"].sum().sort_values()
            min_year   = int(yearly.idxmin()); min_yr_n = int(yearly.min())
            max_year   = int(yearly.idxmax()); max_yr_n = int(yearly.max())
            total_ev_  = int(pd.to_numeric(df["# of events"], errors="coerce").sum())
            n_states_  = df["State"].nunique()

            # Dynamic gap summary for prompts
            top2_str  = " | ".join(f"{s}: {int(v):,} ({v/total*100:.1f}% of {total:,})" for s,v in top2_states)
            bot3_str  = " | ".join(f"{s}: {int(v):,} ({v/total*100:.1f}% of {total:,})" for s,v in bot3_states)
            gaps_str  = (
                f"Remote: {remote_n_:,} young people ({remote_pct_}% of {total:,}) — "
                f"Regional: {reg_n_:,} ({reg_pct_}% of {total:,}) — "
                f"Metro: {metro_n_:,} ({metro_pct_}% of {total:,}) — "
                f"School engagement: {school_n_:,} ({school_pct_}% of {total:,}) — "
                f"States covered: {n_states_} — "
                f"Top state: {top_state_} ({top_state_n_:,} / {top_state_pct_}%) — "
                f"Lowest 3 states: {bot3_str} — "
                f"Peak year: {max_year} ({max_yr_n:,}) — "
                f"Lowest year: {min_year} ({min_yr_n:,})"
            )

            # ── Prompt 1: Line chart ─────────────────────────────
            insights_main = call_ai(api_key, model,
                f"""You are an impact analyst for Monkey Baa Theatre, an Australian children's theatre company.
Monkey Baa's Theory of Change goal for this section:
EXPAND ACCESS to live theatre for young people, especially those facing geographic, financial or social barriers.

Your task is to generate insights for the AUDIENCE TREND OVER TIME line chart.
Focus EXCLUSIVELY on temporal patterns:
- growth over time
- peak years
- declines or stagnation
- what the trend suggests about continuity and scale of access

Important writing principles:
- Use ONLY the data provided
- Do NOT guess causes, drivers, or explanations unless explicitly supported by the data
- If the data does not explain why something happened, describe the pattern only
- Do NOT overclaim impact
- Keep insights clear, explainable, and grounded in the chart values
- Support internal decision-making by identifying meaningful patterns, risks, or opportunities
- Use professional, concise Australian English

Return exactly 4 bullet points.
Each bullet must:
- start with •
- contain exactly 2 sentences
- be 30–50 words total
- use exact years and numbers from the data
- avoid vague language

Required structure:
1. Describe the overall audience trajectory using exact years and values from the data
2. Identify the peak year using exact numbers and explain what that peak indicates about scale of reach, without guessing causes
3. Identify any decline, stagnation, or recovery using exact years and values, and explain what this means for continuity of access
4. Connect the trend to the Theory of Change by assessing whether audience reach appears to be expanding, fluctuating, or constrained over time

Style requirements:
- Be analytical, clear, and easy to understand
- Use cautious interpretation language such as "indicates", "suggests", or "reflects"
- Do NOT use headers
- Do NOT use markdown beyond the bullet symbol

Number rules:
- Use ONLY numbers that appear in the data
- Every percentage must include its base in the format: X% (N of {total:,})
- If a percentage cannot be calculated directly from the provided data, do not create one
- If a required value is missing, write "data not available"
- Never estimate, infer missing values, or fabricate causes

Example of good style:
• Audience reach increased from 52,400 in 2021 to 98,700 in 2023, showing strong expansion over the first half of the period. This pattern suggests Monkey Baa widened its annual reach substantially during those years, supporting broader access to live theatre.

Example of bad style:
• Audience numbers improved a lot over time and the program clearly became more successful. This shows the strategy worked very well.""",
                context)

            # ── Prompt 2: Metro/Regional/Remote pie chart ────────
            insights_region = call_ai(api_key, model,
                f"""You are an equity analyst for Monkey Baa Theatre, an Australian children's theatre company.
Monkey Baa's Theory of Change states: "There is greater equity in cultural access across Australia.
Our focus on removing barriers ensures young people from communities experiencing entrenched
disadvantage gain equal opportunities to engage in the arts."

Analyse the geographic distribution in the data and return exactly 4 bullet points (starting with •).
Each bullet must be 2 sentences, 30-50 words total:
1. Describe the Metro vs Regional vs Remote split — what it means for equity of access
2. Identify which region type most aligns with the Theory of Change mission and why
3. Name the most underserved geographic segment with exact numbers from the data
4. Give one specific recommendation to improve geographic equity, grounded in the data

EXAMPLE of a good bullet (use this style):
• Remote communities received only 3,200 young people (0.9% of {total:,}), the smallest share of any region type. This critical gap directly undermines the Theory of Change goal of equitable access for young people facing geographic disadvantage.

STRICT RULES:
- Every % must include base: write "X% (N of {total:,} young people)".
- Before writing each bullet, verify the number exists in the dataset — if not, write "data not available".
- No headers. No markdown. Start each point with •.""",
                context)

            # ── Prompt 3: State table ────────────────────────────
            insights_states = call_ai(api_key, model,
                f"""You are an impact analyst for Monkey Baa Theatre, an Australian children's theatre company.
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
• NSW led with 142,300 young people reached (40.5% of {total:,}), followed by VIC at 89,400 (25.4% of {total:,}). Together these two states account for two-thirds of total access, creating a geographic concentration risk for the program's equity mission.

STRICT RULES:
- Every % must include base: write "X% (N of {total:,} young people)".
- Before writing each bullet, verify the number exists in the dataset — if not, write "data not available".
- No headers. No markdown. Start each point with •.""",
                context)

            st.session_state["ar_main"]   = insights_main
            st.session_state["ar_region"] = insights_region
            st.session_state["ar_states"] = insights_states

            # ── Prompt 4: Weaknesses (JSON) ──────────────────────
            insights_weak = call_ai_json(api_key, model,
                f"""You are a strategic analyst for Monkey Baa Theatre, an Australian children's theatre company.
Monkey Baa's Theory of Change identifies these barriers to access:
"Young people miss out due to geographic, financial or social barriers.
Limited exposure to live performing arts restricts opportunities to engage, imagine, and grow."

KEY DATA GAPS FROM THE CURRENT DATASET:
{gaps_str}

From all gaps in the data, select the 2 weaknesses with the largest gap between current
reach and Theory of Change target. Weakness 1 must be geographic. Weakness 2 must be
demographic or programmatic. Rank by scale of impact on young people missed.
Derive your findings from the data — do not assume or invent.

Return ONLY this JSON, no markdown, no preamble:
{{
  "weakness_1": {{
    "title": "Weakness title (5-7 words, derived from the data)",
    "points": [
      "Specific finding with exact number from the data (X of {total:,} young people / X% of {total:,})",
      "Why this undermines the Theory of Change access goal",
      "Which communities are most affected and scale of the gap"
    ]
  }},
  "weakness_2": {{
    "title": "Weakness title (5-7 words, different focus from weakness 1)",
    "points": [
      "Specific finding with exact number from the data (X of {total:,} young people / X% of {total:,})",
      "Why this represents a barrier as defined in the Theory of Change",
      "Risk to long-term mission if not addressed — be specific about the consequence"
    ]
  }}
}}
STRICT: Every % MUST include the base: write "X% (N of {total:,})".
If a number is not in the dataset, write "data not available" — never estimate.""",
                context)
            st.session_state["ar_weak"] = insights_weak

            # ── Prompt 5: Primary Recommendation (JSON) ──────────
            insights_rec = call_ai_json(api_key, model,
                f"""You are a strategic analyst for Monkey Baa Theatre, an Australian children's theatre company.
Monkey Baa's Theory of Change strategy: "Expand access to theatre for more young people.
We provide targeted access to theatre to young people in need via Theatre Unlimited.
We partner with local organisations to connect with young people nationally."

KEY DATA GAPS FROM THE CURRENT DATASET:
{gaps_str}

Based on the data gaps above, write ONE primary strategic recommendation that
directly advances the Theory of Change access strategy. Choose the gap with the
largest number of young people missed.

Return ONLY this JSON, no markdown, no preamble:
{{
  "title": "Recommendation title (5-8 words, action-oriented verb first)",
  "description": "3-4 sentences: (1) name the specific data gap with exact numbers from the dataset (X of {total:,}), (2) link it explicitly to one Theory of Change strategy activity, (3) propose one concrete and measurable action, (4) state the expected outcome in terms of additional young people reached."
}}
STRICT: Every % must include the base number. Use only numbers from the dataset.
If a number is not in the data, write "data not available" — never estimate.""",
                context)
            st.session_state["ar_rec"] = insights_rec

            # ── Prompt 6: Recommendation Details (JSON) ───────────
            insights_recdet = call_ai_json(api_key, model,
                f"""You are a strategic analyst for Monkey Baa Theatre, an Australian children's theatre company.
Monkey Baa's Theory of Change activities include:
- Touring extensively to provide regular theatre experiences across regional and urban Australia
- Providing targeted access via Theatre Unlimited to young people in need
- Partnering with local organisations to connect with young people nationally
- Developing new Australian works consulted with young people and schools

KEY DATA GAPS FROM THE CURRENT DATASET:
{gaps_str}

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
        "Specific action with current baseline number from the data (X of {total:,})",
        "How this advances the Theory of Change output metric — be specific about the target"
      ]
    }},
    {{
      "title": "Action title (5-8 words, ties to ToC activity, verb first)",
      "points": [
        "Specific action with current baseline number from the data (X of {total:,})",
        "How this addresses the Theory of Change access barrier — name the barrier explicitly"
      ]
    }},
    {{
      "title": "Action title (5-8 words, ties to ToC activity, verb first)",
      "points": [
        "Specific action targeting underserved segment from the data (X of {total:,})",
        "How this advances the Theory of Change equity goal — state the expected change"
      ]
    }}
  ]
}}
STRICT: Every % must include the base number. Use only numbers from the dataset.
If a number is not in the data, write "data not available" — never estimate.""",
                context)
            st.session_state["ar_recdet"] = insights_recdet

            # ── Prompt 7: Executive Summary (synthesises ALL) ─────
            page_synthesis = f"""
=== RAW DATA ===
{context}

=== TREND INSIGHTS (line chart 2021-2025) ===
{insights_main}

=== STATE TABLE INSIGHTS ===
{insights_states}

=== GEOGRAPHIC EQUITY INSIGHTS (Metro/Regional/Remote pie chart) ===
{insights_region}

=== KEY WEAKNESSES IDENTIFIED ===
{insights_weak}

=== PRIMARY RECOMMENDATION ===
{insights_rec}

=== DETAILED RECOMMENDATIONS ===
{insights_recdet}
"""
            insights_summary = call_ai(api_key, model,
                f"""You are writing the EXECUTIVE SUMMARY for Monkey Baa Theatre's
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
   (write all percentages as "X% (N of {total:,})")
4. Names the most critical weakness and links it to a specific Theory of Change barrier
5. Summarises the strategic direction from the recommendations in one sentence
6. Closes with a forward-looking statement tied to the Theory of Change horizon:
   "greater equity in cultural access across Australia"

This must land with weight as the final word a board member reads.
Professional, warm tone. No headers. No bullet points.""",
                page_synthesis,
                max_tokens=900)
            st.session_state["ar_summary"] = insights_summary
        except Exception as e:
            st.error(f"API error: {e}")
            st.stop()

# ── Section 1: Line chart interactive (Plotly) + insights ──
st.markdown("<div class='card'>", unsafe_allow_html=True)
c1, c2 = st.columns([4, 6])
with c1:
    yearly = df.groupby("Year")["Audience_n"].sum().reset_index()
    yearly["Year"] = yearly["Year"].astype(int)

    fig_line = go.Figure()

    # Shaded area under line
    fig_line.add_trace(go.Scatter(
        x=yearly["Year"], y=yearly["Audience_n"],
        mode="none", fill="tozeroy",
        fillcolor="rgba(232,103,58,0.10)",
        hoverinfo="skip", showlegend=False,
    ))

    # Main line + markers
    fig_line.add_trace(go.Scatter(
        x=yearly["Year"], y=yearly["Audience_n"],
        mode="lines+markers+text",
        line=dict(color=ORANGE, width=2.8, shape="spline", smoothing=0.5),
        marker=dict(size=9, color=ORANGE, line=dict(color="white", width=2)),
        text=[f"{int(v):,}" for v in yearly["Audience_n"]],
        textposition="top center",
        textfont=dict(size=10, color="#555"),
        hovertemplate="<b>%{x}</b><br>Audience: <b>%{y:,.0f}</b><extra></extra>",
        showlegend=False,
    ))

    fig_line.update_layout(
        title=dict(
            text="Total Audience Reached",
            font=dict(size=13, color="#333", family="Arial", weight="normal"),
            x=0.5, xanchor="center",
        ),
        height=270,
        margin=dict(l=50, r=20, t=44, b=40),
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        xaxis=dict(
            tickmode="array",
            tickvals=yearly["Year"].tolist(),
            ticktext=[str(y) for y in yearly["Year"].tolist()],
            tickfont=dict(size=11, color="#333", family="Arial"),
            linecolor="#ccc", linewidth=1.5,
            showgrid=False, zeroline=False,
            title=None,
        ),
        yaxis=dict(
            tickformat=",.0f",
            tickfont=dict(size=10, color="#333", family="Arial"),
            gridcolor="#f0f0f0", gridwidth=1,
            zeroline=True, zerolinecolor="#ddd", zerolinewidth=1,
            linecolor="#ccc", linewidth=1,
            title=None,
            rangemode="tozero",
            range=[0, yearly["Audience_n"].max() * 1.25],
        ),
        hoverlabel=dict(bgcolor=ORANGE, font_color="white", font_size=12, bordercolor=ORANGE),
    )
    st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})
with c2:
    st.markdown(bullets_html(insights_main) if insights_main
                else placeholder("Click <b>Generate AI Insights</b> to load analysis."),
                unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ── Section 2: insights left, table right ────────────────
st.markdown("<div class='card'>", unsafe_allow_html=True)
c3, c4 = st.columns([5, 5])
with c3:
    st.markdown(bullets_html(insights_states) if insights_states
                else placeholder("Insights will appear here after generation."),
                unsafe_allow_html=True)
with c4:
    sdf = df.groupby("State")["Audience_n"].sum().sort_values(ascending=False).reset_index()
    sdf.columns = ["State","Audience"]
    sdf["Audience"] = sdf["Audience"].round(0).astype(int)
    grand_total = sdf["Audience"].sum()
    sdf["% of total"] = sdf["Audience"].apply(
        lambda v: f"{v/grand_total*100:.1f}% of {grand_total:,}"
    )
    rows = "".join(
        f"<tr><td style='text-align:center;'>{r['State']}</td>"
        f"<td style='text-align:center;'>{r['Audience']:,}</td>"
        f"<td style='text-align:center;font-size:11px;color:#777;'>{r['% of total']}</td></tr>"
        for _, r in sdf.iterrows()
    )
    st.markdown(f"""
    <div style='font-size:13px;font-weight:600;color:#333;
                margin-bottom:6px;text-align:center;'>
      Audience by State
    </div>
    <table style='width:100%;border-collapse:collapse;font-size:12px;color:#333;
                  border:1.5px solid #d4c8be;'>
      <thead><tr>
        <th style='background-color:{ORANGE};color:white;padding:7px 10px;
                   text-align:center;border:1px solid #c85a2a;'>State</th>
        <th style='background-color:{ORANGE};color:white;padding:7px 10px;
                   text-align:center;border:1px solid #c85a2a;'>Audience</th>
        <th style='background-color:{ORANGE};color:white;padding:7px 10px;
                   text-align:center;border:1px solid #c85a2a;'>% of total</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <style>
      table tr td {{ border: 1px solid #ddd; padding: 5px 10px; }}
      table tr:nth-child(even) {{ background-color: #fdf6f2; }}
      table tr:hover {{ background-color: #fce8dc; }}
    </style>
    """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ── Section 3: Pie interactive (Plotly) + regional insights ──
st.markdown("<div class='card'>", unsafe_allow_html=True)
c5, c6 = st.columns([4, 6])
with c5:
    reg = df.groupby("Regional II")["Audience_n"].sum()
    for cat in ["Metro","Regional","Remote"]:
        if cat not in reg.index: reg[cat] = 0
    reg = reg[["Metro","Regional","Remote"]]
    total_reg = reg.sum()

    fig_pie = go.Figure(go.Pie(
        labels=reg.index.tolist(),
        values=reg.values.tolist(),
        hole=0.38,
        marker=dict(
            colors=["#E8673A", "#4CAF7D", "#C0392B"],
            line=dict(color="white", width=2.5),
        ),
        # Metro and Regional: percent inside | Remote: label+percent outside
        textposition=["inside", "inside", "outside"],
        textinfo="percent",
        textfont=dict(size=12, color="white"),
        insidetextorientation="horizontal",
        hovertemplate="<b>%{label}</b><br>Audience: %{value:,.0f}<br>Share: %{percent}<extra></extra>",
        pull=[0, 0, 0.15],
        direction="clockwise",
        sort=False,
    ))
    fig_pie.update_layout(
        title=dict(
            text="Audience by Region Type",
            font=dict(size=13, color="#333", family="Arial", weight="normal"),
            x=0.5, xanchor="center",
        ),
        height=290,
        margin=dict(l=20, r=20, t=44, b=30),
        paper_bgcolor=WHITE,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom", y=-0.15,
            xanchor="center", x=0.5,
            font=dict(size=12, color="#333"),
        ),
        hoverlabel=dict(bgcolor="#333", font_color="white", font_size=11),
    )
    st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
with c6:
    st.markdown(bullets_html(insights_region) if insights_region
                else placeholder("Geographic insights will appear after generation."),
                unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


# ── Recommendation Details Section ───────────────────────
st.markdown("""
<style>
  .rec-section-title {
    font-size:15px; font-weight:700; color:#333;
    margin:4px 0 14px 0; padding-bottom:8px;
    border-bottom: 2px solid #E8673A;
    display:inline-block;
  }
  .weak-card {
    background-color:#FFF8F5; border:1.5px solid #F2D0C0;
    border-radius:12px; padding:18px 20px; height:100%;
  }
  .weak-header {
    display:flex; align-items:center; gap:10px; margin-bottom:10px;
  }
  .warn-icon {
    width:28px; height:28px; flex-shrink:0;
    background:#FFF8F5; border:1.5px solid #E8673A;
    border-radius:6px; display:flex; align-items:center;
    justify-content:center; font-size:15px;
  }
  .weak-title { font-size:13px; font-weight:700; color:#333; }
  .weak-card ul {
    margin:0; padding-left:18px;
    color:#555; font-size:13px; line-height:1.75;
  }
  .weak-card li { margin-bottom:5px; }

  .rec-primary {
    background:linear-gradient(135deg,#FFF8F5 0%,#FDF0E8 100%);
    border:1.5px solid #E8673A; border-radius:12px;
    padding:20px 24px; display:flex; gap:16px; align-items:flex-start;
    margin-top:12px;
  }
  .star-bg {
    background:#E8673A; color:white; border-radius:50%;
    width:34px; height:34px; flex-shrink:0;
    display:flex; align-items:center; justify-content:center; font-size:17px;
  }
  .rec-primary-title { font-size:14px; font-weight:700; color:#333; margin-bottom:8px; }
  .rec-primary p { margin:0; color:#555; font-size:13px; line-height:1.75; }

  .rec-detail-card {
    background-color:#F7F4F1; border-radius:12px;
    padding:22px 24px; margin-top:12px;
  }
  .rec-detail-header {
    font-size:14px; font-weight:700; color:#333;
    margin-bottom:16px; display:flex; align-items:center; gap:8px;
  }
  .rec-item {
    background:white; border-radius:10px; padding:14px 20px;
    margin-bottom:8px; border-left:4px solid #E8673A;
  }
  .rec-item-title {
    font-size:13px; font-weight:700; color:#C4512A; margin-bottom:8px;
  }
  .rec-item ul {
    margin:0; padding-left:18px;
    color:#555; font-size:12.5px; line-height:1.72;
  }
  .rec-item li { margin-bottom:4px; }
  .rec-connector { color:#E8673A; text-align:left; font-size:16px;
                   padding-left:18px; margin:4px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='rec-section-title'>🔍 Key Findings & Recommendations</div>",
            unsafe_allow_html=True)

# ── Only show this section after AI has run ───────────────
if not insights_weak and not insights_rec and not insights_recdet:
    st.markdown(
        "<div style='color:#bbb;font-style:italic;font-size:13px;padding:12px 0;'>"
        "Click <b>Generate AI Insights</b> above to load findings and recommendations.</div>",
        unsafe_allow_html=True)
else:
    # ── Parse Weaknesses ─────────────────────────────────
    import json as _json

    try:
        w_data    = _json.loads(insights_weak) if insights_weak else {}
        w1_title  = w_data.get("weakness_1", {}).get("title",  "Weakness 1")
        w1_points = w_data.get("weakness_1", {}).get("points", [])
        w2_title  = w_data.get("weakness_2", {}).get("title",  "Weakness 2")
        w2_points = w_data.get("weakness_2", {}).get("points", [])
    except Exception:
        w1_title, w1_points = "Weakness 1", []
        w2_title, w2_points = "Weakness 2", []

    def make_li(points):
        return "".join(f"<li style='margin-bottom:5px;'>{p}</li>" for p in points)

    wc1, wc2 = st.columns(2)
    with wc1:
        st.markdown(f"""
        <div class='weak-card'>
          <div class='weak-header'>
            <div class='warn-icon'>⚠️</div>
            <div>
              <div style='font-size:10px;font-weight:600;color:#E8673A;
                          text-transform:uppercase;letter-spacing:.6px;
                          margin-bottom:2px;'>Key Weakness</div>
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
              <div style='font-size:10px;font-weight:600;color:#E8673A;
                          text-transform:uppercase;letter-spacing:.6px;
                          margin-bottom:2px;'>Key Weakness</div>
              <div class='weak-title'>{w2_title}</div>
            </div>
          </div>
          <ul style='margin:0;padding-left:18px;color:#555;
                     font-size:13px;line-height:1.75;'>
            {make_li(w2_points)}
          </ul>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

    # ── Parse Primary Recommendation ─────────────────────
    try:
        r_data    = _json.loads(insights_rec) if insights_rec else {}
        rec_title = r_data.get("title",       "Primary Recommendation")
        rec_desc  = r_data.get("description", "")
    except Exception:
        rec_title, rec_desc = "Primary Recommendation", ""

    if rec_desc:
        st.markdown(f"""
        <div class='rec-primary'>
          <div class='star-bg'>★</div>
          <div>
            <div class='rec-primary-title'>{rec_title}</div>
            <p style='margin:0;color:#555;font-size:13px;line-height:1.75;'>
              {rec_desc}
            </p>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

    # ── Parse & Render Recommendation Details ────────────
    try:
        rd_data  = _json.loads(insights_recdet) if insights_recdet else {}
        rd_items = rd_data.get("items", [])
    except Exception:
        rd_items = []

    if rd_items:
        # Build each card as a separate st.markdown call — avoids the black box bug
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
                        border-left:4px solid #E8673A;margin-bottom:4px;'>
              <div style='font-size:13px;font-weight:700;color:#C4512A;
                          margin-bottom:8px;'>
                {i+1} · {item.get("title","")}
              </div>
              <ul style='margin:0;padding-left:18px;color:#555;
                         font-size:12.5px;line-height:1.72;'>
                {bullets}
              </ul>
            </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
st.markdown("<div style='font-size:15px;font-weight:600;color:#333;margin-bottom:4px;'>Summary</div>",
            unsafe_allow_html=True)
st.markdown("<hr class='div'>", unsafe_allow_html=True)
st.markdown(
    f"<div class='summary-box'>{insights_summary}</div>" if insights_summary
    else "<div class='summary-box' style='color:#bbb;font-style:italic;'>"
         "Click <b>Generate AI Insights</b> to generate an executive summary.</div>",
    unsafe_allow_html=True)

# ── Download ─────────────────────────────────────────────
if insights_summary:
    st.divider()
    
    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    import matplotlib.pyplot as plt
    
    def fig_to_bytes(fig):
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        return buffer
    
    def generate_full_pdf_report(df, total_aud, regional_pct, top_state, 
                                 insights_main, insights_states, insights_region, 
                                 insights_summary, insights_weak, insights_rec, insights_recdet):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                               topMargin=0.4*inch, bottomMargin=0.4*inch,
                               leftMargin=0.6*inch, rightMargin=0.6*inch)
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22,
                                    textColor=colors.HexColor('#222222'), spaceAfter=2, spaceBefore=0, fontName='Helvetica-Bold')
        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Heading2'], fontSize=14,
                                       textColor=colors.HexColor('#E8673A'), spaceAfter=8, spaceBefore=0, fontName='Helvetica-Bold')
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading3'], fontSize=12,
                                      textColor=colors.HexColor('#333333'), spaceAfter=6, spaceBefore=8, fontName='Helvetica-Bold')
        body_style = ParagraphStyle('CustomBody', parent=styles['BodyText'], fontSize=9,
                                   textColor=colors.HexColor('#555555'), spaceAfter=4, leading=11, alignment=TA_JUSTIFY)
        bullet_style = ParagraphStyle('BulletStyle', parent=styles['BodyText'], fontSize=9,
                                     textColor=colors.HexColor('#555555'), spaceAfter=3, leftIndent=18, leading=11, bulletIndent=8)
        
        # PÁGINA 1
        story.append(Paragraph("MONKEY BAA THEATRE", title_style))
        story.append(Paragraph("Expanding Youth Theatre Access: <font color='#E8673A'>Social Outcomes Impact</font>", subtitle_style))
        story.append(Spacer(1, 0.08*inch))
        
        # KPI Cards con Paragraphs en lugar de texto plano
        kpi_col1 = Paragraph(f"<b>Young People Reached</b><br/>{total_aud:,}", 
                            ParagraphStyle('KPI', parent=styles['Normal'], fontSize=11, 
                                         textColor=colors.white, alignment=TA_CENTER, fontName='Helvetica-Bold'))
        kpi_col2 = Paragraph(f"<b>% Regional Audience</b><br/>{regional_pct:.0f}%", 
                            ParagraphStyle('KPI', parent=styles['Normal'], fontSize=11, 
                                         textColor=colors.white, alignment=TA_CENTER, fontName='Helvetica-Bold'))
        kpi_col3 = Paragraph(f"<b>Top Performing State</b><br/>{top_state}", 
                            ParagraphStyle('KPI', parent=styles['Normal'], fontSize=11, 
                                         textColor=colors.white, alignment=TA_CENTER, fontName='Helvetica-Bold'))
        
        kpi_data = [[kpi_col1, kpi_col2, kpi_col3]]
        kpi_table = Table(kpi_data, colWidths=[2*inch, 2*inch, 2*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E8673A')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 16),
            ('TOPPADDING', (0, 0), (-1, -1), 16),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 0.12*inch))
        
        # Gráfico 1
        try:
            yearly = df.groupby("Year")["Audience_n"].sum().reset_index()
            yearly["Year"] = yearly["Year"].astype(int)
            fig1, ax1 = plt.subplots(figsize=(6.5, 2.5))
            ax1.plot(yearly["Year"], yearly["Audience_n"], marker='o', color='#E8673A', linewidth=2.5, markersize=6)
            ax1.fill_between(yearly["Year"], yearly["Audience_n"], alpha=0.15, color='#E8673A')
            ax1.set_title("Total Audience Reached", fontsize=11, fontweight='bold', color='#333')
            ax1.set_xlabel("Year", fontsize=9)
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}k'))
            ax1.grid(True, alpha=0.2)
            ax1.set_facecolor('#F5F0EA')
            fig1.patch.set_facecolor('white')
            plt.tight_layout()
            img1_buffer = fig_to_bytes(fig1)
            img1 = Image(img1_buffer, width=6.5*inch, height=2.5*inch)
            story.append(img1)
            plt.close(fig1)
        except:
            story.append(Paragraph("<i>Chart generation failed</i>", body_style))
        
        story.append(Spacer(1, 0.08*inch))
        story.append(Paragraph("Key Trends:", heading_style))
        for line in insights_main.split('\n'):
            if line.strip().startswith('•'):
                story.append(Paragraph(line.strip(), bullet_style))
        
        story.append(PageBreak())
        
        # PÁGINA 2
        story.append(Paragraph("Audience by State", heading_style))
        sdf = df.groupby("State")["Audience_n"].sum().sort_values(ascending=False).reset_index()
        sdf.columns = ["State","Audience"]
        sdf["Audience"] = sdf["Audience"].round(0).astype(int)
        grand_total = sdf["Audience"].sum()
        sdf["% of total"] = sdf["Audience"].apply(lambda v: f"{v/grand_total*100:.1f}%")
        
        table_data = [["State", "Audience", "% of total"]]
        for _, row in sdf.iterrows():
            table_data.append([row['State'], f"{row['Audience']:,}", row['% of total']])
        
        state_table = Table(table_data, colWidths=[2*inch, 2*inch, 2*inch])
        state_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8673A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#fdf6f2'), colors.white]),
        ]))
        story.append(state_table)
        story.append(Spacer(1, 0.08*inch))
        story.append(Paragraph("State Insights:", heading_style))
        for line in insights_states.split('\n'):
            if line.strip().startswith('•'):
                story.append(Paragraph(line.strip(), bullet_style))
        
        story.append(Spacer(1, 0.12*inch))
        
        # Gráfico 2: Pie
        try:
            reg = df.groupby("Regional II")["Audience_n"].sum()
            for cat in ["Metro","Regional","Remote"]:
                if cat not in reg.index: reg[cat] = 0
            reg = reg[["Metro","Regional","Remote"]]
            fig2, ax2 = plt.subplots(figsize=(5, 2.2))
            colors_pie = ['#E8673A', '#4CAF7D', '#C0392B']
            ax2.pie(reg.values, labels=reg.index, autopct='%1.0f%%', colors=colors_pie, startangle=90)
            ax2.set_title("Audience by Region Type", fontsize=11, fontweight='bold', color='#333')
            fig2.patch.set_facecolor('white')
            plt.tight_layout()
            img2_buffer = fig_to_bytes(fig2)
            img2 = Image(img2_buffer, width=5*inch, height=2.2*inch)
            story.append(img2)
            plt.close(fig2)
        except:
            story.append(Paragraph("<i>Chart generation failed</i>", body_style))
        
        story.append(Spacer(1, 0.06*inch))
        story.append(Paragraph("Geographic Distribution:", heading_style))
        for line in insights_region.split('\n'):
            if line.strip().startswith('•'):
                story.append(Paragraph(line.strip(), bullet_style))
        
        story.append(Spacer(1, 0.12*inch))
        
        # PÁGINA 3: Weaknesses y Recommendations
        story.append(Paragraph("Key Weaknesses", heading_style))
        story.append(Spacer(1, 0.05*inch))
        
        try:
            import json as _json
            w_data = _json.loads(insights_weak) if insights_weak else {}
            w1_title = w_data.get("weakness_1", {}).get("title", "Weakness 1")
            w1_points = w_data.get("weakness_1", {}).get("points", [])
            w2_title = w_data.get("weakness_2", {}).get("title", "Weakness 2")
            w2_points = w_data.get("weakness_2", {}).get("points", [])
            
            story.append(Paragraph(f"<b>⚠️ {w1_title}</b>", body_style))
            for point in w1_points:
                story.append(Paragraph(point, bullet_style))
            story.append(Spacer(1, 0.05*inch))
            story.append(Paragraph(f"<b>⚠️ {w2_title}</b>", body_style))
            for point in w2_points:
                story.append(Paragraph(point, bullet_style))
        except:
            pass
        
        story.append(Spacer(1, 0.12*inch))
        story.append(Paragraph("Recommendations", heading_style))
        story.append(Spacer(1, 0.05*inch))
        
        try:
            import json as _json
            r_data = _json.loads(insights_rec) if insights_rec else {}
            rec_title = r_data.get("title", "Primary Recommendation")
            rec_desc = r_data.get("description", "")
            
            story.append(Paragraph(f"<b>★ {rec_title}</b>", body_style))
            story.append(Paragraph(rec_desc, bullet_style))
            
            rd_data = _json.loads(insights_recdet) if insights_recdet else {}
            rd_items = rd_data.get("items", [])
            
            if rd_items:
                story.append(Spacer(1, 0.05*inch))
                story.append(Paragraph("<b>Recommendation Details:</b>", body_style))
                for i, item in enumerate(rd_items, 1):
                    story.append(Paragraph(f"<b>{i}. {item.get('title', '')}</b>", body_style))
                    for point in item.get("points", []):
                        story.append(Paragraph(point, bullet_style))
        except:
            pass
        
        story.append(PageBreak())
        
        # PÁGINA 4: Summary
        story.append(Paragraph("Executive Summary", heading_style))
        story.append(Spacer(1, 0.05*inch))
        story.append(Paragraph(insights_summary, body_style))
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Report generated by Monkey Baa Theatre AI Reporting System", 
                              ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, 
                                           textColor=colors.HexColor('#999'), alignment=TA_CENTER)))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    md = f"""# Monkey Baa — Access & Audience Reach
**Total:** {total_audience:,} | **Regional:** {regional_pct:.0f}% | **Top State:** {top_state}

## Trends
{insights_main}

## Summary
{insights_summary}
"""
    
    pdf_bytes = generate_full_pdf_report(df, total_audience, regional_pct, top_state,
                                        insights_main, insights_states, insights_region,
                                        insights_summary, insights_weak, insights_rec, insights_recdet)
    st.download_button(
        "📄 Download Report (.pdf)",
        data=pdf_bytes,
        file_name="access_audience_reach.pdf",
        mime="application/pdf"
    )