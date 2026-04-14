"""
pages/5_Executive_Overview.py
================================
Report 5: Executive Overview
OWNER: [Persona 1 — assign your name here]

Covers:
- Full program summary for leadership / board
- All key metrics in one place
- Strategic outlook and priorities
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
    chart_audience_by_year_line,
)
from utils.data_loader import build_context
from openai import OpenAI

# ─────────────────────────────────────────────────────────
# Prompt
# ─────────────────────────────────────────────────────────
PROMPT = """You are a senior analyst preparing a board-level executive report for an Australian children's theatre company.
Analyse the following touring dataset and return a comprehensive JSON object with:

- "executive_summary": 3-4 sentence narrative overview of the full touring program 2021-2025
- "key_metrics": list of dicts with "label" and "value" covering all major KPIs (total audience, events, venues, states, goal achievement, growth rate)
- "trends": list of strings on year-on-year program evolution
- "growth_rates": year-on-year percentage changes for headline metrics
- "best_year": which year performed best overall and why
- "2025_outlook": strategic assessment of planned 2025 activity
- "geographic_insights": list of strings on national reach and coverage
- "top_performing_venues": list of strings — most impactful venues
- "metro_vs_regional": summary of access equity
- "anomalies": list of strings — notable risks or outliers for board awareness
- "recommendations": list of strategic priorities for the next program cycle
- "data_quality_score": integer 0-100

Return ONLY valid JSON, no markdown, no preamble."""

# ─────────────────────────────────────────────────────────
# Page
# ─────────────────────────────────────────────────────────
st.title("📋 Executive Overview")
st.caption("Full program summary for leadership and board — 2021 to 2025.")

if "df" not in st.session_state:
    st.warning("⬅️ Please upload the Excel file in the sidebar on the Home page first.")
    st.stop()

df        = st.session_state["df"]
api_key   = st.session_state.get("api_key", "")
model     = st.session_state.get("model", "gpt-4o")
completed = df[df["Status"] == "Completed"]
planned   = df[df["Status"] == "Planned"]

# Full metrics dashboard
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total records",    f"{len(df):,}")
c2.metric("Completed",        len(completed))
c3.metric("Planned 2025",     len(planned))
c4.metric("Total audience",   f"{int(completed['Audience Actual (n)'].sum()):,}")
c5.metric("Avg goal %",       f"{completed['Goal Achievement %'].mean():.1f}%")
c6.metric("States reached",   completed["State"].nunique())

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

    st.header("📑 Executive Insights")
    if "executive_summary" in insights:
        st.info(insights["executive_summary"])
    render_key_metrics(insights)

    st.divider()

    # Program performance
    st.subheader("📊 Program Performance 2021–2025")
    col_line, col_bar_text = st.columns([6, 4])
    with col_line:
        fig = chart_audience_by_year_line(df)
        st.pyplot(fig); plt.close(fig)
    with col_bar_text:
        render_list(insights, "trends",       "🔄", "Trends")
        render_list(insights, "growth_rates", "📈", "Growth rates")
        render_list(insights, "best_year",    "🏆", "Best year")
        render_list(insights, "2025_outlook", "🔭", "2025 outlook")

    st.divider()

    # Goal vs Actual + Geographic
    st.subheader("🎯 Goal Achievement & Geographic Reach")
    col_a, col_b = st.columns(2)
    with col_a:
        fig = chart_goal_vs_actual(df)
        st.pyplot(fig); plt.close(fig)
    with col_b:
        fig = chart_audience_by_state(df)
        st.pyplot(fig); plt.close(fig)

    # Pie + geo text
    col_pie, col_geo = st.columns(2)
    with col_pie:
        fig = chart_metro_vs_regional(df)
        if fig:
            st.pyplot(fig); plt.close(fig)
    with col_geo:
        render_list(insights, "geographic_insights",  "🗺️", "Geographic insights")
        render_list(insights, "metro_vs_regional",    "🏙️", "Metro vs Regional")
        render_list(insights, "top_performing_venues","🎭", "Top performing venues")

    st.divider()

    # Strategic section
    st.subheader("💡 Strategic Priorities")
    p1, p2 = st.columns(2)
    with p1:
        render_list(insights, "anomalies", "⚡", "Risks & anomalies")
    with p2:
        render_list(insights, "recommendations", "💡", "Recommendations")

    render_data_quality(insights)

    if show_raw:
        with st.expander("Raw JSON"):
            st.json(insights)

    st.divider()
    st.subheader("⬇️ Download Report")
    md = build_report(insights, df, "Executive Overview")
    d1, d2 = st.columns(2)
    d1.download_button("📄 Markdown (.md)", md,
                       file_name="report_executive_overview.md", mime="text/markdown")
    d2.download_button("📋 JSON (.json)", json.dumps(insights, indent=2),
                       file_name="report_executive_overview.json", mime="application/json")
