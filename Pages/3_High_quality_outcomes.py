"""
pages/1_Access_and_Audience_Reach.py
=====================================
Report 1: Access & Audience Reach
OWNER: [Persona 1 — assign your name here]

Covers:
- Total audience reached vs goals
- Geographic reach (states, metro/regional)
- Venue-level attendance performance
"""

import json
import matplotlib.pyplot as plt
import streamlit as st

from utils.ai_client import (
    call_openai, render_list, render_key_metrics,
    render_data_quality, build_report,
)
from utils.charts import (
    chart_goal_vs_actual,
    chart_audience_by_state,
    chart_metro_vs_regional,
    chart_goal_achievement_dist,
)
from utils.data_loader import build_context
from openai import OpenAI

# ─────────────────────────────────────────────────────────
# Prompt
# ─────────────────────────────────────────────────────────
PROMPT = """You are a senior analyst for an Australian children's theatre company.
Analyse the following touring dataset and return a JSON object with these exact keys:

- "executive_summary": 2-3 sentence overview of audience reach and access
- "key_metrics": list of dicts with "label" and "value" (total audience, total events, venues reached, avg attendance per venue, completion rate)
- "goal_achievement_rate": overall percentage of audience goal achieved
- "trends": list of strings on year-on-year audience trends
- "top_performing_venues": list of strings — best venues by audience
- "overperforming_locations": list of strings — venues/states where actual exceeded goal
- "underperforming_locations": list of strings — venues/states that fell short
- "geographic_insights": list of strings about state/region reach
- "metro_vs_regional": analysis of Metro vs Regional split
- "underserved_states": states/territories with low or no coverage
- "anomalies": list of strings — outliers or unusual data points
- "recommendations": list of actionable suggestions to improve access and reach
- "data_quality_score": integer 0-100

Return ONLY valid JSON, no markdown, no preamble."""

# ─────────────────────────────────────────────────────────
# Page
# ─────────────────────────────────────────────────────────
st.title("🌏 Access & Audience Reach")
st.caption("How far did Monkey Baa reach — and did they hit their targets?")

# Guard: need data loaded
if "df" not in st.session_state:
    st.warning("⬅️ Please upload the Excel file in the sidebar on the Home page first.")
    st.stop()

df        = st.session_state["df"]
api_key   = st.session_state.get("api_key", "")
model     = st.session_state.get("model", "gpt-4o")
completed = df[df["Status"] == "Completed"]

# Quick stats
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total records",   f"{len(df):,}")
c2.metric("Completed tours", len(completed))
c3.metric("Planned tours",   (df["Status"] == "Planned").sum())
c4.metric("Total audience",  f"{int(completed['Audience Actual (n)'].sum()):,}")
c5.metric("Avg goal %",      f"{completed['Goal Achievement %'].mean():.1f}%")

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

    # Executive summary
    st.header("📑 AI Insights")
    if "executive_summary" in insights:
        st.info(insights["executive_summary"])
    render_key_metrics(insights)

    st.divider()

    # Goal vs Actual + trends
    st.subheader("📊 Audience Performance Over Time")
    col_chart, col_text = st.columns([6, 4])
    with col_chart:
        fig = chart_goal_vs_actual(df)
        st.pyplot(fig); plt.close(fig)
    with col_text:
        render_list(insights, "goal_achievement_rate",    "🎯", "Overall goal achievement rate")
        render_list(insights, "trends",                   "🔄", "Trends")
        render_list(insights, "top_performing_venues",    "🎭", "Top performing venues")

    st.divider()

    # Geographic
    st.subheader("🗺️ Geographic Reach")
    col_pie, col_bar = st.columns(2)
    with col_pie:
        fig = chart_metro_vs_regional(df)
        if fig:
            st.pyplot(fig); plt.close(fig)
    with col_bar:
        fig = chart_audience_by_state(df)
        st.pyplot(fig); plt.close(fig)

    geo1, geo2 = st.columns(2)
    with geo1:
        render_list(insights, "metro_vs_regional",   "🏙️", "Metro vs Regional")
        render_list(insights, "geographic_insights", "🗺️", "Geographic insights")
    with geo2:
        render_list(insights, "underserved_states",  "🔍", "Underserved states")

    st.divider()

    # Performance detail
    st.subheader("⚡ Performance Detail")
    fig = chart_goal_achievement_dist(df)
    if fig:
        st.pyplot(fig); plt.close(fig)

    p1, p2 = st.columns(2)
    with p1:
        render_list(insights, "overperforming_locations",  "✅", "Overperforming locations")
        render_list(insights, "underperforming_locations", "⚠️", "Underperforming locations")
        render_list(insights, "anomalies",                 "⚡", "Anomalies")
    with p2:
        render_list(insights, "recommendations", "💡", "Recommendations")

    render_data_quality(insights)

    if show_raw:
        with st.expander("Raw JSON"):
            st.json(insights)

    # Downloads
    st.divider()
    st.subheader("⬇️ Download Report")
    md = build_report(insights, df, "Access & Audience Reach")
    d1, d2 = st.columns(2)
    d1.download_button("📄 Markdown (.md)", md,
                       file_name="report_access_audience.md", mime="text/markdown")
    d2.download_button("📋 JSON (.json)", json.dumps(insights, indent=2),
                       file_name="report_access_audience.json", mime="application/json")
