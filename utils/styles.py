"""
utils/styles.py
===============
Shared styles for all report pages.
Call apply_styles() at the top of every page.
"""

import streamlit as st

ORANGE      = "#E8673A"
ORANGE_DARK = "#C4512A"
BEIGE       = "#F5F0EA"
WHITE       = "#FFFFFF"
GRAY_TEXT   = "#555555"
TEAL_DARK   = "#1F4A4E"


def apply_styles():
    st.markdown(f"""
    <style>
      /* Page background */
      .stApp {{ background-color: {BEIGE}; }}

      /* Force main content text to be dark */
      .main .block-container p,
      .main .block-container span,
      .main .block-container div,
      .main .block-container h1,
      .main .block-container h2,
      .main .block-container h3,
      .main .block-container label,
      .main .block-container li {{
        color: #222222;
      }}

      /* Hide top header bar */
      [data-testid="stHeader"] {{ display: none !important; }}

      /* Sidebar background */
      [data-testid="stSidebar"] {{ background-color: {TEAL_DARK} !important; }}
      [data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.2) !important; }}
      [data-testid="stSidebar"] .stButton > button {{
        background-color: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 8px;
      }}

      /* Cards */
      .card {{ background-color: {WHITE}; border-radius: 12px; padding: 18px 22px; margin-bottom: 12px; }}
      .insight-box {{ background-color: #FDF3EE; border-radius: 10px; padding: 14px 16px; color: {GRAY_TEXT}; font-size: 13px; line-height: 1.65; }}
      .insight-box ul {{ margin: 0; padding-left: 16px; }}
      .insight-box li {{ margin-bottom: 8px; }}
      .kpi-card {{ background-color: {ORANGE}; border-radius: 12px; padding: 14px 12px; text-align: center; color: white; }}
      .kpi-label {{ font-size: 11px; font-weight: 500; opacity: .88; margin-bottom: 3px; }}
      .kpi-value {{ font-size: 28px; font-weight: 700; line-height: 1.1; }}
      .kpi-sub   {{ font-size: 11px; opacity: .82; margin-top: 3px; }}
      .section-label {{ font-size: 11px; font-weight: 600; color: {ORANGE}; text-transform: uppercase; letter-spacing: 0.7px; margin-bottom: 3px; }}
      .section-title {{ font-size: 15px; font-weight: 700; color: #333; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 2px solid {ORANGE}; display: inline-block; }}
      .summary-box {{ background-color: {WHITE}; border-radius: 12px; padding: 18px 22px; color: {GRAY_TEXT}; font-size: 13px; line-height: 1.78; }}
      .weak-card {{ background: #FFF8F5; border: 1.5px solid #F2D0C0; border-radius: 12px; padding: 18px 20px; }}
      .weak-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }}
      .warn-icon {{ width: 28px; height: 28px; flex-shrink: 0; background: #FFF8F5; border: 1.5px solid {ORANGE}; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 15px; }}
      .weak-title {{ font-size: 13px; font-weight: 700; color: #333; }}
      .weak-card ul {{ margin: 0; padding-left: 18px; color: #555; font-size: 13px; line-height: 1.75; }}
      .weak-card li {{ margin-bottom: 5px; }}
      .rec-primary {{ background: #FFF8F5; border: 1.5px solid {ORANGE}; border-radius: 12px; padding: 20px 24px; display: flex; gap: 16px; align-items: flex-start; margin-top: 12px; }}
      .star-bg {{ background: {ORANGE}; color: white; border-radius: 50%; width: 34px; height: 34px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 17px; }}
      .rec-primary-title {{ font-size: 14px; font-weight: 700; color: #333; margin-bottom: 8px; }}
      .rec-primary p {{ margin: 0; color: #555; font-size: 13px; line-height: 1.75; }}
      .rec-section-title {{ font-size: 15px; font-weight: 700; color: #333; margin: 4px 0 14px 0; padding-bottom: 8px; border-bottom: 2px solid {ORANGE}; display: inline-block; }}
      hr.div {{ border: none; border-top: 1px solid #e0d8d0; margin: 6px 0 14px 0; }}
      .stDownloadButton > button {{ width: 100%; }}
    </style>
    """, unsafe_allow_html=True)