"""
utils/data_loader.py
====================
Data loading, cleaning, and shared context builder.
Used by ALL report pages — do not edit without telling your partner.
"""

import io
import pandas as pd
import streamlit as st


# ─────────────────────────────────────────────────────────
# Load & clean
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
# Build context string for the OpenAI API
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
    buf.append(f"Cancelled tours: {(df['Status'] == 'Cancelled').sum()}")

    return "\n".join(buf)
