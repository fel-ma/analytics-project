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

ORANGE      = "#E8673A"
ORANGE_DARK = "#C4512A"
BEIGE       = "#F5F0EA"
WHITE       = "#FFFFFF"
GRAY_TEXT   = "#555555"

st.markdown(f"""
<style>
  .stApp {{ background-color: {BEIGE}; }}
  .kpi-card {{ background-color:{ORANGE};border-radius:12px;padding:14px 12px;text-align:center;color:white; }}
  .kpi-label {{ font-size:11px;font-weight:500;opacity:.85;margin-bottom:3px; }}
  .kpi-value {{ font-size:28px;font-weight:700;line-height:1.1; }}
  .card {{ background-color:{WHITE};border-radius:12px;padding:16px 20px;margin-bottom:12px; }}
  .insight-box {{ background-color:#FDF3EE;border-radius:10px;padding:14px 16px;
                  color:{GRAY_TEXT};font-size:13px;line-height:1.6; }}
  .insight-box ul {{ margin:0;padding-left:16px; }}
  .insight-box li {{ margin-bottom:7px; }}
  .section-title {{ font-size:14px;font-weight:600;color:{ORANGE_DARK};
                    margin-bottom:8px;text-decoration:underline; }}
  .summary-box {{ background-color:{WHITE};border-radius:12px;padding:16px 20px;
                  color:{GRAY_TEXT};font-size:13px;line-height:1.7; }}
  table.st-table {{ width:100%;border-collapse:collapse;font-size:12px;color:{GRAY_TEXT}; }}
  table.st-table th {{ background-color:#f0e8e0;padding:6px 10px;text-align:left;
                       font-weight:600;border-bottom:2px solid #ddd; }}
  table.st-table td {{ padding:5px 10px;border-bottom:1px solid #eee; }}
  hr.div {{ border:none;border-top:1px solid #e0d8d0;margin:6px 0 12px 0; }}
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────
def build_context(df):
    total = df["Audience_n"].sum()
    buf = [f"Monkey Baa Audience 2021-2025 | {len(df)} rows | Total: {int(total):,}"]
    buf.append("\nBY YEAR:")
    for y, v in df.groupby("Year")["Audience_n"].sum().items():
        buf.append(f"  {int(y)}: {int(v):,}")
    buf.append("\nBY STATE:")
    for s, v in df.groupby("State")["Audience_n"].sum().sort_values(ascending=False).items():
        buf.append(f"  {s}: {int(v):,} ({v/total*100:.1f}%)")
    buf.append("\nREGION SPLIT:")
    for r, v in df.groupby("Regional II")["Audience_n"].sum().items():
        buf.append(f"  {r}: {int(v):,} ({v/total*100:.1f}%)")
    buf.append(f"\nTOP STATE: {df.groupby('State')['Audience_n'].sum().idxmax()}")
    reg = df[df["Regional II"]=="Regional"]["Audience_n"].sum()/total*100
    rem = df[df["Regional II"]=="Remote"]["Audience_n"].sum()/total*100
    buf.append(f"REGIONAL%: {reg:.1f} | REMOTE%: {rem:.1f}")
    return "\n".join(buf)

def call_ai(api_key, model, system_prompt, context):
    r = OpenAI(api_key=api_key).chat.completions.create(
        model=model,
        messages=[{"role":"system","content":system_prompt},
                  {"role":"user","content":f"Data:\n{context}"}],
        temperature=0.3, max_tokens=500,
    )
    return r.choices[0].message.content.strip()

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
total_audience = int(df["Audience_n"].sum())
top_state      = df.groupby("State")["Audience_n"].sum().idxmax()
regional_pct   = df[df["Regional II"]=="Regional"]["Audience_n"].sum() / df["Audience_n"].sum() * 100

k1, k2, k3 = st.columns(3)
for col, label, value in [
    (k1, "Total Audience",       f"{total_audience:,}"),
    (k2, "% Regional Audience",  f"{regional_pct:.0f}%"),
    (k3, "Top Performing State", top_state),
]:
    with col:
        st.markdown(f"""<div class='kpi-card'>
          <div class='kpi-label'>{label}</div>
          <div class='kpi-value'>{value}</div></div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)

# ── AI button ────────────────────────────────────────────
run              = st.button("🚀 Generate AI Insights", type="primary")
context          = build_context(df)
insights_main    = st.session_state.get("ar_main",    None)
insights_region  = st.session_state.get("ar_region",  None)
insights_summary = st.session_state.get("ar_summary", None)

if run:
    if not api_key:
        st.error("Enter your OpenAI API key in the sidebar on the Home page.")
        st.stop()
    with st.spinner("Generating insights…"):
        try:
            insights_main = call_ai(api_key, model,
                "Return exactly 4 bullet points (starting with •) on: national reach, "
                "year-on-year trends, growth patterns, underserved opportunities. "
                "No headers, no markdown.", context)

            insights_region = call_ai(api_key, model,
                "Return exactly 4 bullet points (starting with •) on: Metro vs Regional vs Remote "
                "balance, geographic inclusiveness, underrepresented regions, one recommendation. "
                "No headers, no markdown.", context)

            insights_summary = call_ai(api_key, model,
                "Write one paragraph (4-5 sentences) for a board report covering: "
                "overall performance 2021-2025, total audience and top state, "
                "regional/remote reach, one strategic recommendation. Professional tone.", context)

            st.session_state["ar_main"]    = insights_main
            st.session_state["ar_region"]  = insights_region
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

# ── Section 2: insights left, table right (with title + orange header) ──
st.markdown("<div class='card'>", unsafe_allow_html=True)
c3, c4 = st.columns([5, 5])
with c3:
    st.markdown(bullets_html(insights_main) if insights_main
                else placeholder("Insights will appear here after generation."),
                unsafe_allow_html=True)
with c4:
    sdf = df.groupby("State")["Audience_n"].sum().sort_values(ascending=False).reset_index()
    sdf.columns = ["State","Audience"]
    sdf["Audience"] = sdf["Audience"].round(0).astype(int)
    sdf["%"] = (sdf["Audience"]/sdf["Audience"].sum()*100).round(1).astype(str)+"%"
    rows = "".join(
        f"<tr><td style='text-align:center;'>{r['State']}</td>"
        f"<td style='text-align:center;'>{r['Audience']:,}</td>"
        f"<td style='text-align:center;'>{r['%']}</td></tr>"
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
                   text-align:center;border:1px solid #c85a2a;'>%</th>
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

# ── Summary ──────────────────────────────────────────────
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
    md = f"""# Monkey Baa — Access & Audience Reach
**Total:** {total_audience:,} | **Regional:** {regional_pct:.0f}% | **Top State:** {top_state}

## Trends
{insights_main}

## Geographic Distribution
{insights_region}

## Summary
{insights_summary}
"""
    st.download_button("📄 Download Report (.md)", md,
                       file_name="access_audience_reach.md", mime="text/markdown")