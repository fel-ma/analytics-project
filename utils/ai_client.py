"""
utils/ai_client.py
==================
OpenAI API call, shared render helpers, and markdown report builder.
Used by ALL report pages — do not edit without telling your partner.
"""

import json
from datetime import datetime

import streamlit as st
from openai import OpenAI


# ─────────────────────────────────────────────────────────
# OpenAI call
# ─────────────────────────────────────────────────────────
def call_openai(client: OpenAI, system_prompt: str, context: str, model: str) -> dict:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": f"Dataset summary:\n\n{context}"},
        ],
        temperature=0.2,
        max_tokens=2000,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


# ─────────────────────────────────────────────────────────
# Shared UI render helpers (used in every report page)
# ─────────────────────────────────────────────────────────
def render_list(insights: dict, key: str, icon: str, label: str):
    """Render a list or string insight section."""
    val = insights.get(key)
    if not val:
        return
    st.markdown(f"**{icon} {label}**")
    if isinstance(val, list):
        for item in val:
            st.markdown(f"- {item}")
    else:
        st.write(str(val))


def render_key_metrics(insights: dict):
    """Render key_metrics as Streamlit metric cards."""
    metrics = insights.get("key_metrics")
    if not metrics or not isinstance(metrics, list):
        return
    cols = st.columns(min(5, len(metrics)))
    for i, m in enumerate(metrics[:5]):
        cols[i % len(cols)].metric(m.get("label", ""), str(m.get("value", "")))


def render_data_quality(insights: dict):
    """Render data quality score with colour coding."""
    score = insights.get("data_quality_score")
    if score is None:
        return
    colour = "green" if score >= 75 else ("orange" if score >= 50 else "red")
    st.markdown(f"**Data quality score:** :{colour}[{score} / 100]")


# ─────────────────────────────────────────────────────────
# Markdown report builder
# ─────────────────────────────────────────────────────────
SECTION_MAP = [
    ("executive_summary",          "## Executive Summary",               "str"),
    ("key_metrics",                "## Key Metrics",                     "metrics"),
    ("goal_achievement_rate",      "## Overall Goal Achievement",        "str"),
    ("trends",                     "## Trends",                          "list"),
    ("growth_rates",               "## Growth Rates",                    "str"),
    ("best_year",                  "## Best Year",                       "str"),
    ("2025_outlook",               "## 2025 Outlook",                    "str"),
    ("top_performing_venues",      "## Top Performing Venues",           "list"),
    ("overperforming_locations",   "## Overperforming Locations",        "list"),
    ("underperforming_locations",  "## Underperforming Locations",       "list"),
    ("geographic_insights",        "## Geographic Insights",             "list"),
    ("state_breakdown",            "## State Breakdown",                 "list"),
    ("metro_vs_regional",          "## Metro vs Regional",               "str"),
    ("underserved_states",         "## Underserved States",              "list"),
    ("emotional_impact",           "## Emotional Impact",                "list"),
    ("social_outcomes",            "## Social Outcomes",                 "list"),
    ("arts_cultural_value",        "## Arts & Cultural Value",           "list"),
    ("community_engagement",       "## Community Engagement",            "list"),
    ("sponsor_roi",                "## Sponsor ROI",                     "list"),
    ("funding_highlights",         "## Funding Highlights",              "list"),
    ("anomalies",                  "## Anomalies",                       "list"),
    ("recommendations",            "## Recommendations",                 "list"),
    ("data_quality_score",         "## Data Quality Score",              "score"),
]


def build_report(insights: dict, df, report_name: str) -> str:
    import pandas as pd
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    completed = df[df["Status"] == "Completed"]
    lines = [
        f"# Monkey Baa Theatre — {report_name}",
        f"**Generated:** {ts}",
        f"**Records:** {len(df):,}  |  **Completed:** {len(completed):,}  |  **Years:** 2021–2025",
        "---",
    ]
    for key, header, kind in SECTION_MAP:
        val = insights.get(key)
        if val is None:
            continue
        lines.append(header)
        if kind == "str":
            lines.append(str(val))
        elif kind == "score":
            lines.append(f"**{val} / 100**")
        elif kind == "list":
            for item in (val if isinstance(val, list) else [str(val)]):
                lines.append(f"- {item}")
        elif kind == "metrics":
            for m in (val if isinstance(val, list) else []):
                lines.append(f"- **{m.get('label','')}:** {m.get('value','')}")
        lines.append("")
    return "\n".join(lines)
