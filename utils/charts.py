"""
utils/charts.py
===============
Shared chart functions used across multiple report pages.
Add new charts here so both team members can reuse them.
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

PURPLE       = "#7c3aed"
LIGHT_PURPLE = "#a78bfa"
VERY_LIGHT   = "#ede9fe"


def chart_goal_vs_actual(df: pd.DataFrame):
    """Bar chart: Audience Goal vs Actual by Year (completed tours)."""
    completed = df[df["Status"] == "Completed"]
    yearly = completed.groupby("Year").agg(
        goal=("Audience Goal (n)", "sum"),
        actual=("Audience Actual (n)", "sum"),
    ).reset_index()
    fig, ax = plt.subplots(figsize=(7, 3.5))
    x = list(range(len(yearly)))
    w = 0.35
    ax.bar([i - w/2 for i in x], yearly["goal"],   width=w, label="Goal",   color=LIGHT_PURPLE, alpha=0.9)
    ax.bar([i + w/2 for i in x], yearly["actual"], width=w, label="Actual", color=PURPLE,       alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels(yearly["Year"].astype(str))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.set_title("Audience Goal vs Actual by Year (Completed)", fontsize=12)
    ax.legend()
    plt.tight_layout()
    return fig


def chart_audience_by_state(df: pd.DataFrame):
    """Horizontal bar chart: Total Audience by State (completed)."""
    completed = df[df["Status"] == "Completed"]
    state_agg = completed.groupby("State")["Audience Actual (n)"].sum().sort_values()
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.barh(state_agg.index, state_agg.values, color=PURPLE, alpha=0.85)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.set_title("Total Audience by State (Completed)", fontsize=12)
    plt.tight_layout()
    return fig


def chart_metro_vs_regional(df: pd.DataFrame):
    """Pie chart: Metro vs Regional audience split."""
    completed = df[df["Status"] == "Completed"]
    reg = completed.groupby("Regional.1")["Audience Actual (n)"].sum()
    reg = reg[reg.index != "Unknown"]
    if reg.empty:
        return None
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(
        reg, labels=reg.index, autopct="%1.0f%%",
        colors=[PURPLE, LIGHT_PURPLE, VERY_LIGHT][:len(reg)],
        startangle=90, wedgeprops={"linewidth": 0.5, "edgecolor": "white"},
    )
    ax.set_title("Metro vs Regional Audience Split", fontsize=12)
    plt.tight_layout()
    return fig


def chart_goal_achievement_dist(df: pd.DataFrame):
    """Histogram: Goal Achievement % distribution."""
    completed = df[df["Status"] == "Completed"]
    pct = completed["Goal Achievement %"].dropna()
    if pct.empty:
        return None
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.hist(pct, bins=20, color=PURPLE, alpha=0.85, edgecolor="white")
    ax.axvline(100, color="#dc2626", linestyle="--", linewidth=1.2, label="100% target")
    ax.set_title("Goal Achievement % Distribution (Completed)", fontsize=12)
    ax.set_xlabel("Goal Achievement %")
    ax.legend()
    plt.tight_layout()
    return fig


def chart_audience_by_year_line(df: pd.DataFrame):
    """Line chart: Audience trend year-on-year."""
    completed = df[df["Status"] == "Completed"]
    yearly = completed.groupby("Year")["Audience Actual (n)"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.plot(yearly["Year"], yearly["Audience Actual (n)"],
            marker="o", color=PURPLE, linewidth=2.5, markersize=7)
    ax.fill_between(yearly["Year"], yearly["Audience Actual (n)"],
                    alpha=0.15, color=PURPLE)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.set_title("Total Audience by Year (Completed)", fontsize=12)
    ax.set_xlabel("Year")
    plt.tight_layout()
    return fig


def chart_events_by_state(df: pd.DataFrame):
    """Bar chart: Number of events by state."""
    completed = df[df["Status"] == "Completed"]
    state_ev = completed.groupby("State")["Number of events"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(state_ev.index, state_ev.values, color=LIGHT_PURPLE, alpha=0.9, edgecolor="white")
    ax.set_title("Number of Events by State (Completed)", fontsize=12)
    ax.set_ylabel("Events")
    plt.tight_layout()
    return fig
