"""
pages/3_Emotional_and_Social_Impact.py
========================================
Report 3: Emotional & Social Impact
OWNER: [Persona 1 — assign your name here]

Covers:
- Community and social outcomes from touring
- Reach into underserved communities
- Regional vs metro equity
- Social value of arts access for children
"""

import json
import matplotlib.pyplot as plt
import streamlit as st

from utils.ai_client import (
    call_openai, render_list, render_key_metrics,
    render_data_quality, build_report,
)
from utils.charts import (
    chart_metro_vs_regional,
    chart_audience_by_state,
    chart_audience_by_year_line,
)
from utils.data_loader import build_context
from openai import OpenAI

# ─────────────────────────────────────────────────────────
# Prompt
# ─────────────────────────────────────────────────────────
PROMPT = """You are a social impact analyst for an Australian children's theatre company.
Analyse the following touring dataset and return a JSON object focused on emotional and social outcomes:

- "executive_summary": 2-3 sentences on the social and emotional impact of the touring program
- "key_metrics": list of dicts with "label" and "value" (children reached, regional communities served, underserved areas visited, equity indicators)
- "emotional_impact": list of strings describing the emotional and developmental value delivered to child audiences
- "social_outcomes": list of strings on community-level social outcomes (access, inclusion, equity)
- "community_engagement": list of strings on how touring engaged local communities, especially regional ones
- "metro_vs_regional": analysis of equity in access between metro and regional communities
- "underserved_states": states or territories with limited arts access that benefited most
- "trends": list of strings on how social reach has changed year-on-year
- "anomalies": list of strings — any notable gaps or access inequities
- "recommendations": list of suggestions to deepen social and emotional impact
- "data_quality_score": integer 0-100

Return ONLY valid JSON, no markdown, no preamble."""

# ─────────────────────────────────────────────────────────
# Page
# ─────────────────────────────────────────────────────────
st.title("💛 Emotional & Social Impact")
st.caption("What social and emotional value did the touring program create for communities?")

if "df" not in st.session_state:
    st.warning("⬅️ Please upload the Excel file in the sidebar on the Home page first.")
    st.stop()

df        = st.session_state["df"]
api_key   = st.session_state.get("api_key", "")
model     = st.session_state.get("model", "gpt-4o")
completed = df[df["Status"] == "Completed"]

# Quick stats
regional_count = (completed["Regional.1"] == "Regional").sum()
metro_count    = (completed["Regional.1"] == "Metro").sum()
states_count   = completed["State"].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total audience",      f"{int(completed['Audience Actual (n)'].sum()):,}")
c2.metric("Regional venues",     regional_count)
c3.metric("Metro venues",        metro_count)
c4.metric("States reached",      states_count)

st.divider()

show_raw = st.checkbox("Show raw JSON response")
run = st.button("🚀 Run AI Analysis", type="primary")

if run:
    if not api_key:
        st.error("Enter your OpenAI API key in the sidebar on the Home page.")
        st.stop()

    with st.spinner("Analysing with GPT…"):
        try:
            client   = OpenAI(api_key=api_key)
            context  = build_context(df)
            insights = call_openai(client, PROMPT, context, model)
        except Exception as e:
            st.error(f"API error: {e}")
            st.stop()

    st.success("Analysis complete!")

    st.header("📑 AI Insights")
    if "executive_summary" in insights:
        st.info(insights["executive_summary"])
    render_key_metrics(insights)

    st.divider()

    # Emotional & social outcomes
    st.subheader("💛 Emotional & Social Outcomes")
    col_a, col_b = st.columns(2)
    with col_a:
        render_list(insights, "emotional_impact",    "💛", "Emotional impact")
        render_list(insights, "social_outcomes",     "🤝", "Social outcomes")
    with col_b:
        render_list(insights, "community_engagement","🏘️", "Community engagement")
        render_list(insights, "trends",              "🔄", "Trends over time")

    st.divider()

    # Geographic equity
    st.subheader("🗺️ Geographic Equity — Who Was Reached?")
    col_pie, col_bar = st.columns(2)
    with col_pie:
        fig = chart_metro_vs_regional(df)
        if fig:
            st.pyplot(fig); plt.close(fig)
    with col_bar:
        fig = chart_audience_by_state(df)
        st.pyplot(fig); plt.close(fig)

    eq1, eq2 = st.columns(2)
    with eq1:
        render_list(insights, "metro_vs_regional",  "🏙️", "Metro vs Regional")
    with eq2:
        render_list(insights, "underserved_states", "🔍", "Underserved states")

    st.divider()

    # Audience growth
    st.subheader("📈 Audience Reach Over Time")
    fig = chart_audience_by_year_line(df)
    st.pyplot(fig); plt.close(fig)

    st.divider()

    p1, p2 = st.columns(2)
    with p1:
        render_list(insights, "anomalies", "⚡", "Anomalies & gaps")
    with p2:
        render_list(insights, "recommendations", "💡", "Recommendations")

    render_data_quality(insights)

    if show_raw:
        with st.expander("Raw JSON"):
            st.json(insights)

    st.divider()
    st.subheader("⬇️ Download Report")
    md = build_report(insights, df, "Emotional & Social Impact")
    d1, d2 = st.columns(2)
    d1.download_button("📄 Markdown (.md)", md,
                       file_name="report_emotional_social_impact.md", mime="text/markdown")
    d2.download_button("📋 JSON (.json)", json.dumps(insights, indent=2),
                       file_name="report_emotional_social_impact.json", mime="application/json")
