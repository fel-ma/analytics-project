"""
AI-Powered Data Analyst — Monkey Baa Theatre Touring Data
==========================================================
Adapted for the Monkey Baa 2025 Dashboard dataset.

Columns:
    Description.1     - Tour category label (Tours / National Tours / etc.)
    Name              - Venue city / location name
    Status            - Completed | Planned | Cancelled
    Year              - 2021 – 2025
    Type              - On-Tour (only value)
    Number of events  - Number of performances at this location
    Audience Goal     - Target audience (string with commas, needs cleaning)
    Audience Actual   - Actual audience achieved (same format)
    Regional.1        - Metro | Regional  (56 nulls — needs imputation)
    State             - ACT / NSW / NT / QLD / SA / TAS / VIC / WA
    Venue Temp        - Venue name (1 null)
    Date from         - Performance start date (45 nulls)

Requirements:
    pip install streamlit openai openpyxl pandas matplotlib seaborn

Run:
    streamlit run ai_data_analyst.py
"""

import io
import json
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import streamlit as st
from openai import OpenAI

# ─────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Monkey Baa — AI Tour Analyst",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stDownloadButton > button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# Prompt templates — tuned for touring / arts industry data
# ─────────────────────────────────────────────────────────
PROMPT_TEMPLATES = {
    "Tour Performance Overview": """You are a senior analyst for an Australian children's theatre company.
Analyse the following touring dataset summary and return a JSON object with these exact keys:

- "executive_summary": 2-3 sentence overview of the touring program
- "key_metrics": list of dicts, each with "label" and "value" (e.g. total audience, total events, avg attendance per venue, completion rate)
- "trends": list of strings describing year-on-year trends in audience numbers and tour reach
- "top_performing_venues": list of strings naming best-performing venues by audience
- "geographic_insights": list of strings about state/region distribution and reach
- "anomalies": list of strings describing outliers or unusual data points
- "recommendations": list of actionable suggestions for future touring strategy
- "data_quality_score": integer 0-100

Return ONLY valid JSON, no markdown, no preamble.""",

    "Audience Goal vs Actual": """You are a data analyst specialising in live events and performing arts.
Review this touring dataset and return a JSON object with:

- "executive_summary": brief overview of how well audience targets were met
- "goal_achievement_rate": overall percentage of audience goal achieved across all tours
- "overperforming_locations": list of strings - venues or states where actual exceeded goal
- "underperforming_locations": list of strings - venues or states that fell short
- "trends": patterns in how goal achievement has changed year-on-year
- "anomalies": any extreme over/under-performance worth flagging
- "recommendations": strategies to improve audience goal accuracy and achievement
- "data_quality_score": integer 0-100

Return ONLY valid JSON, no markdown, no preamble.""",

    "Geographic & State Analysis": """You are a touring strategy analyst for Australian performing arts.
Analyse the geographic distribution in this dataset and return a JSON object with:

- "executive_summary": overview of the geographic footprint of the touring program
- "key_metrics": list of dicts with "label" and "value" for state-level stats
- "state_breakdown": list of strings describing each state's tour activity and audience
- "metro_vs_regional": analysis of Metro vs Regional split in events and audience
- "underserved_states": states or territories with low or no coverage
- "trends": how geographic reach has shifted across years
- "recommendations": suggestions for geographic expansion or rebalancing
- "data_quality_score": integer 0-100

Return ONLY valid JSON, no markdown, no preamble.""",

    "Year-on-Year Growth Analysis": """You are a performing arts business analyst.
Focus on year-on-year changes in this touring dataset and return a JSON object with:

- "executive_summary": brief narrative of how the touring program has evolved 2021-2025
- "key_metrics": list of dicts with yearly totals for events, venues, and audience
- "growth_rates": year-on-year percentage changes for key indicators
- "best_year": which year performed best and why
- "trends": narrative trends across the full period
- "2025_outlook": assessment of planned 2025 activity vs historical performance
- "anomalies": any years that deviate significantly from the trend
- "recommendations": strategic implications for planning
- "data_quality_score": integer 0-100

Return ONLY valid JSON, no markdown, no preamble.""",

    "Custom Prompt": "",
}

