"""
pages/6_Impact_Report_Sponsors.py
====================================
Report 6: Impact Report — Sponsors & Funders
OWNER: [Persona 2 — assign your name here]

Covers:
- ROI narrative for funders and sponsors
- Children and communities reached with their support
- Geographic spread of impact
- Evidence for continued investment
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
PROMPT = """You are a grants and philanthropy specialist preparing a funder impact report for an Australian children's theatre company.
Your audience is sponsors, government funders, and philanthropic partners who need to see the return on their investment.
Analyse the following touring dataset and return a JSON object with:

- "executive_summary": 3-4 sentence compelling narrative of impact delivered with funder support
- "key_metrics": list of dicts with "label" and "value" — frame these as impact figures (children reached, communities served, states covered, performances delivered)
- "sponsor_roi": list of strings describing the tangible return on investment for funders (reach, access, equity, cultural value)
- "funding_highlights": list of strings — the most impressive or headline achievements worth highlighting to funders
- "geographic_insights": list of strings on the breadth of geographic impact achieved with funder support
- "metro_vs_regional": analysis framed for funders — evidence of equity and access in underserved areas
- "underserved_states": states or territories where funding unlocked access for children who would otherwise miss out
- "trends": list of strings on how impact has grown year-on-year thanks to ongoing support
- "top_performing_venues": list of strings — key venues that demonstrate reach and credibility
- "anomalies": list of strings — any areas where targets were missed (be honest — funders value transparency)
- "recommendations": list of suggestions for how continued or increased funding would extend impact
- "data_quality_score": integer 0-100

Return ONLY valid JSON, no markdown, no preamble."""

# ─────────────────────────────────────────────────────────
# Page
# ─────────────────────────────────────────────────────────
st.title("🤝 Impact Report — Sponsors & Funders")
st.caption("Demonstrating the value of investment in Monkey Baa's touring program.")

if "df" not in st.session_state:
    st.warning("⬅️ Please upload the Excel file in the sidebar on the Home page first.")
    st.stop()

df        = st.session_state["df"]
api_key   = st.session_state.get("api_key", "")
model     = st.session_state.get("model", "gpt-4o")
completed = df[df["Status"] == "Completed"]

# Impact headline metrics (framed for funders)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Children reached",    f"{int(completed['Audience Actual (n)'].sum()):,}")
c2.metric("Communities visited", len(completed))
c3.metric("States covered",      completed["State"].nunique())
c4.metric("Performances given",  f"{int(completed['Number of events'].sum()):,}")
c5.metric("Years of touring",    completed["Year"].nunique())

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

    st.header("📑 Impact Summary for Funders")
    if "executive_summary" in insights:
        st.info(insights["executive_summary"])
    render_key_metrics(insights)

    st.divider()

    # ROI & highlights
    st.subheader("💰 Return on Investment")
    col_a, col_b = st.columns(2)
    with col_a:
        render_list(insights, "sponsor_roi",        "💰", "Funder ROI")
        render_list(insights, "funding_highlights", "⭐", "Impact highlights")
    with col_b:
        render_list(insights, "trends",             "🔄", "Growth with funder support")
        render_list(insights, "top_performing_venues","🎭", "Key venues")

    st.divider()

    # Audience growth for funders
    st.subheader("📈 Audience Growth Over the Investment Period")
    fig = chart_audience_by_year_line(df)
    st.pyplot(fig); plt.close(fig)

    st.divider()

    # Geographic reach
    st.subheader("🗺️ Geographic Reach of Your Investment")
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
        render_list(insights, "metro_vs_regional",   "🏙️", "Metro vs Regional equity")
        render_list(insights, "geographic_insights", "🗺️", "Geographic impact")
    with geo2:
        render_list(insights, "underserved_states",  "🔍", "Communities unlocked by funding")

    st.divider()

    # Goal vs Actual
    st.subheader("🎯 Targets vs Actual Delivery")
    fig = chart_goal_vs_actual(df)
    st.pyplot(fig); plt.close(fig)

    st.divider()

    p1, p2 = st.columns(2)
    with p1:
        render_list(insights, "anomalies",       "⚡", "Areas for improvement (transparent reporting)")
    with p2:
        render_list(insights, "recommendations", "💡", "How further investment extends impact")

    render_data_quality(insights)

    if show_raw:
        with st.expander("Raw JSON"):
            st.json(insights)

    st.divider()
    st.subheader("⬇️ Download Report")
    md = build_report(insights, df, "Impact Report — Sponsors & Funders")
    d1, d2 = st.columns(2)
    d1.download_button("📄 Markdown (.md)", md,
                       file_name="report_sponsors_impact.md", mime="text/markdown")
    d2.download_button("📋 JSON (.json)", json.dumps(insights, indent=2),
                       file_name="report_sponsors_impact.json", mime="application/json")
