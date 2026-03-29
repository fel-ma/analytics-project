"""
pages/2_Access_and_Audience_Reach.py
======================================
Report: Access & Audience Reach — Expanding Youth Theatre Access
OWNER: Persona 1

Data: Audience_final_data.csv
Columns: Description, Name, school, Year, Type, # of events,
         Audience, Regional II, State, Date from
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import streamlit as st
from openai import OpenAI

# ─────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Access & Audience Reach — Monkey Baa",
    page_icon="🎭",
    layout="wide",
)

# ─────────────────────────────────────────────────────────
# Design tokens
# ─────────────────────────────────────────────────────────
ORANGE      = "#E8673A"
ORANGE_DARK = "#C4512A"
BEIGE       = "#F5F0EA"
WHITE       = "#FFFFFF"
GRAY_TEXT   = "#555555"
CHART_LINE  = "#E8673A"

st.markdown(f"""
<style>
  .stApp {{ background-color: {BEIGE}; }}

  .kpi-card {{
    background-color: {ORANGE};
    border-radius: 14px;
    padding: 22px 18px 18px 18px;
    text-align: center;
    color: white;
    min-height: 110px;
  }}
  .kpi-label {{
    font-size: 13px;
    font-weight: 500;
    opacity: 0.9;
    letter-spacing: 0.3px;
    margin-bottom: 6px;
  }}
  .kpi-value {{
    font-size: 36px;
    font-weight: 700;
    line-height: 1.1;
  }}

  .card {{
    background-color: {WHITE};
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 18px;
  }}

  .insight-box {{
    background-color: #FDF3EE;
    border-radius: 12px;
    padding: 20px 22px;
    color: {GRAY_TEXT};
    font-size: 15px;
    line-height: 1.75;
  }}
  .insight-box ul {{
    margin: 0;
    padding-left: 18px;
  }}
  .insight-box li {{
    margin-bottom: 10px;
  }}

  .section-title {{
    font-size: 17px;
    font-weight: 600;
    color: {ORANGE_DARK};
    margin-bottom: 14px;
    text-decoration: underline;
  }}

  .summary-box {{
    background-color: {WHITE};
    border-radius: 14px;
    padding: 24px 28px;
    color: {GRAY_TEXT};
    font-size: 15px;
    line-height: 1.8;
  }}

  table.styled-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    color: {GRAY_TEXT};
  }}
  table.styled-table th {{
    background-color: #f0e8e0;
    padding: 8px 12px;
    text-align: left;
    font-weight: 600;
    border-bottom: 2px solid #ddd;
  }}
  table.styled-table td {{
    padding: 7px 12px;
    border-bottom: 1px solid #eee;
  }}
  table.styled-table tr:hover {{ background-color: #fdf6f2; }}

  hr.divider {{ border: none; border-top: 1px solid #e0d8d0; margin: 8px 0 18px 0; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# Data loader (CSV)
# ─────────────────────────────────────────────────────────
@st.cache_data
def load_data(file_bytes: bytes) -> pd.DataFrame:
    import io
    df = pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    df["Audience_n"] = pd.to_numeric(
        df["Audience"].astype(str).str.strip().str.replace(",", "", regex=False),
        errors="coerce"
    )
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Regional II"] = df["Regional II"].fillna("Unknown").str.strip()
    return df


def build_context(df: pd.DataFrame) -> str:
    buf = []
    total = df["Audience_n"].sum()
    buf.append("DATASET: Monkey Baa Theatre — Audience Data 2021-2025")
    buf.append(f"Total records: {len(df)} | Total audience: {int(total):,}\n")

    buf.append("AUDIENCE BY YEAR:")
    yearly = df.groupby("Year")["Audience_n"].sum().round(0).astype(int)
    buf.append(yearly.to_string())

    buf.append("\nAUDIENCE BY STATE:")
    state = df.groupby("State")["Audience_n"].sum().sort_values(ascending=False)
    for s, v in state.items():
        buf.append(f"  {s}: {int(v):,} ({v/total*100:.1f}%)")

    buf.append("\nREGION TYPE SPLIT (Metro / Regional / Remote):")
    reg = df.groupby("Regional II")["Audience_n"].sum()
    for r, v in reg.items():
        buf.append(f"  {r}: {int(v):,} ({v/total*100:.1f}%)")

    buf.append("\nTYPE OF EVENT:")
    buf.append(df["Type"].value_counts().to_string())

    buf.append(f"\nTOP STATE: {df.groupby('State')['Audience_n'].sum().idxmax()}")
    regional_pct = df[df["Regional II"] == "Regional"]["Audience_n"].sum() / total * 100
    remote_pct   = df[df["Regional II"] == "Remote"]["Audience_n"].sum() / total * 100
    buf.append(f"REGIONAL AUDIENCE %: {regional_pct:.1f}%")
    buf.append(f"REMOTE AUDIENCE %: {remote_pct:.1f}%")

    return "\n".join(buf)


def call_ai(api_key: str, model: str, prompt: str, context: str) -> str:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user",   "content": f"Dataset summary:\n\n{context}"},
        ],
        temperature=0.3,
        max_tokens=600,
    )
    return response.choices[0].message.content.strip()


def render_bullets(text: str):
    """Render AI bullet points in the insight box."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    bullets = [l for l in lines if l.startswith("•") or l.startswith("-")]
    if bullets:
        items = "".join(f"<li>{b.lstrip('•- ').strip()}</li>" for b in bullets)
    else:
        items = "".join(f"<li>{l}</li>" for l in lines)
    st.markdown(f"<div class='insight-box'><ul>{items}</ul></div>",
                unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🎭 Monkey Baa")
    st.divider()
    api_key = st.text_input("OpenAI API key", type="password", placeholder="sk-...")
    model   = st.selectbox("Model", ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])
    st.divider()
    uploaded = st.file_uploader("Upload Audience CSV", type=["csv"])

df = None
if uploaded:
    df = load_data(uploaded.read())
    st.session_state["df_audience"] = df
elif "df_audience" in st.session_state:
    df = st.session_state["df_audience"]


# ─────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────
col_title, col_logo = st.columns([3, 1])
with col_title:
    st.markdown("""
    <div style='padding-top:10px'>
      <div style='font-size:12px;font-weight:500;color:#999;letter-spacing:1px;
                  text-transform:uppercase;margin-bottom:4px;'>Monkey Baa Theatre</div>
      <div style='font-size:22px;font-weight:700;color:#333;line-height:1.35;'>
        Expanding Youth Theatre Access:<br>
        <span style='color:#E8673A;'>Social Outcomes Impact (Horizon)</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
with col_logo:
    st.markdown("""
    <div style='text-align:right;padding-top:18px;font-size:26px;font-weight:700;
                color:#222;font-style:italic;letter-spacing:-0.5px;'>
      monkey baa
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr class='divider' style='margin-top:18px;'>", unsafe_allow_html=True)

if df is None:
    st.info("⬅️ Upload the **Audience_final_data.csv** file in the sidebar to begin.")
    st.stop()

# ─────────────────────────────────────────────────────────
# Compute KPIs
# ─────────────────────────────────────────────────────────
total_audience = int(df["Audience_n"].sum())
top_state      = df.groupby("State")["Audience_n"].sum().idxmax()
regional_pct   = df[df["Regional II"] == "Regional"]["Audience_n"].sum() / df["Audience_n"].sum() * 100

# ─────────────────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────────────────
k1, k2, k3 = st.columns(3)
cards = [
    ("Total Audience",        f"{total_audience:,}"),
    ("% Regional Audience",   f"{regional_pct:.0f}%"),
    ("Top Performing State",  top_state),
]
for col, (label, value) in zip([k1, k2, k3], cards):
    with col:
        st.markdown(f"""
        <div class='kpi-card'>
          <div class='kpi-label'>{label}</div>
          <div class='kpi-value'>{value}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:22px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# AI button
# ─────────────────────────────────────────────────────────
run = st.button("🚀 Generate AI Insights", type="primary")
context          = build_context(df)
insights_main    = st.session_state.get("ar_insights_main",    None)
insights_region  = st.session_state.get("ar_insights_region",  None)
insights_summary = st.session_state.get("ar_insights_summary", None)

if run:
    if not api_key:
        st.error("Enter your OpenAI API key in the sidebar.")
        st.stop()
    with st.spinner("Generating AI insights…"):
        try:
            PROMPT_MAIN = """You are a senior analyst for an Australian children's theatre company.
Based on the dataset summary, return exactly 4 bullet points (each starting with •) covering:
- National reach across states
- Year-on-year audience trends and peaks
- Growth patterns and what drove them
- Opportunities in underserved areas
Be concise and data-driven. No headers, no markdown formatting."""

            PROMPT_REGION = """You are a geographic access analyst for an Australian children's theatre company.
Based on the dataset, return exactly 4 bullet points (each starting with •) covering:
- Balance between Metro, Regional, and Remote audiences
- Level of inclusiveness across geographic areas
- Which regions are underrepresented (especially Remote)
- One strategic recommendation to improve outreach
Be concise and specific. No headers, no markdown formatting."""

            PROMPT_SUMMARY = """You are a senior analyst writing an executive summary paragraph for a board report
for an Australian children's theatre company. Write a single paragraph of 4-5 sentences that:
- Synthesises overall audience performance 2021-2025
- Mentions total audience reached and top-performing state
- Evaluates regional and remote reach
- Closes with one strategic recommendation
Be professional, clear, and data-driven. No headers or lists."""

            insights_main    = call_ai(api_key, model, PROMPT_MAIN,    context)
            insights_region  = call_ai(api_key, model, PROMPT_REGION,  context)
            insights_summary = call_ai(api_key, model, PROMPT_SUMMARY, context)

            st.session_state["ar_insights_main"]    = insights_main
            st.session_state["ar_insights_region"]  = insights_region
            st.session_state["ar_insights_summary"] = insights_summary
        except Exception as e:
            st.error(f"API error: {e}")
            st.stop()

# ─────────────────────────────────────────────────────────
# MAIN SECTION — Line chart + insights
# ─────────────────────────────────────────────────────────
st.markdown("<div class='card'>", unsafe_allow_html=True)
col_chart, col_insight = st.columns([6, 4])

with col_chart:
    yearly = df.groupby("Year")["Audience_n"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(6, 3.6))
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)
    ax.plot(yearly["Year"], yearly["Audience_n"],
            color=CHART_LINE, linewidth=2.5, marker="o", markersize=7, zorder=3)
    ax.fill_between(yearly["Year"], yearly["Audience_n"], alpha=0.07, color=CHART_LINE)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.set_xticks(yearly["Year"].astype(int))
    ax.set_title("Total Audience Reached", fontsize=13, fontweight="600",
                 color="#333", pad=12, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#ddd")
    ax.tick_params(colors=GRAY_TEXT, labelsize=10)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with col_insight:
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    if insights_main:
        render_bullets(insights_main)
    else:
        st.markdown("""<div class='insight-box'><ul>
          <li>Click <strong>Generate AI Insights</strong> to load dynamic analysis</li>
          <li>Will cover national reach, year-on-year trends, and growth opportunities</li>
        </ul></div>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# MID SECTION — Bullets + State table
# ─────────────────────────────────────────────────────────
st.markdown("<div class='card'>", unsafe_allow_html=True)
col_b, col_t = st.columns([5, 5])

with col_b:
    if insights_main:
        render_bullets(insights_main)
    else:
        st.markdown("""<div class='insight-box'><ul>
          <li>Strong national impact with most states achieving leading performance</li>
          <li>Broad and inclusive reach across Metro and Regional areas</li>
        </ul></div>""", unsafe_allow_html=True)

with col_t:
    state_df = df.groupby("State")["Audience_n"].sum().sort_values(ascending=False).reset_index()
    state_df.columns = ["State", "Audience"]
    state_df["Audience"] = state_df["Audience"].round(0).astype(int)
    state_df["%"] = (state_df["Audience"] / state_df["Audience"].sum() * 100).round(1).astype(str) + "%"
    rows = "".join(
        f"<tr><td>{r['State']}</td><td>{r['Audience']:,}</td><td>{r['%']}</td></tr>"
        for _, r in state_df.iterrows()
    )
    st.markdown(f"""
    <table class='styled-table'>
      <thead><tr><th>State</th><th>Audience</th><th>%</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# LOWER SECTION — Pie chart + regional insights
# ─────────────────────────────────────────────────────────
st.markdown("<div class='card'>", unsafe_allow_html=True)
col_pie, col_reg = st.columns([5, 5])

with col_pie:
    st.markdown("<div class='section-title'>Audience Distribution by Region Type</div>",
                unsafe_allow_html=True)
    reg = df.groupby("Regional II")["Audience_n"].sum()
    for cat in ["Metro", "Regional", "Remote"]:
        if cat not in reg.index:
            reg[cat] = 0
    reg = reg[["Metro", "Regional", "Remote"]]

    fig, ax = plt.subplots(figsize=(4.5, 4))
    fig.patch.set_facecolor(WHITE)
    wedges, texts, autotexts = ax.pie(
        reg,
        labels=reg.index,
        autopct="%1.1f%%",
        colors=["#E8673A", "#4CAF7D", "#E84040"],
        startangle=90,
        wedgeprops={"linewidth": 1.5, "edgecolor": "white"},
        textprops={"fontsize": 11, "color": "#333"},
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_color("white")
        at.set_fontweight("600")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with col_reg:
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    if insights_region:
        render_bullets(insights_region)
    else:
        st.markdown("""<div class='insight-box'><ul>
          <li>Click <strong>Generate AI Insights</strong> to load geographic analysis</li>
          <li>Will cover Metro vs Regional vs Remote balance and outreach recommendations</li>
        </ul></div>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# SUMMARY SECTION
# ─────────────────────────────────────────────────────────
st.markdown("""
<div style='font-size:17px;font-weight:600;color:#333;margin-bottom:8px;'>Summary</div>
""", unsafe_allow_html=True)
st.markdown("<hr class='divider'>", unsafe_allow_html=True)

if insights_summary:
    st.markdown(f"<div class='summary-box'>{insights_summary}</div>",
                unsafe_allow_html=True)
else:
    st.markdown("""<div class='summary-box' style='color:#bbb;font-style:italic;'>
    Click <strong>Generate AI Insights</strong> above to generate an AI-written
    executive summary based on the full dataset.
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# Download
# ─────────────────────────────────────────────────────────
if insights_summary:
    st.divider()
    report_md = f"""# Monkey Baa — Access & Audience Reach
## Expanding Youth Theatre Access: Social Outcomes Impact

**Total Audience:** {total_audience:,}
**% Regional:** {regional_pct:.0f}%
**Top State:** {top_state}

---
## Audience Trends
{insights_main}

---
## Geographic Distribution
{insights_region}

---
## Summary
{insights_summary}
"""
    st.download_button("📄 Download Report (.md)", report_md,
                       file_name="access_audience_reach.md",
                       mime="text/markdown")