# ─────────────────────────────────────────────────────────
# Data loading & cleaning
# ─────────────────────────────────────────────────────────
@st.cache_data
def load_and_clean(file_bytes: bytes) -> pd.DataFrame:
    df = pd.read_excel(
        io.BytesIO(file_bytes),
        sheet_name="Monkey Baa _Data_2025_Dashboard",
    )

    # Clean audience columns (stored as "1,234.00" strings)
    for col in ["Audience Goal", "Audience Actual"]:
        df[col + " (n)"] = pd.to_numeric(
            df[col].astype(str).str.replace(",", "").str.strip(),
            errors="coerce",
        )

    # Goal achievement %
    df["Goal Achievement %"] = (
        df["Audience Actual (n)"] / df["Audience Goal (n)"] * 100
    ).round(1)

    # Impute known-null Regional.1 values
    metro_hints = {
        "Belrose", "Parramatta", "Casula", "Crawley", "Subiaco",
        "Northbridge", "Sydney", "Melbourne", "Brisbane", "Perth",
    }
    def impute_regional(row):
        if pd.notna(row["Regional.1"]):
            return row["Regional.1"]
        return "Metro" if row["Name"] in metro_hints else "Unknown"

    df["Regional.1"] = df.apply(impute_regional, axis=1)
    return df


