"""
pages/4_Arts_and_Cultural_Impact.py
=====================================
Report 4: Arts & Cultural Impact
OWNER: [Persona 2 — assign your name here]

Covers:
- Artistic reach and cultural value
- National tour footprint
- Contribution to Australian children's arts sector
- Cultural access in diverse regions
"""

import json
import matplotlib.pyplot as plt
import streamlit as st

from utils.ai_client import (
    call_openai, render_list, render_key_metrics,
    render_data_quality, build_report,
)
from utils.charts import (
    chart_audience_by_state,
    chart_events_by_state,
    chart_metro_vs_regional,
    chart_audience_by_year_line,
)
from utils.data_loader import build_context
from openai import OpenAI

# ─────────────────────────────────────────────────────────
# Prompt
# ─────────────────────────────────────────────────────────
PROMPT = """You are a cultural policy analyst specialising in Australian performing arts.
Analyse the following touring dataset and return a JSON object focused on arts and cultural impact:

- "executive_summary": 2-3 sentences on the cultural significance and artistic reach of the program
- "key_metrics": list of dicts with "label" and "value" (productions toured, states reached, cultural venues visited, total performances)
- "arts_cultural_value": list of strings on the cultural and artistic value delivered by the touring program
- "geographic_insights": list of strings on the national footprint and cultural access created
- "state_breakdown": list of strings describing each state's arts and cultural engagement
- "metro_vs_regional": analysis of cultural access equity between metro and regional areas
- "underserved_states": territories or states with limited children's arts access
- "trends": list of strings on how the cultural reach has evolved 2021-2025
- "top_performing_venues": list of strings — culturally significant venues visited
- "anomalies": list of strings — any cultural gaps or missed opportunities
- "recommendations": list of suggestions to deepen arts and cultural impact nationally
- "data_quality_score": integer 0-100

Return ONLY valid JSON, no markdown, no preamble."""

# ─────────────────────────────────────────────────────────
# Page
# ─────────────────────────────────────────────────────────
st.title("🎨 Arts & Cultural Impact")
st.caption("What is the cultural contribution of Monkey Baa's national touring program?")

if "df" not in st.session_state:
    st.warning("⬅️ Please upload the Excel file in the sidebar on the Home page first.")
    st.stop()

df        = st.session_state["df"]
api_key   = st.session_state.get("api_key", "")
model     = st.session_state.get("model", "gpt-4o")
completed = df[df["Status"] == "Completed"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("States covered",       completed["State"].nunique())
c2.metric("Total performances",   f"{int(completed['Number of events'].sum()):,}")
c3.metric("Venues visited",       len(completed))
c4.metric("Total audience",       f"{int(completed['Audience Actual (n)'].sum()):,}")

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

    # Cultural value
    st.subheader("🎨 Arts & Cultural Value")
    col_a, col_b = st.columns(2)
    with col_a:
        render_list(insights, "arts_cultural_value",  "🎨", "Cultural value delivered")
        render_list(insights, "top_performing_venues","🎭", "Key cultural venues")
    with col_b:
        render_list(insights, "trends",               "🔄", "Cultural reach trends")
        render_list(insights, "geographic_insights",  "🗺️", "National footprint")

    st.divider()

    # Geographic cultural access
    st.subheader("🗺️ Cultural Access by Region")
    col_pie, col_bar = st.columns(2)
    with col_pie:
        fig = chart_metro_vs_regional(df)
        if fig:
            st.pyplot(fig); plt.close(fig)
    with col_bar:
        fig = chart_audience_by_state(df)
        st.pyplot(fig); plt.close(fig)

    st.divider()

    # Events by state + state breakdown
    st.subheader("📍 State-Level Cultural Engagement")
    col_ev, col_text = st.columns([6, 4])
    with col_ev:
        fig = chart_events_by_state(df)
        st.pyplot(fig); plt.close(fig)
    with col_text:
        render_list(insights, "state_breakdown",    "📍", "State breakdown")
        render_list(insights, "metro_vs_regional",  "🏙️", "Metro vs Regional")
        render_list(insights, "underserved_states", "🔍", "Underserved states")

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
    md = build_report(insights, df, "Arts & Cultural Impact")
    d1, d2 = st.columns(2)
    d1.download_button("📄 Markdown (.md)", md,
                       file_name="report_arts_cultural_impact.md", mime="text/markdown")
    d2.download_button("📋 JSON (.json)", json.dumps(insights, indent=2),
                       file_name="report_arts_cultural_impact.json", mime="application/json")