# ─────────────────────────────────────────────────────────
# Build data context for the API
# ─────────────────────────────────────────────────────────
def build_context(df: pd.DataFrame) -> str:
    buf = []
    buf.append("DATASET: Monkey Baa Theatre — Australian Touring Data 2021-2025")
    buf.append(f"Total records: {len(df)} | Columns: 12\n")

    buf.append("STATUS BREAKDOWN:")
    buf.append(df["Status"].value_counts().to_string())

    buf.append("\nYEAR BREAKDOWN (tour stops):")
    buf.append(df["Year"].value_counts().sort_index().to_string())

    buf.append("\nSTATE BREAKDOWN:")
    buf.append(df["State"].value_counts().to_string())

    buf.append("\nMETRO vs REGIONAL:")
    buf.append(df["Regional.1"].value_counts().to_string())

    buf.append("\nTOUR CATEGORY LABELS:")
    buf.append(df["Description.1"].value_counts().to_string())

    completed = df[df["Status"] == "Completed"]
    buf.append("\nAUDIENCE STATS (completed tours only):")
    buf.append(
        completed[["Audience Goal (n)", "Audience Actual (n)",
                    "Goal Achievement %", "Number of events"]]
        .describe().round(1).to_string()
    )

    buf.append("\nAUDIENCE BY YEAR (completed):")
    yearly = completed.groupby("Year").agg(
        total_audience=("Audience Actual (n)", "sum"),
        total_events=("Number of events", "sum"),
        venues=("Name", "count"),
        avg_goal_pct=("Goal Achievement %", "mean"),
    ).round(1)
    buf.append(yearly.to_string())

    buf.append("\nAUDIENCE BY STATE (completed):")
    state_agg = completed.groupby("State").agg(
        total_audience=("Audience Actual (n)", "sum"),
        venues=("Name", "count"),
        total_events=("Number of events", "sum"),
    ).sort_values("total_audience", ascending=False)
    buf.append(state_agg.to_string())

    buf.append("\nTOP 10 VENUES BY AUDIENCE (completed):")
    top = completed.nlargest(10, "Audience Actual (n)")[
        ["Name", "State", "Audience Actual (n)", "Number of events", "Year"]
    ]
    buf.append(top.to_string(index=False))

    buf.append("\nDATA QUALITY NOTES:")
    buf.append(f"Missing Date from: {df['Date from'].isna().sum()} rows")
    buf.append(f"Missing Regional.1 (original): 56 rows")
    buf.append(f"Missing Venue Temp: {df['Venue Temp'].isna().sum()} rows")
    buf.append(f"Cancelled tours: {(df['Status']=='Cancelled').sum()}")

    return "\n".join(buf)


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
# Charts
# ─────────────────────────────────────────────────────────
def make_charts(df: pd.DataFrame):
    completed = df[df["Status"] == "Completed"].copy()
    figs = []
    purple = "#7c3aed"
    light_purple = "#a78bfa"

    # 1. Goal vs Actual by year
    yearly = completed.groupby("Year").agg(
        goal=("Audience Goal (n)", "sum"),
        actual=("Audience Actual (n)", "sum"),
    ).reset_index()
    fig, ax = plt.subplots(figsize=(7, 3.5))
    x = list(range(len(yearly)))
    w = 0.35
    ax.bar([i - w/2 for i in x], yearly["goal"],   width=w, label="Goal",   color=light_purple, alpha=0.9)
    ax.bar([i + w/2 for i in x], yearly["actual"], width=w, label="Actual", color=purple,       alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels(yearly["Year"].astype(str))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.set_title("Audience Goal vs Actual by Year (Completed)", fontsize=12)
    ax.legend()
    plt.tight_layout()
    figs.append(("Audience Goal vs Actual by Year", fig))

    # 2. Audience by state
    state_agg = completed.groupby("State")["Audience Actual (n)"].sum().sort_values()
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.barh(state_agg.index, state_agg.values, color=purple, alpha=0.85)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.set_title("Total Audience by State (Completed)", fontsize=12)
    plt.tight_layout()
    figs.append(("Audience by State", fig))

    # 3. Metro vs Regional pie
    reg = completed.groupby("Regional.1")["Audience Actual (n)"].sum()
    reg = reg[reg.index != "Unknown"]
    if not reg.empty:
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie(reg, labels=reg.index, autopct="%1.0f%%",
               colors=[purple, light_purple, "#ede9fe"][:len(reg)],
               startangle=90, wedgeprops={"linewidth": 0.5, "edgecolor": "white"})
        ax.set_title("Metro vs Regional Audience Split", fontsize=12)
        plt.tight_layout()
        figs.append(("Metro vs Regional", fig))

    # 4. Goal achievement % distribution
    pct = completed["Goal Achievement %"].dropna()
    if not pct.empty:
        fig, ax = plt.subplots(figsize=(7, 3.5))
        ax.hist(pct, bins=20, color=purple, alpha=0.85, edgecolor="white")
        ax.axvline(100, color="#dc2626", linestyle="--", linewidth=1.2, label="100% target")
        ax.set_title("Goal Achievement % Distribution (Completed)", fontsize=12)
        ax.set_xlabel("Goal Achievement %")
        ax.legend()
        plt.tight_layout()
        figs.append(("Goal Achievement Distribution", fig))

    return figs


# ─────────────────────────────────────────────────────────
# Markdown report
# ─────────────────────────────────────────────────────────
def build_report(insights: dict, df: pd.DataFrame, template_name: str) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    completed = df[df["Status"] == "Completed"]
    lines = [
        "# Monkey Baa Theatre — AI Tour Analysis Report",
        f"**Analysis:** {template_name}  |  **Generated:** {ts}",
        f"**Records:** {len(df):,}  |  **Completed:** {len(completed):,}  |  **Years:** 2021–2025",
        "---",
    ]
    section_map = [
        ("executive_summary",          "## Executive Summary",                "str"),
        ("key_metrics",                "## Key Metrics",                      "metrics"),
        ("goal_achievement_rate",      "## Overall Goal Achievement",         "str"),
        ("trends",                     "## Trends",                           "list"),
        ("growth_rates",               "## Growth Rates",                     "str"),
        ("best_year",                  "## Best Year",                        "str"),
        ("2025_outlook",               "## 2025 Outlook",                     "str"),
        ("top_performing_venues",      "## Top Performing Venues",            "list"),
        ("overperforming_locations",   "## Overperforming Locations",         "list"),
        ("underperforming_locations",  "## Underperforming Locations",        "list"),
        ("geographic_insights",        "## Geographic Insights",              "list"),
        ("state_breakdown",            "## State Breakdown",                  "list"),
        ("metro_vs_regional",          "## Metro vs Regional",                "str"),
        ("underserved_states",         "## Underserved States",               "list"),
        ("anomalies",                  "## Anomalies",                        "list"),
        ("recommendations",            "## Recommendations",                  "list"),
        ("data_quality_score",         "## Data Quality Score",               "score"),
    ]
    for key, header, kind in section_map:
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


# ─────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Configuration")
    api_key = st.text_input("OpenAI API key", type="password", placeholder="sk-...")
    model   = st.selectbox("Model", ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])

    st.divider()
    st.subheader("Analysis type")
    template_name = st.selectbox("Template", list(PROMPT_TEMPLATES.keys()))

    if template_name == "Custom Prompt":
        system_prompt = st.text_area(
            "Your prompt", height=250,
            placeholder="Describe the analysis. Ask for JSON output.",
        )
    else:
        system_prompt = PROMPT_TEMPLATES[template_name]
        with st.expander("View prompt"):
            st.code(system_prompt, language="text")

    st.divider()
    show_raw = st.checkbox("Show raw JSON response")

# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────
st.title("🎭 Monkey Baa — AI Tour Analyst")
st.caption("Upload the Monkey Baa Dashboard Excel file to get AI-driven touring insights.")

uploaded = st.file_uploader("Upload Excel file (.xlsx)", type=["xlsx"])

if uploaded:
    df        = load_and_clean(uploaded.read())
    completed = df[df["Status"] == "Completed"]
    planned   = df[df["Status"] == "Planned"]

    # Summary metrics row
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total records",   f"{len(df):,}")
    c2.metric("Completed tours", len(completed))
    c3.metric("Planned tours",   len(planned))
    c4.metric("Total audience",  f"{int(completed['Audience Actual (n)'].sum()):,}")
    c5.metric("Avg goal %",      f"{completed['Goal Achievement %'].mean():.1f}%")

    # Data preview
    with st.expander("📋 Data preview", expanded=False):
        display_cols = [
            "Description.1", "Name", "Status", "Year", "State", "Regional.1",
            "Number of events", "Audience Goal (n)", "Audience Actual (n)",
            "Goal Achievement %", "Venue Temp",
        ]
        st.dataframe(df[display_cols].head(40), use_container_width=True)
        st.subheader("Data quality notes")
        st.markdown("""
- **Regional.1** — 56 original nulls, imputed where city name indicates metro area
- **Date from** — 45 nulls, mostly planned tours without confirmed dates
- **Audience Goal / Actual** — stored as comma-formatted strings, converted to numeric
- **Type** — only one value ("On-Tour"), column is redundant for analysis
- **Description.1** — inconsistent labels ("Tour" / "Tours" / "National Tours") that should be normalised
        """)

    # Run button
    st.divider()
    run = st.button("🚀 Run AI Analysis", type="primary")

    if run:
        if not api_key:
            st.error("Enter your OpenAI API key in the sidebar.")
            st.stop()
        if not system_prompt.strip():
            st.error("Select or write a prompt in the sidebar.")
            st.stop()

        with st.spinner("Analysing with GPT…"):
            try:
                client   = OpenAI(api_key=api_key)
                context  = build_context(df)
                insights = call_openai(client, system_prompt, context, model)
            except Exception as e:
                st.error(f"API error: {e}")
                st.stop()

        st.success("Analysis complete!")

        # ── Rebuild charts for use inside the integrated layout ──
        completed_df = df[df["Status"] == "Completed"].copy()
        purple       = "#7c3aed"
        light_purple = "#a78bfa"

        def chart_goal_vs_actual():
            yearly = completed_df.groupby("Year").agg(
                goal=("Audience Goal (n)", "sum"),
                actual=("Audience Actual (n)", "sum"),
            ).reset_index()
            fig, ax = plt.subplots(figsize=(6, 3.2))
            x = list(range(len(yearly)))
            w = 0.35
            ax.bar([i - w/2 for i in x], yearly["goal"],   width=w, label="Goal",   color=light_purple, alpha=0.9)
            ax.bar([i + w/2 for i in x], yearly["actual"], width=w, label="Actual", color=purple,       alpha=0.9)
            ax.set_xticks(x)
            ax.set_xticklabels(yearly["Year"].astype(str))
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
            ax.set_title("Audience Goal vs Actual by Year", fontsize=11)
            ax.legend(fontsize=9)
            plt.tight_layout()
            return fig

        def chart_audience_by_state():
            state_agg = completed_df.groupby("State")["Audience Actual (n)"].sum().sort_values()
            fig, ax = plt.subplots(figsize=(5, 3.2))
            ax.barh(state_agg.index, state_agg.values, color=purple, alpha=0.85)
            ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
            ax.set_title("Total Audience by State", fontsize=11)
            plt.tight_layout()
            return fig

        def chart_metro_vs_regional():
            reg = completed_df.groupby("Regional.1")["Audience Actual (n)"].sum()
            reg = reg[reg.index != "Unknown"]
            if reg.empty:
                return None
            fig, ax = plt.subplots(figsize=(4, 3.2))
            ax.pie(reg, labels=reg.index, autopct="%1.0f%%",
                   colors=[purple, light_purple][:len(reg)],
                   startangle=90, wedgeprops={"linewidth": 0.5, "edgecolor": "white"})
            ax.set_title("Metro vs Regional Split", fontsize=11)
            plt.tight_layout()
            return fig

        def chart_goal_achievement():
            pct = completed_df["Goal Achievement %"].dropna()
            if pct.empty:
                return None
            fig, ax = plt.subplots(figsize=(7, 3.2))
            ax.hist(pct, bins=20, color=purple, alpha=0.85, edgecolor="white")
            ax.axvline(100, color="#dc2626", linestyle="--", linewidth=1.2, label="100% target")
            ax.set_title("Goal Achievement % Distribution", fontsize=11)
            ax.set_xlabel("Goal Achievement %")
            ax.legend(fontsize=9)
            plt.tight_layout()
            return fig

        def render_list(key, icon, label):
            val = insights.get(key)
            if not val:
                return
            st.markdown(f"**{icon} {label}**")
            if isinstance(val, list):
                for item in val:
                    st.markdown(f"- {item}")
            else:
                st.write(str(val))

        # ════════════════════════════════════════════════
        # BLOCK 1 — Executive Summary
        # ════════════════════════════════════════════════
        st.header("📑 AI Insights")
        if "executive_summary" in insights:
            st.info(insights["executive_summary"])

        # Key metrics row
        if "key_metrics" in insights and isinstance(insights["key_metrics"], list):
            mcols = st.columns(min(5, len(insights["key_metrics"])))
            for i, m in enumerate(insights["key_metrics"][:5]):
                mcols[i % len(mcols)].metric(m.get("label", ""), str(m.get("value", "")))

        st.divider()

        # ════════════════════════════════════════════════
        # BLOCK 2 — Audience Goal vs Actual + trends
        # ════════════════════════════════════════════════
        st.subheader("📊 Audience Performance Over Time")
        col_chart, col_text = st.columns([6, 4])
        with col_chart:
            fig = chart_goal_vs_actual()
            st.pyplot(fig)
            plt.close(fig)
        with col_text:
            render_list("trends",      "🔄", "Trends")
            render_list("growth_rates","📈", "Growth rates")
            render_list("best_year",   "🏆", "Best year")
            render_list("2025_outlook","🔭", "2025 outlook")

        st.divider()

        # ════════════════════════════════════════════════
        # BLOCK 3 — Geographic Coverage
        # ════════════════════════════════════════════════
        st.subheader("🗺️ Geographic Coverage")
        col_pie, col_bar = st.columns(2)
        with col_pie:
            fig = chart_metro_vs_regional()
            if fig:
                st.pyplot(fig)
                plt.close(fig)
        with col_bar:
            fig = chart_audience_by_state()
            st.pyplot(fig)
            plt.close(fig)

        # Geographic text insights below both charts
        geo_col1, geo_col2 = st.columns(2)
        with geo_col1:
            render_list("metro_vs_regional",  "🏙️", "Metro vs Regional")
            render_list("geographic_insights","🗺️", "Geographic insights")
        with geo_col2:
            render_list("state_breakdown",    "📍", "State breakdown")
            render_list("underserved_states", "🔍", "Underserved states")

        st.divider()

        # ════════════════════════════════════════════════
        # BLOCK 4 — Performance & Recommendations
        # ════════════════════════════════════════════════
        st.subheader("⚡ Performance & Recommendations")
        fig = chart_goal_achievement()
        if fig:
            st.pyplot(fig)
            plt.close(fig)

        perf_col1, perf_col2 = st.columns(2)
        with perf_col1:
            render_list("goal_achievement_rate",    "🎯", "Overall goal achievement rate")
            render_list("overperforming_locations", "✅", "Overperforming locations")
            render_list("underperforming_locations","⚠️", "Underperforming locations")
            render_list("top_performing_venues",    "🎭", "Top performing venues")
            render_list("anomalies",                "⚡", "Anomalies")
        with perf_col2:
            render_list("recommendations", "💡", "Recommendations")

        st.divider()

        # ════════════════════════════════════════════════
        # BLOCK 5 — Data Quality
        # ════════════════════════════════════════════════
        if "data_quality_score" in insights:
            score  = insights["data_quality_score"]
            colour = "green" if score >= 75 else ("orange" if score >= 50 else "red")
            st.markdown(f"**Data quality score:** :{colour}[{score} / 100]")

        if show_raw:
            with st.expander("Raw JSON"):
                st.json(insights)

        # Downloads
        st.divider()
        st.subheader("⬇️ Download Report")
        md = build_report(insights, df, template_name)
        d1, d2, d3 = st.columns(3)
        d1.download_button("📄 Markdown (.md)", md,
                           file_name="monkey_baa_analysis.md", mime="text/markdown")
        d2.download_button("📋 JSON (.json)", json.dumps(insights, indent=2),
                           file_name="monkey_baa_analysis.json", mime="application/json")
        csv_out = df[[
            "Year", "State", "Regional.1", "Status", "Name",
            "Number of events", "Audience Goal (n)",
            "Audience Actual (n)", "Goal Achievement %",
        ]].to_csv(index=False)
        d3.download_button("📊 Cleaned CSV", csv_out,
                           file_name="monkey_baa_cleaned.csv", mime="text/csv")

else:
    st.markdown("""
### How to use this app

1. Enter your **OpenAI API key** in the sidebar
2. Choose an **analysis type**
3. **Upload the Monkey Baa Dashboard Excel file**
4. Click **Run AI Analysis**

---

#### Available analysis templates

| Template | What it answers |
|---|---|
| Tour Performance Overview | General season summary, top venues, geographic insights |
| Audience Goal vs Actual | How well audience targets were met by location and year |
| Geographic & State Analysis | Coverage by state, metro vs regional split |
| Year-on-Year Growth | Program evolution 2021–2025 and 2025 outlook |

---

#### What we know about this dataset
- **183 records** — 50 completed · 132 planned · 1 cancelled
- **8 states** covered — NSW leads (64 stops), followed by VIC (52)
- **Total completed audience** ≈ 192,000 attendees
- **Date range**: January 2021 – December 2024 (planned through 2025)
- **Columns requiring attention**: Regional.1 (56 nulls), Date from (45 nulls), Description.1 (inconsistent labels)
    """)