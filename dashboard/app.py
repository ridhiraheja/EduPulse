import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ============================================================
# 1. PAGE CONFIGURATION & METADATA
# ============================================================

st.set_page_config(
    page_title="EduPulse | State Education Intelligence Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 2. SESSION STATE INITIALIZATION
# ============================================================

if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "🏠 Home"

if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "dark"

if "show_ai_agent" not in st.session_state:
    st.session_state["show_ai_agent"] = False

if "selected_school_idx" not in st.session_state:
    st.session_state["selected_school_idx"] = 0

if "ai_input_text" not in st.session_state:
    st.session_state["ai_input_text"] = ""

if "filter_district" not in st.session_state:
    st.session_state["filter_district"] = "All Districts"

if "filter_block" not in st.session_state:
    st.session_state["filter_block"] = "All Blocks"

if "filter_type" not in st.session_state:
    st.session_state["filter_type"] = "All Levels"

if "filter_medium" not in st.session_state:
    st.session_state["filter_medium"] = "All Mediums"

if "filter_risk_band" not in st.session_state:
    st.session_state["filter_risk_band"] = "All Risk Bands"

if "search_query" not in st.session_state:
    st.session_state["search_query"] = ""

# Policy Simulator State
if "sim_att_val" not in st.session_state:
    st.session_state["sim_att_val"] = 5.0
if "sim_score_val" not in st.session_state:
    st.session_state["sim_score_val"] = 5.0
if "sim_infra_val" not in st.session_state:
    st.session_state["sim_infra_val"] = 0.5
if "sim_proxy_val" not in st.session_state:
    st.session_state["sim_proxy_val"] = 2.0

# ============================================================
# 3. DATA LOADING & CACHING
# ============================================================

@st.cache_data(ttl=3600)
def load_all_datasets():
    analytics = pd.read_csv("data/processed/school_analytics.csv")
    test_scores = pd.read_csv("data/processed/clean_test_scores.csv")
    attendance = pd.read_csv("data/processed/clean_attendance.csv")
    mdm = pd.read_csv("data/processed/clean_mid_day_meal_procurement.csv")
    infra = pd.read_csv("data/processed/clean_infrastructure.csv")
    
    attendance["date"] = pd.to_datetime(attendance["date"], errors="coerce")
    test_scores["date"] = pd.to_datetime(test_scores["date"], errors="coerce")
    
    return analytics, test_scores, attendance, mdm, infra

try:
    df_analytics, df_tests, df_att, df_mdm, df_infra = load_all_datasets()
except Exception as e:
    st.error(f"Error loading data files: {e}")
    st.stop()

# ============================================================
# 4. DYNAMIC THEME SYSTEM (DARK & LIGHT MODE WITH CSS)
# ============================================================

is_dark = (st.session_state["theme_mode"] == "dark")

if is_dark:
    app_bg = "#080c16"
    card_bg = "#0d1424"
    card_border = "rgba(255, 255, 255, 0.08)"
    text_primary = "#f8fafc"
    text_secondary = "#94a3b8"
    text_muted = "#64748b"
    sidebar_bg = "#080c16"
    input_bg = "#0d1424"
    pill_bg = "#0d1424"
    alert_row_bg = "rgba(255, 255, 255, 0.02)"
    hero_grad = "linear-gradient(135deg, #0d1424 0%, #111a30 50%, #15203c 100%)"
else:
    app_bg = "#f1f5f9"
    card_bg = "#ffffff"
    card_border = "rgba(0, 0, 0, 0.08)"
    text_primary = "#0f172a"
    text_secondary = "#475569"
    text_muted = "#64748b"
    sidebar_bg = "#ffffff"
    input_bg = "#ffffff"
    pill_bg = "#ffffff"
    alert_row_bg = "rgba(0, 0, 0, 0.02)"
    hero_grad = "linear-gradient(135deg, #e0e7ff 0%, #ede9fe 50%, #fce7f3 100%)"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}

    /* App Background */
    .stApp {{
        background-color: {app_bg} !important;
        color: {text_primary} !important;
    }}

    .block-container {{
        padding-top: 0.4rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1.4rem !important;
        padding-right: 1.4rem !important;
        max-width: 98% !important;
    }}

    /* Remove Streamlit default header & decorations */
    header[data-testid="stHeader"] {{
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        background: transparent !important;
    }}
    div[data-testid="stDecoration"] {{ display: none !important; }}
    div[data-testid="stToolbar"] {{ top: 6px !important; right: 10px !important; }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
        border-right: 1px solid {card_border} !important;
    }}

    section[data-testid="stSidebar"] > div {{
        padding-top: 1rem !important;
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
    }}

    /* Completely hide any radio labels (removes "SideNav" or any label text) */
    div[data-testid="stRadio"] > label {{
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    div[data-testid="stRadio"] > div {{
        display: flex;
        flex-direction: column;
        gap: 5px;
    }}

    div[data-testid="stRadio"] label {{
        background: transparent !important;
        padding: 8px 12px !important;
        border-radius: 10px !important;
        color: {text_secondary} !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        border: 1px solid transparent !important;
        margin: 0 !important;
    }}

    div[data-testid="stRadio"] label:hover {{
        background: rgba(255, 255, 255, 0.05) !important;
        color: {text_primary} !important;
    }}

    /* Active navigation rail item */
    div[data-testid="stRadio"] label[data-checked="true"],
    div[data-testid="stRadio"] label:has(input:checked) {{
        background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4) !important;
        border-radius: 10px !important;
    }}

    div[data-testid="stRadio"] input {{ display: none !important; }}

    /* Top Search Bar */
    .top-search-input input {{
        background: {input_bg} !important;
        border: 1px solid {card_border} !important;
        border-radius: 10px !important;
        color: {text_primary} !important;
        font-size: 12.5px !important;
        padding: 8px 14px !important;
        height: 38px !important;
    }}

    .top-search-input input::placeholder {{ color: {text_muted} !important; }}

    .top-pill-btn {{
        background: {pill_bg};
        border: 1px solid {card_border};
        border-radius: 10px;
        padding: 0 12px;
        display: flex;
        align-items: center;
        gap: 8px;
        height: 38px;
        font-size: 11.5px;
        color: {text_secondary};
    }}

    .user-pill-container {{
        display: flex;
        align-items: center;
        gap: 8px;
        background: {pill_bg};
        border: 1px solid {card_border};
        border-radius: 10px;
        padding: 4px 12px;
        height: 38px;
    }}

    .user-avatar-circle {{
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        color: white;
        font-size: 11px;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    /* Prominent Magenta Glowing AI Button in Header */
    .btn-ai-header button {{
        background: linear-gradient(135deg, #ec4899 0%, #a855f7 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 12.5px !important;
        border: none !important;
        border-radius: 9999px !important;
        padding: 8px 18px !important;
        box-shadow: 0 4px 16px rgba(236, 72, 153, 0.45) !important;
        height: 38px !important;
        letter-spacing: 0.2px;
        transition: all 0.2s ease !important;
    }}

    .btn-ai-header button:hover {{
        transform: translateY(-1px) scale(1.02) !important;
        box-shadow: 0 6px 22px rgba(236, 72, 153, 0.6) !important;
        color: #ffffff !important;
    }}

    /* Centered EduPulse AI modal */
    [data-testid="stDialog"] > div {{
        border-radius: 20px !important;
        border: 1px solid rgba(168, 85, 247, 0.45) !important;
        background: linear-gradient(145deg, #0b1224 0%, #111a32 100%) !important;
        box-shadow: 0 24px 80px rgba(0, 0, 0, 0.65),
                    0 0 45px rgba(139, 92, 246, 0.18) !important;
    }}

    [data-testid="stDialog"] textarea {{
        border: 1px solid rgba(139, 92, 246, 0.75) !important;
        border-radius: 14px !important;
        background: rgba(18, 32, 61, 0.95) !important;
        color: #f8fafc !important;
        min-height: 105px !important;
    }}

    [data-testid="stDialog"] textarea:focus {{
        border-color: #a855f7 !important;
        box-shadow: 0 0 0 1px #a855f7,
                    0 0 18px rgba(168, 85, 247, 0.25) !important;
    }}

    [data-testid="stDialog"] .stButton > button {{
        border-radius: 11px !important;
        min-height: 42px !important;
        background: rgba(255, 255, 255, 0.035) !important;
        border: 1px solid rgba(148, 163, 184, 0.18) !important;
        color: #e2e8f0 !important;
    }}

    [data-testid="stDialog"] .stButton > button:hover {{
        border-color: rgba(168, 85, 247, 0.65) !important;
        background: rgba(168, 85, 247, 0.10) !important;
        color: #ffffff !important;
    }}

    .ai-modal-send button {{
        background: linear-gradient(135deg, #8b5cf6, #ec4899) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        box-shadow: 0 5px 20px rgba(139, 92, 246, 0.35) !important;
    }}

    /* Hero Containers */
    .hero-card-container {{
        background: {hero_grad};
        border: 1px solid {card_border};
        border-radius: 16px;
        padding: 18px 22px;
        height: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}

    .scope-card-container {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 16px;
        padding: 16px 20px;
        height: 100%;
    }}

    .scope-card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }}

    /* Selectboxes */
    div[data-testid="stSelectbox"] label {{
        font-size: 11px !important;
        font-weight: 600 !important;
        color: {text_secondary} !important;
        margin-bottom: 2px !important;
    }}

    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        background-color: {app_bg} !important;
        border: 1px solid {card_border} !important;
        border-radius: 8px !important;
        color: {text_primary} !important;
        font-size: 11.5px !important;
        min-height: 32px !important;
        height: 32px !important;
    }}

    /* 6 Top KPI Cards */
    .kpi-row-card {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 14px;
        padding: 14px 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        height: 100%;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }}

    .kpi-row-card:hover {{
        transform: translateY(-2px);
    }}

    .kpi-sq-icon {{
        width: 42px;
        height: 42px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 19px;
        flex-shrink: 0;
    }}

    .kpi-text-box {{ flex: 1; min-width: 0; }}

    .kpi-label-line {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2px;
    }}

    .kpi-label-text {{
        font-size: 11px;
        color: {text_secondary};
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    .kpi-val-text {{
        font-size: 22px;
        font-weight: 800;
        color: {text_primary};
        letter-spacing: -0.5px;
        line-height: 1.2;
    }}

    .kpi-sub-text {{
        font-size: 10.5px;
        color: {text_muted};
        margin-top: 1px;
        font-weight: 500;
    }}

    /* Horizontal Nav Tabs */
    .st-htab button {{
        background: {card_bg} !important;
        border: 1px solid {card_border} !important;
        color: {text_secondary} !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 6px 12px !important;
        transition: all 0.2s ease !important;
        white-space: nowrap !important;
    }}

    .st-htab button:hover {{
        background: rgba(59, 130, 246, 0.15) !important;
        color: {text_primary} !important;
    }}

    .st-htab-active button {{
        background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        padding: 6px 12px !important;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35) !important;
        white-space: nowrap !important;
    }}

    /* Panels */
    .exact-panel {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 16px;
        padding: 18px 20px;
        height: 100%;
        position: relative;
    }}

    .exact-panel-head {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }}

    .exact-panel-title {{
        font-size: 14px;
        font-weight: 700;
        color: {text_primary};
        display: flex;
        align-items: center;
        gap: 6px;
    }}

    .exact-panel-sub {{
        font-size: 11px;
        color: {text_muted};
        margin-top: 2px;
    }}

    /* ══════════════════════════════════════════════
       QUICK ACTIONS BUTTONS (REAL STREAMLIT BUTTONS WITH EXACT GRADIENTS)
       ══════════════════════════════════════════════ */
    .qa-wrap-stack {{
        display: flex;
        flex-direction: column;
        gap: 6px;
    }}

    .qa-wrap-stack div[data-testid="stButton"] {{
        margin-bottom: 4px !important;
    }}

    .qa-wrap-stack div[data-testid="stButton"] button {{
        height: 38px !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-align: left !important;
        padding: 0 14px !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        width: 100% !important;
    }}

    .qa-wrap-stack div[data-testid="stButton"] button:hover {{
        transform: translateX(4px) !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4) !important;
        color: #ffffff !important;
    }}

    /* Individual Custom Gradients from Image */
    .qa-btn-1 button {{ background: linear-gradient(90deg, #6d28d9 0%, #9333ea 100%) !important; }}
    .qa-btn-2 button {{ background: linear-gradient(90deg, #1d4ed8 0%, #2563eb 100%) !important; }}
    .qa-btn-3 button {{ background: linear-gradient(90deg, #831843 0%, #9d174d 100%) !important; }}
    .qa-btn-4 button {{ background: linear-gradient(90deg, #0f766e 0%, #0d9488 100%) !important; }}
    .qa-btn-5 button {{ background: linear-gradient(90deg, #78350f 0%, #92400e 100%) !important; }}
    .qa-btn-6 button {{ background: linear-gradient(90deg, #1e3a8a 0%, #1d4ed8 100%) !important; }}
    .qa-btn-7 button {{ background: linear-gradient(90deg, #1e293b 0%, #334155 100%) !important; }}

    /* Recent Alerts Rows */
    .recent-alert-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 9px 12px;
        border-radius: 10px;
        margin-bottom: 6px;
        background: {alert_row_bg};
        border: 1px solid {card_border};
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
    """,
    unsafe_allow_html=True
)

# Plotly Safe Layout Helper (Respects Dark / Light Mode)
def make_layout(**kwargs):
    layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color=text_secondary, size=11),
        margin=dict(l=15, r=15, t=25, b=20),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)" if is_dark else "rgba(0,0,0,0.06)", zeroline=False, color=text_muted),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)" if is_dark else "rgba(0,0,0,0.06)", zeroline=False, color=text_muted),
        legend=dict(font=dict(color=text_primary, size=10.5), bgcolor="rgba(13,20,36,0.8)" if is_dark else "rgba(255,255,255,0.9)")
    )
    for k, v in kwargs.items():
        if isinstance(v, dict) and k in layout and isinstance(layout[k], dict):
            layout[k] = {**layout[k], **v}
        else:
            layout[k] = v
    return layout

# ============================================================
# 5. LEFT SIDEBAR (COMPACT RAIL WITHOUT "SideNav" TEXT)
# ============================================================

with st.sidebar:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 4px 6px 12px 6px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 32px; height: 32px; border-radius: 8px; background: linear-gradient(135deg, #2563eb, #7c3aed); display: flex; align-items: center; justify-content: center; font-size: 16px; box-shadow: 0 4px 12px rgba(37,99,235,0.4);">
                    🎓
                </div>
                <div style="font-size: 16px; font-weight: 800; color: {text_primary}; letter-spacing: -0.3px;">EduPulse</div>
            </div>
            <div style="font-size: 12px; color: {text_muted};">&lt;</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    sidebar_nav_items = [
        "🏠 Home",
        "📊 Analytics",
        "🏫 Schools",
        "👥 Students",
        "📅 Attendance",
        "📝 Test Scores",
        "🍱 Mid-Day Meal",
        "🏢 Infrastructure",
        "⚠️ Risk Analysis",
        "🔮 Policy Simulator",
        "🛡️ Data Rescue & Audit"
    ]

    curr_nav_idx = sidebar_nav_items.index(st.session_state["nav_page"]) if st.session_state["nav_page"] in sidebar_nav_items else 0
    # Radio widget with empty label to ensure no "SideNav" text appears
    selected_sidebar_item = st.radio("", sidebar_nav_items, index=curr_nav_idx, label_visibility="collapsed")

    if selected_sidebar_item != st.session_state["nav_page"]:
        st.session_state["nav_page"] = selected_sidebar_item
        st.session_state["show_ai_agent"] = False
        st.rerun()

    st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True)

    # ── FUNCTIONAL LIGHT / DARK MODE TOGGLE ──
    st.markdown(f"<div style='border-top: 1px solid {card_border}; padding-top: 12px;'></div>", unsafe_allow_html=True)
    t_c1, t_c2 = st.columns([0.8, 2.2])
    with t_c1:
        st.markdown(f"<div style='font-size: 18px; text-align: center; padding-top: 4px;'>{'🌙' if is_dark else '☀️'}</div>", unsafe_allow_html=True)
    with t_c2:
        dark_toggle_val = st.toggle("Dark Theme", value=is_dark, key="theme_toggle_switch")
        new_theme = "dark" if dark_toggle_val else "light"
        if new_theme != st.session_state["theme_mode"]:
            st.session_state["theme_mode"] = new_theme
            st.rerun()

# ============================================================
# 6. TOP HEADER (FUNCTIONAL SEARCH, DATE, USER, AI BUTTON)
# ============================================================

top_h1, top_h2 = st.columns([3.6, 2.4])

with top_h1:
    st.markdown('<div class="top-search-input">', unsafe_allow_html=True)
    search_input_val = st.text_input(
        "Search Platform",
        value=st.session_state.get("search_query", ""),
        placeholder="🔍 Search by school name, district, block, or ID... (Press Enter)",
        label_visibility="collapsed",
        key="search_query"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with top_h2:
    th_c1, th_c2, th_c3 = st.columns([1.2, 1.4, 1.6])
    with th_c1:
        st.markdown(
            f"""
            <div class="top-pill-btn">
                <span>📅</span>
                <span style="font-weight: 600; color: {text_primary};">{datetime.now().strftime("%b %d, %Y")}</span>
                <span style="font-size: 9px; color: {text_muted};">▼</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with th_c2:
        st.markdown(
            f"""
            <div class="user-pill-container">
                <div class="user-avatar-circle">RR</div>
                <div style="line-height: 1.1; overflow: hidden; flex: 1;">
                    <div style="font-size: 11px; font-weight: 700; color: {text_primary};">Ridhi Raheja</div>
                    <div style="font-size: 9.5px; color: {text_muted};">Analyst</div>
                </div>
                <span style="font-size: 9px; color: {text_muted};">▼</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with th_c3:
        st.markdown('<div class="btn-ai-header">', unsafe_allow_html=True)
        if st.button("✦ Ask EduPulse AI", use_container_width=True):
            st.session_state["show_ai_agent"] = not st.session_state["show_ai_agent"]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 7. LIVE SEARCH RESULTS OVERLAY (WHEN SEARCH QUERY IS ENTERED)
# ============================================================

search_query_clean = st.session_state.get("search_query", "").strip().lower()

if search_query_clean:
    search_matches = df_analytics[
        df_analytics["school_name"].str.lower().str.contains(search_query_clean, na=False) |
        df_analytics["school_id"].astype(str).str.lower().str.contains(search_query_clean, na=False) |
        df_analytics["district"].str.lower().str.contains(search_query_clean, na=False) |
        df_analytics["block"].str.lower().str.contains(search_query_clean, na=False)
    ]

    st.markdown(
        f"""
        <div class="exact-panel" style="margin-bottom: 14px; border: 1px solid rgba(56, 189, 248, 0.4);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="font-size: 14px; font-weight: 700; color: #38bdf8;">
                    🔍 Found {len(search_matches):,} Matching Schools for "{st.session_state['search_query']}"
                </div>
            </div>
        """,
        unsafe_allow_html=True
    )

    s_btn_c1, _ = st.columns([1.2, 5])
    with s_btn_c1:
        if st.button("✕ Clear Search Filter", key="btn_clear_search_top", use_container_width=True):
            st.session_state["search_query"] = ""
            st.rerun()

    if len(search_matches) > 0:
        # Show quick action cards for top matching schools
        for idx, srow in search_matches.head(5).iterrows():
            s_c1, s_c2, s_c3, s_c4, s_c5, s_c6 = st.columns([2.5, 1.2, 1.1, 1.1, 1.1, 1.3])
            s_c1.markdown(f"**🏫 {srow['school_name']}** (`{srow['school_id']}`)")
            s_c2.markdown(f"📍 {srow['district']} ({srow['block']})")
            s_c3.markdown(f"📊 {srow['average_attendance_rate']:.1f}% Att.")
            s_c4.markdown(f"📝 {srow['average_test_score']:.1f}% Score")
            s_c5.markdown(f"🛡️ **{srow['retention_risk_indicator']:.1f}** Risk")
            with s_c6:
                if st.button("Inspect 360° →", key=f"s_res_btn_{srow['school_id']}", use_container_width=True):
                    school_names_list = sorted(df_analytics["school_name"].unique())
                    if srow["school_name"] in school_names_list:
                        st.session_state["selected_school_idx"] = school_names_list.index(srow["school_name"])
                    st.session_state["nav_page"] = "🏫 Schools"
                    st.rerun()
            st.markdown("<hr style='border-color: rgba(255,255,255,0.04); margin: 4px 0;'/>", unsafe_allow_html=True)
    else:
        st.info(f"No schools found matching '{st.session_state['search_query']}'. Try searching by district (e.g. 'Amritsar'), block, or partial school name.")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# 8. ROW 1: HERO SECTION (WELCOME CARD & INLINE FILTERS SCOPE)
# ============================================================

hero_left, hero_right = st.columns([1.32, 1.0])

with hero_left:
    svg_illustration = """
    <svg width="180" height="130" viewBox="0 0 180 130" fill="none" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;">
      <defs>
        <radialGradient id="haloGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.4"/>
          <stop offset="60%" stop-color="#8b5cf6" stop-opacity="0.15"/>
          <stop offset="100%" stop-color="#080c16" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="capGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#60a5fa"/>
          <stop offset="40%" stop-color="#2563eb"/>
          <stop offset="100%" stop-color="#1e1b4b"/>
        </linearGradient>
        <linearGradient id="bookP1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.85"/>
          <stop offset="100%" stop-color="#0f172a" stop-opacity="0.95"/>
        </linearGradient>
      </defs>
      <circle cx="90" cy="65" r="55" fill="url(#haloGlow)"/>
      <circle cx="35" cy="30" r="1.8" fill="#38bdf8" opacity="0.8"/>
      <circle cx="145" cy="35" r="1.5" fill="#c084fc" opacity="0.9"/>
      <circle cx="25" cy="80" r="1.5" fill="#38bdf8" opacity="0.7"/>
      <circle cx="155" cy="85" r="1.8" fill="#38bdf8" opacity="0.8"/>
      <path d="M30 92 C60 80 85 88 90 92 C95 88 120 80 150 92 C145 102 120 96 90 100 C60 96 35 102 30 92 Z" fill="url(#bookP1)"/>
      <path d="M35 88 C60 78 85 86 90 90 C95 86 120 78 145 88 C140 96 120 90 90 94 C60 90 40 96 35 88 Z" fill="#0f172a" stroke="#38bdf8" stroke-width="1.2"/>
      <polygon points="90,32 130,46 90,60 50,46" fill="url(#capGrad)" stroke="#93c5fd" stroke-width="1.2"/>
      <path d="M70 53 L70 64 C70 73 110 73 110 64 L110 53 Z" fill="#0f172a" stroke="#3b82f6" stroke-width="1"/>
      <ellipse cx="90" cy="46" rx="3.5" ry="2" fill="#fbbf24"/>
      <path d="M90 46 Q112 48 118 58 Q120 65 118 72" fill="none" stroke="#f59e0b" stroke-width="1.8" stroke-linecap="round"/>
      <polygon points="116,71 121,72 120,81 115,81" fill="#fbbf24"/>
    </svg>
    """
    
    st.markdown(
        f"""
        <div class="hero-card-container">
            <div style="flex: 1; padding-right: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 20px; font-weight: 800; color: {text_primary}; letter-spacing: -0.4px;">
                        👋 Welcome to EduPulse
                    </div>
                </div>
                <div style="font-size: 12px; color: #38bdf8; font-weight: 600; margin-top: 3px; display: flex; align-items: center; gap: 8px;">
                    <span>State Education Intelligence Platform</span>
                    <span style="font-size: 10px; background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 1px 7px; border-radius: 9999px;">Overview Suite</span>
                </div>
                <div style="font-size: 12px; color: {text_secondary}; line-height: 1.55; margin-top: 8px; max-width: 90%;">
                    Monitoring student attendance, academic performance, infrastructure, mid-day meal welfare and retention risk indicators across schools.
                </div>
            </div>
            {svg_illustration}
        </div>
        """,
        unsafe_allow_html=True
    )

with hero_right:
    st.markdown(
        f"""
        <div class="scope-card-container">
            <div class="scope-card-header">
                <div style="font-size: 13px; font-weight: 700; color: {text_primary}; display: flex; align-items: center; gap: 6px;">
                    <span>🎛️</span>
                    <span>Filters & Scope</span>
                </div>
                <a href="#" style="font-size: 11px; color: #38bdf8; text-decoration: none;">View All</a>
            </div>
        """,
        unsafe_allow_html=True
    )

    sc_r1_c1, sc_r1_c2, sc_r1_c3 = st.columns(3)
    all_districts = sorted(df_analytics["district"].dropna().unique())
    with sc_r1_c1:
        sel_dist = st.selectbox("District", ["All Districts"] + all_districts, key="filter_district")

    avail_blocks = sorted(df_analytics[df_analytics["district"] == sel_dist]["block"].dropna().unique()) if sel_dist != "All Districts" else sorted(df_analytics["block"].dropna().unique())
    if st.session_state.get("filter_block") not in (["All Blocks"] + avail_blocks):
        st.session_state["filter_block"] = "All Blocks"
    with sc_r1_c2:
        sel_block = st.selectbox("Block", ["All Blocks"] + avail_blocks, key="filter_block")

    school_types = sorted(df_analytics["school_type"].dropna().unique())
    with sc_r1_c3:
        sel_type = st.selectbox("School Level", ["All Levels"] + school_types, key="filter_type")

    sc_r2_c1, sc_r2_c2 = st.columns(2)
    mediums = sorted(df_analytics["medium"].dropna().unique())
    with sc_r2_c1:
        sel_med = st.selectbox("Instruction Medium", ["All Mediums"] + mediums, key="filter_medium")

    risk_bands = ["All Risk Bands", "Low (0–20)", "Moderate (20–25)", "High (25–30)", "Critical (30+)"]
    with sc_r2_c2:
        sel_risk = st.selectbox("Analytical Risk Band", risk_bands, key="filter_risk_band")

    st.markdown("</div>", unsafe_allow_html=True)

# Dynamic Filter Application
filtered_df = df_analytics.copy()
if sel_dist != "All Districts": filtered_df = filtered_df[filtered_df["district"] == sel_dist]
if sel_block != "All Blocks": filtered_df = filtered_df[filtered_df["block"] == sel_block]
if sel_type != "All Levels": filtered_df = filtered_df[filtered_df["school_type"] == sel_type]
if sel_med != "All Mediums": filtered_df = filtered_df[filtered_df["medium"] == sel_med]

if sel_risk == "Low (0–20)":
    filtered_df = filtered_df[filtered_df["retention_risk_indicator"] <= 20.0]
elif sel_risk == "Moderate (20–25)":
    filtered_df = filtered_df[(filtered_df["retention_risk_indicator"] > 20.0) & (filtered_df["retention_risk_indicator"] <= 25.0)]
elif sel_risk == "High (25–30)":
    filtered_df = filtered_df[(filtered_df["retention_risk_indicator"] > 25.0) & (filtered_df["retention_risk_indicator"] <= 30.0)]
elif sel_risk == "Critical (30+)":
    filtered_df = filtered_df[filtered_df["retention_risk_indicator"] > 30.0]

if search_query_clean:
    filtered_df = filtered_df[
        filtered_df["school_name"].str.lower().str.contains(search_query_clean, na=False) |
        filtered_df["school_id"].astype(str).str.lower().str.contains(search_query_clean, na=False) |
        filtered_df["district"].str.lower().str.contains(search_query_clean, na=False) |
        filtered_df["block"].str.lower().str.contains(search_query_clean, na=False)
    ]

# If search yielded zero inside current filter, fallback to total matches so user still sees statistics
if len(filtered_df) == 0 and search_query_clean:
    filtered_df = search_matches

if len(filtered_df) == 0:
    st.warning("⚠️ No schools match the current filter criteria.")
    st.stop()

# Aggregate Core Numbers
tot_schools = len(filtered_df)
tot_students = filtered_df["total_enrolled_students"].sum()
avg_attendance = filtered_df["average_attendance_rate"].mean()
avg_score = filtered_df["average_test_score"].mean()
avg_infra = filtered_df["average_facility_count"].mean()
avg_risk = filtered_df["retention_risk_indicator"].mean()

# ============================================================
# 9. ROW 2: 6 TOP KPI CARDS (EXACT MATCH)
# ============================================================

st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
k_c1, k_c2, k_c3, k_c4, k_c5, k_c6 = st.columns(6)

with k_c1:
    st.markdown(
        f"""
        <div class="kpi-row-card">
            <div class="kpi-sq-icon" style="background: rgba(37, 99, 235, 0.18); border: 1px solid rgba(59, 130, 246, 0.3); color: #38bdf8;">🏫</div>
            <div class="kpi-text-box">
                <div class="kpi-label-line">
                    <span class="kpi-label-text">Schools</span>
                    <span style="color:#10b981; font-size:10px;">▣</span>
                </div>
                <div class="kpi-val-text">{tot_schools:,}</div>
                <div class="kpi-sub-text">Monitored Scope</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k_c2:
    st.markdown(
        f"""
        <div class="kpi-row-card">
            <div class="kpi-sq-icon" style="background: rgba(16, 185, 129, 0.18); border: 1px solid rgba(16, 185, 129, 0.3); color: #34d399;">👥</div>
            <div class="kpi-text-box">
                <div class="kpi-label-line">
                    <span class="kpi-label-text">Enrollment</span>
                    <span style="color:#10b981; font-size:10px;">▣</span>
                </div>
                <div class="kpi-val-text">{tot_students/1000:.1f}k</div>
                <div class="kpi-sub-text">Active Students</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k_c3:
    st.markdown(
        f"""
        <div class="kpi-row-card">
            <div class="kpi-sq-icon" style="background: rgba(2, 132, 199, 0.18); border: 1px solid rgba(56, 189, 248, 0.3); color: #38bdf8;">📅</div>
            <div class="kpi-text-box">
                <div class="kpi-label-line">
                    <span class="kpi-label-text">Avg. Attendance</span>
                    <span style="color:#38bdf8; font-size:10px;">▣</span>
                </div>
                <div class="kpi-val-text">{avg_attendance:.1f}%</div>
                <div class="kpi-sub-text">Average Presence</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k_c4:
    st.markdown(
        f"""
        <div class="kpi-row-card">
            <div class="kpi-sq-icon" style="background: rgba(147, 51, 234, 0.18); border: 1px solid rgba(168, 85, 247, 0.3); color: #c084fc;">📝</div>
            <div class="kpi-text-box">
                <div class="kpi-label-line">
                    <span class="kpi-label-text">Avg. Test Score</span>
                    <span style="color:#c084fc; font-size:10px;">▣</span>
                </div>
                <div class="kpi-val-text">{avg_score:.1f}%</div>
                <div class="kpi-sub-text">Converted Average</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k_c5:
    st.markdown(
        f"""
        <div class="kpi-row-card">
            <div class="kpi-sq-icon" style="background: rgba(217, 119, 6, 0.18); border: 1px solid rgba(245, 158, 11, 0.3); color: #fbbf24;">🏛️</div>
            <div class="kpi-text-box">
                <div class="kpi-label-line">
                    <span class="kpi-label-text">Infrastructure Score</span>
                    <span style="color:#fbbf24; font-size:10px;">▣</span>
                </div>
                <div class="kpi-val-text">{avg_infra:.2f}<span style="font-size:12px;color:{text_muted};">/5</span></div>
                <div class="kpi-sub-text">Facility Index</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k_c6:
    st.markdown(
        f"""
        <div class="kpi-row-card">
            <div class="kpi-sq-icon" style="background: rgba(225, 29, 72, 0.18); border: 1px solid rgba(244, 63, 94, 0.3); color: #f43f5e;">🛡️</div>
            <div class="kpi-text-box">
                <div class="kpi-label-line">
                    <span class="kpi-label-text">Retention Risk</span>
                    <span style="color:#f43f5e; font-size:10px;">✕</span>
                </div>
                <div class="kpi-val-text">{avg_risk:.1f}</div>
                <div class="kpi-sub-text">Moderate Risk</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    f"""
    <div style="font-size: 10.5px; color: {text_muted}; font-style: italic; margin-top: 6px; margin-bottom: 12px;">
        * Retention Risk Indicator is a composite analytical measure — not a measured student dropout probability.
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 10. ROW 3: HORIZONTAL TAB NAVIGATION BAR
# ============================================================

tabs_list = [
    "🏠 Home",
    "📊 Analytics",
    "🏫 Schools",
    "👥 Students",
    "📅 Attendance",
    "📝 Test Scores",
    "🍱 Mid-Day Meal",
    "🏢 Infrastructure",
    "⚠️ Risk Analysis",
    "🔮 Policy Simulator",
    "🛡️ Data Rescue & Audit"
]

tab_cols = st.columns(len(tabs_list))
for idx, tab_name in enumerate(tabs_list):
    with tab_cols[idx]:
        is_active = (st.session_state["nav_page"] == tab_name) and (not st.session_state["show_ai_agent"])
        btn_class = "st-htab-active" if is_active else "st-htab"
        st.markdown(f'<div class="{btn_class}">', unsafe_allow_html=True)
        if st.button(tab_name, key=f"htab_btn_{idx}", use_container_width=True):
            st.session_state["nav_page"] = tab_name
            st.session_state["show_ai_agent"] = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 11. ROW 4 & 5: HOME DASHBOARD (EXACT VISUAL MATCH)
# ============================================================

if not st.session_state["show_ai_agent"] and st.session_state["nav_page"] == "🏠 Home":

    # ── MIDDLE ROW: REAL DATA CHARTS + QUICK ACTIONS ──
    m_col1, m_col2, m_col3, m_col4 = st.columns([1.5, 1.15, 0.95, 0.9])

    # Card 1: Attendance Trend — calculated from cleaned attendance records
    with m_col1:
        st.markdown(
            f"""
            <div class="exact-panel">
                <div class="exact-panel-head">
                    <div>
                        <div class="exact-panel-title">📈 Attendance Trend</div>
                        <div class="exact-panel-sub">Monthly average attendance from cleaned attendance records</div>
                    </div>
                </div>
            """,
            unsafe_allow_html=True
        )

        scope_ids = set(filtered_df["school_id"])
        trend_df = df_att[df_att["school_id"].isin(scope_ids)].dropna(
            subset=["date", "attendance_rate"]
        ).copy()
        if len(trend_df):
            trend_df["month"] = trend_df["date"].dt.to_period("M").dt.to_timestamp()
            trend_df = (
                trend_df.groupby("month", as_index=False)["attendance_rate"]
                .mean()
                .sort_values("month")
                .tail(6)
            )
            fig_trend = px.line(
                trend_df,
                x="month",
                y="attendance_rate",
                markers=True,
                labels={"month": "", "attendance_rate": "Attendance Rate (%)"}
            )
            fig_trend.update_traces(line=dict(color="#38bdf8", width=3), marker=dict(size=7))
            fig_trend.update_layout(
                make_layout(
                    height=250,
                    yaxis=dict(range=[0, 100], tickvals=[0, 20, 40, 60, 80, 100],
                               ticktext=["0%", "20%", "40%", "60%", "80%", "100%"]),
                    showlegend=False,
                    hovermode="x unified"
                )
            )
            fig_trend.update_xaxes(tickformat="%b %Y")
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No valid attendance dates available for the trend.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Card 2: Academic Performance — real converted scores
    with m_col2:
        st.markdown(
            """
            <div class="exact-panel">
                <div class="exact-panel-head">
                    <div>
                        <div class="exact-panel-title">📚 Academic Performance</div>
                        <div class="exact-panel-sub">Average converted test score by subject</div>
                    </div>
                </div>
            """,
            unsafe_allow_html=True
        )

        scope_ids = set(filtered_df["school_id"])
        acad_df = (
            df_tests[df_tests["school_id"].isin(scope_ids)]
            .dropna(subset=["subject", "score_percentage"])
            .groupby("subject", as_index=False)["score_percentage"]
            .mean()
            .sort_values("score_percentage", ascending=False)
        )
        if len(acad_df):
            fig_acad = px.bar(
                acad_df,
                x="subject",
                y="score_percentage",
                text_auto=".1f",
                labels={"subject": "", "score_percentage": "Average Score (%)"}
            )
            fig_acad.update_traces(marker_color="#38bdf8")
            fig_acad.update_layout(
                make_layout(
                    height=250,
                    yaxis=dict(range=[0, 100], tickvals=[0, 25, 50, 75, 100]),
                    showlegend=False
                )
            )
            st.plotly_chart(fig_acad, use_container_width=True)
        else:
            st.info("No converted test scores available.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Card 3: Risk Distribution — calculated from the actual risk index
    with m_col3:
        st.markdown(
            """
            <div class="exact-panel">
                <div class="exact-panel-head">
                    <div>
                        <div class="exact-panel-title">🛡️ Risk Distribution</div>
                        <div class="exact-panel-sub">Schools by analytical risk band</div>
                    </div>
                </div>
            """,
            unsafe_allow_html=True
        )

        risk_vals = filtered_df["retention_risk_indicator"].dropna()
        risk_counts = pd.Series({
            "Low": int((risk_vals <= 20).sum()),
            "Moderate": int(((risk_vals > 20) & (risk_vals <= 25)).sum()),
            "High": int(((risk_vals > 25) & (risk_vals <= 30)).sum()),
            "Critical": int((risk_vals > 30).sum())
        })
        risk_counts = risk_counts[risk_counts > 0]

        if len(risk_counts):
            fig_donut = px.pie(
                names=risk_counts.index,
                values=risk_counts.values,
                hole=0.68,
                color=risk_counts.index,
                color_discrete_map={
                    "Low": "#10b981",
                    "Moderate": "#fbbf24",
                    "High": "#fb7185",
                    "Critical": "#f43f5e"
                }
            )
            fig_donut.update_traces(textinfo="none", hoverinfo="label+value+percent")
            fig_donut.update_layout(
                make_layout(
                    height=250,
                    annotations=[dict(
                        text=f"<b style='font-size:20px;color:{text_primary};'>{len(filtered_df)}</b>"
                             f"<br><span style='font-size:9.5px;color:{text_muted};'>Total Schools</span>",
                        x=0.5, y=0.5, font_size=11, showarrow=False
                    )],
                    showlegend=True,
                    legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="right", x=1.1)
                )
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("No risk values available.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Card 4: Quick Actions
    with m_col4:
        st.markdown(
            """
            <div class="exact-panel">
                <div class="exact-panel-head">
                    <div class="exact-panel-title">⚡ Quick Actions</div>
                </div>
                <div class="qa-wrap-stack">
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div class="qa-btn-1">', unsafe_allow_html=True)
        if st.button("✨  Ask EduPulse AI                →", key="btn_act_1", use_container_width=True):
            st.session_state["show_ai_agent"] = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="qa-btn-2">', unsafe_allow_html=True)
        if st.button("🏫  Explore Schools                →", key="btn_act_2", use_container_width=True):
            st.session_state["nav_page"] = "🏫 Schools"
            st.session_state["show_ai_agent"] = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="qa-btn-3">', unsafe_allow_html=True)
        if st.button("⚠️  View Risk Analysis           →", key="btn_act_3", use_container_width=True):
            st.session_state["nav_page"] = "⚠️ Risk Analysis"
            st.session_state["show_ai_agent"] = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="qa-btn-4">', unsafe_allow_html=True)
        if st.button("📅  View Attendance              →", key="btn_act_4", use_container_width=True):
            st.session_state["nav_page"] = "📅 Attendance"
            st.session_state["show_ai_agent"] = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="qa-btn-5">', unsafe_allow_html=True)
        if st.button("🏛️  Infrastructure Analysis →", key="btn_act_5", use_container_width=True):
            st.session_state["nav_page"] = "🏢 Infrastructure"
            st.session_state["show_ai_agent"] = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="qa-btn-6">', unsafe_allow_html=True)
        if st.button("🛡️  Data Quality Audit           →", key="btn_act_6", use_container_width=True):
            st.session_state["nav_page"] = "🛡️ Data Rescue & Audit"
            st.session_state["show_ai_agent"] = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="qa-btn-7">', unsafe_allow_html=True)
        if st.button("📥  Export Data                       →", key="btn_act_7", use_container_width=True):
            st.session_state["nav_page"] = "📑 Reports & Export"
            st.session_state["show_ai_agent"] = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)

    # ── BOTTOM ROW: REAL DISTRICT COMPARISON & DYNAMIC ALERTS ──
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    b_col1, b_col2 = st.columns([1.32, 1.0])

    with b_col1:
        st.markdown(
            """
            <div class="exact-panel">
                <div class="exact-panel-head">
                    <div>
                        <div class="exact-panel-title">📍 District-wise Comparison</div>
                        <div class="exact-panel-sub">Average test scores across districts in current scope</div>
                    </div>
                </div>
            """,
            unsafe_allow_html=True
        )

        dist_summary = (
            filtered_df.groupby("district", dropna=False)
            .agg(avg_score=("average_test_score", "mean"))
            .reset_index()
            .dropna(subset=["avg_score"])
            .sort_values("avg_score", ascending=False)
        )
        if len(dist_summary):
            dist_plot = dist_summary.head(10).sort_values("avg_score", ascending=True)
            fig_dist = px.bar(
                dist_plot,
                x="avg_score",
                y="district",
                orientation="h",
                text_auto=".1f",
                labels={"avg_score": "Average Test Score (%)", "district": ""}
            )
            fig_dist.update_traces(marker_color="#38bdf8")
            fig_dist.update_layout(make_layout(height=220, xaxis=dict(range=[0, 100]), showlegend=False))
            st.plotly_chart(fig_dist, use_container_width=True)
        else:
            st.info("No district-level test-score data available.")
        st.markdown("</div>", unsafe_allow_html=True)

    with b_col2:
        st.markdown(
            f"""
            <div class="exact-panel">
                <div class="exact-panel-head">
                    <div class="exact-panel-title">🔔 Current Alerts</div>
                </div>
            """,
            unsafe_allow_html=True
        )

        alert_items = [
            ("🔴", "Critical-risk schools", int((filtered_df["retention_risk_indicator"] > 30).sum())),
            ("🟠", "Low attendance alert", int((filtered_df["average_attendance_rate"] < 75).sum())),
            ("🟡", "Infrastructure alert", int((filtered_df["average_facility_count"] < 2).sum())),
            ("🔵", "High proxy-attendance alert", int((filtered_df["proxy_attendance_rate"] > 5).sum()))
        ]

        for icon, label, count in alert_items:
            st.markdown(
                f"""
                <div class="recent-alert-row">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="font-size:12px;">{icon}</span>
                        <span style="font-size:12px; color:{text_primary}; font-weight:600;">{label}</span>
                    </div>
                    <div style="font-size:11px; color:{text_secondary};">{count:,} schools</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# 12. AI AGENT WORKSPACE — DETERMINISTIC, REPRODUCIBLE QUERY ENGINE
# ============================================================

def detect_intent(query_text):
    q = str(query_text).lower().strip()

    # Specific patterns first so "electricity vs score" is comparison, not infra ranking.
    if any(w in q for w in ["compare", "vs", "versus", "difference", "with and without"]):
        return "COMPARISON"
    if any(w in q for w in ["trend", "over time", "monthly", "daily", "timeline"]):
        return "TREND"
    if any(w in q for w in ["correlation", "correlated", "relationship", "associated", "association"]):
        return "CORRELATION"
    if any(w in q for w in ["anomaly", "anomalies", "flag", "proxy attendance"]):
        return "ANOMALY"
    if any(w in q for w in ["mdm", "meal", "procurement", "payment", "paid", "pending", "due", "grain"]):
        return "MDM"
    if any(w in q for w in ["subject", "subjects", "marks", "test score", "test scores", "grade"]):
        return "BREAKDOWN"
    if any(w in q for w in ["infrastructure", "facility", "facilities", "toilet", "water", "electricity", "playground", "boundary wall"]):
        return "INFRA_RANKING"
    return "RANKING"


def render_ai_result(query_text, intent, data):
    q = str(query_text).lower()

    if intent == "COMPARISON":
        # Track 4 bonus: average test score with vs without functional electricity.
        if "electric" in q:
            yes = data[data["electricity_available"] >= 100]["average_test_score"].mean()
            no = data[data["electricity_available"] < 100]["average_test_score"].mean()
            n_yes = int((data["electricity_available"] >= 100).sum())
            n_no = int((data["electricity_available"] < 100).sum())

            cmp_df = pd.DataFrame({
                "Group": ["With functional electricity", "Without functional electricity"],
                "Average Test Score (%)": [yes, no],
                "Schools": [n_yes, n_no]
            })
            fig = px.bar(
                cmp_df,
                x="Group",
                y="Average Test Score (%)",
                text="Average Test Score (%)",
                labels={"Group": "", "Average Test Score (%)": "Average Test Score (%)"}
            )
            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside", marker_color="#38bdf8")
            fig.update_layout(make_layout(height=320, yaxis=dict(range=[0, 100]), showlegend=False))
            st.plotly_chart(fig, use_container_width=True)

            diff = yes - no if pd.notna(yes) and pd.notna(no) else np.nan
            if pd.notna(diff):
                st.info(
                    f"Association in the current scope: schools with functional electricity have "
                    f"{yes:.2f}% average test scores versus {no:.2f}% without electricity "
                    f"(difference {diff:+.2f} percentage points). This is observational and does not establish causation."
                )
            return

        # Generic comparison fallback: district attendance vs score.
        comp = data.groupby("district", dropna=False).agg(
            Attendance=("average_attendance_rate", "mean"),
            Score=("average_test_score", "mean")
        ).reset_index()
        comp = comp.dropna(subset=["Attendance", "Score"])
        if len(comp):
            long_comp = comp.melt(id_vars="district", value_vars=["Attendance", "Score"],
                                  var_name="Metric", value_name="Value")
            fig = px.bar(long_comp, x="district", y="Value", color="Metric", barmode="group")
            fig.update_layout(make_layout(height=320, yaxis=dict(range=[0, 100])))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data for the requested comparison.")

    elif intent == "TREND":
        trend = df_att[df_att["school_id"].isin(set(data["school_id"]))].dropna(
            subset=["date", "attendance_rate"]
        ).copy()
        if len(trend):
            trend["month"] = trend["date"].dt.to_period("M").dt.to_timestamp()
            trend = trend.groupby("month", as_index=False)["attendance_rate"].mean().sort_values("month")
            fig = px.line(trend, x="month", y="attendance_rate", markers=True,
                          labels={"month": "", "attendance_rate": "Average Attendance (%)"})
            fig.update_traces(line=dict(color="#38bdf8", width=3), marker=dict(size=7))
            fig.update_layout(make_layout(height=340, yaxis=dict(range=[0, 100]), showlegend=False))
            fig.update_xaxes(tickformat="%b %Y")
            st.plotly_chart(fig, use_container_width=True)
            st.success("Trend shown as a line chart because the query asks how attendance changes over time.")
        else:
            st.info("No valid attendance dates are available.")

    elif intent == "CORRELATION":
        corr = data[["average_attendance_rate", "average_test_score"]].dropna()
        if len(corr) >= 3:
            r = corr["average_attendance_rate"].corr(corr["average_test_score"])
            fig = px.scatter(
                corr,
                x="average_attendance_rate",
                y="average_test_score",
                trendline="ols",
                labels={
                    "average_attendance_rate": "Average Attendance Rate (%)",
                    "average_test_score": "Average Test Score (%)"
                }
            )
            fig.update_layout(make_layout(height=340))
            st.plotly_chart(fig, use_container_width=True)
            st.info(
                f"Pearson correlation in the current school scope: r = {r:.3f}. "
                "This measures linear association, not causation."
            )
        else:
            st.info("At least three schools with both attendance and score values are needed.")

    elif intent == "ANOMALY":
        anomaly = data[data["proxy_attendance_rate"] > 5].copy()
        anomaly = anomaly.sort_values("proxy_attendance_rate", ascending=False)
        if len(anomaly):
            st.dataframe(
                anomaly[[
                    "school_id", "school_name", "district",
                    "proxy_attendance_rate", "average_attendance_rate",
                    "proxy_attendance_records"
                ]].head(30),
                use_container_width=True,
                hide_index=True
            )
            st.warning(f"{len(anomaly):,} schools exceed the configured proxy-attendance alert threshold of 5%.")
        else:
            st.success("No schools exceed the configured proxy-attendance alert threshold of 5%.")

    elif intent == "MDM":
        mdm_status = pd.DataFrame({
            "Payment Status": ["Paid", "Pending", "Due"],
            "Records": [
                int(data["paid_records"].sum()),
                int(data["pending_records"].sum()),
                int(data["due_records"].sum())
            ]
        })
        fig = px.bar(mdm_status, x="Payment Status", y="Records", text_auto=True,
                     labels={"Payment Status": "", "Records": "Procurement Records"})
        fig.update_traces(marker_color="#fbbf24")
        fig.update_layout(make_layout(height=320, showlegend=False))
        st.plotly_chart(fig, use_container_width=True)
        st.info(
            f"Recorded grain quantity in current scope: {data['total_grain_quantity_kg'].sum():,.2f} kg. "
            f"Recorded MDM cost: ₹{data['total_mdm_cost'].sum():,.0f}. "
            "Missing quantity/unit fields are retained and flagged rather than imputed."
        )

    elif intent == "BREAKDOWN":
        score_data = df_tests.dropna(subset=["subject", "score_percentage"]).copy()
        school_ids = set(data["school_id"])
        score_data = score_data[score_data["school_id"].isin(school_ids)]
        subj = score_data.groupby("subject", as_index=False)["score_percentage"].mean().sort_values(
            "score_percentage", ascending=False
        )
        if len(subj):
            fig = px.bar(subj, x="subject", y="score_percentage", text_auto=".1f",
                         labels={"subject": "", "score_percentage": "Average Score (%)"})
            fig.update_traces(marker_color="#a855f7")
            fig.update_layout(make_layout(height=330, yaxis=dict(range=[0, 100]), showlegend=False))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No converted test-score records are available.")

    elif intent == "INFRA_RANKING":
        infra_map = {
            "electricity": ("electricity_available", "Electricity"),
            "water": ("drinking_water_available", "Drinking Water"),
            "toilet": ("functional_toilet_available", "Functional Toilet"),
            "playground": ("playground_available", "Playground"),
            "boundary": ("boundary_wall_available", "Boundary Wall")
        }
        selected = None
        for key, value in infra_map.items():
            if key in q:
                selected = value
                break

        if selected:
            col, label = selected
            known = data[col].dropna()
            coverage = known.mean() if len(known) else np.nan
            st.metric(f"{label} coverage among known school records", f"{coverage:.1f}%" if pd.notna(coverage) else "N/A")
        else:
            infra = pd.DataFrame({
                "Facility": ["Electricity", "Drinking Water", "Functional Toilet", "Boundary Wall", "Playground"],
                "Coverage (%)": [
                    data["electricity_available"].mean(),
                    data["drinking_water_available"].mean(),
                    data["functional_toilet_available"].mean(),
                    data["boundary_wall_available"].mean(),
                    data["playground_available"].mean()
                ]
            }).sort_values("Coverage (%)")
            fig = px.bar(infra, x="Coverage (%)", y="Facility", orientation="h", text_auto=".1f",
                         labels={"Coverage (%)": "Coverage (%)", "Facility": ""})
            fig.update_traces(marker_color="#38bdf8")
            fig.update_layout(make_layout(height=340, xaxis=dict(range=[0, 100]), showlegend=False))
            st.plotly_chart(fig, use_container_width=True)

    else:  # RANKING
        ranking = data.groupby("district", dropna=False)["retention_risk_indicator"].mean().reset_index()
        ranking = ranking.dropna(subset=["retention_risk_indicator"]).sort_values(
            "retention_risk_indicator", ascending=False
        )
        if len(ranking):
            fig = px.bar(
                ranking,
                x="retention_risk_indicator",
                y="district",
                orientation="h",
                text_auto=".2f",
                labels={"retention_risk_indicator": "Average Retention Risk Indicator", "district": ""}
            )
            fig.update_traces(marker_color="#f43f5e")
            fig.update_layout(make_layout(height=340, showlegend=False))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No district risk data is available.")


@st.dialog("✦ Ask EduPulse AI", width="large")
def show_ai_modal():
    """Centered AI workspace shown over the current dashboard."""
    st.markdown(
        """
        <div style="text-align:center; margin-top:-8px; margin-bottom:16px;">
            <div style="
                font-size:12px;
                color:#94a3b8;
                line-height:1.6;
                max-width:560px;
                margin:0 auto;
            ">
                Ask questions about your education data, get insights,
                see visualizations, and explore data-driven decisions.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # If a prompt chip was clicked last run, pre-fill via value= (not key=) and
    # store the result in a plain session-state key so we can read it later.
    _pending = st.session_state.pop("ai_modal_text_pending", None)
    _default = _pending if _pending is not None else st.session_state.get("ai_modal_text", "")
    ai_q = st.text_area(
        "Ask anything",
        value=_default,
        placeholder=(
            "Ask anything... e.g. Show attendance trend, "
            "compare electricity and test scores, rank districts by risk..."
        ),
        height=105,
        label_visibility="collapsed",
        key="ai_modal_text"
    )

    send_col, close_col = st.columns([4, 1])

    with send_col:
        st.markdown('<div class="ai-modal-send">', unsafe_allow_html=True)
        send_clicked = st.button(
            "✦  Analyze with EduPulse AI",
            key="ai_modal_send",
            use_container_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with close_col:
        close_clicked = st.button(
            "✕ Close",
            key="ai_modal_close",
            use_container_width=True
        )

    if close_clicked:
        st.session_state["show_ai_agent"] = False
        st.rerun()

    st.markdown(
        """
        <div style="
            font-size:12px;
            font-weight:700;
            color:#cbd5e1;
            margin:16px 0 8px;
        ">
            Try these examples
        </div>
        """,
        unsafe_allow_html=True
    )

    sample_prompts = [
        "Show attendance trend over time",
        "Show MDM payment status",
        "Compare electricity and test scores",
        "Show test scores by subject",
        "Is attendance associated with academic performance?",
        "Show infrastructure availability",
        "Show schools with proxy attendance above 5%",
        "Rank districts by retention risk",
    ]

    p_cols = st.columns(2)
    for idx, prompt_text in enumerate(sample_prompts):
        with p_cols[idx % 2]:
            if st.button(
                prompt_text,
                key=f"ai_modal_prompt_{idx}",
                use_container_width=True
            ):
                st.session_state["ai_modal_text_pending"] = prompt_text
                st.rerun()

    query = st.session_state.get("ai_modal_text", "").strip()

    if send_clicked and query:
        st.session_state["ai_input_text"] = query

    if query:
        intent = detect_intent(query)

        st.markdown(
            f"""
            <div style="
                margin-top:16px;
                padding:10px 13px;
                border-radius:10px;
                border:1px solid rgba(168,85,247,.25);
                background:rgba(168,85,247,.07);
                font-size:12px;
                color:#cbd5e1;
            ">
                🎯 <b style="color:#f8fafc;">Resolved Intent:</b> {intent}
                &nbsp; • &nbsp;
                ⚡ <b style="color:#f8fafc;">Scope:</b> {len(filtered_df):,} schools
            </div>
            """,
            unsafe_allow_html=True
        )

        render_ai_result(query, intent, filtered_df)

    st.markdown(
        """
        <div style="
            text-align:center;
            margin-top:18px;
            padding-top:10px;
            border-top:1px solid rgba(148,163,184,.12);
            font-size:10px;
            color:#64748b;
        ">
            ✦ Powered by EduPulse AI &nbsp;|&nbsp; Data • Insights • Better Education
        </div>
        """,
        unsafe_allow_html=True
    )


# Open the modal when the header or Quick Action button is clicked.
if st.session_state["show_ai_agent"]:
    show_ai_modal()

# ============================================================
# 13. OTHER VIEWS (ANALYTICS, SCHOOLS, ETC.)
# ============================================================

if True:
    
    # ── ANALYTICS VIEW ──
    if st.session_state["nav_page"] == "📊 Analytics":
        st.markdown(f"<div style='font-size:20px; font-weight:800; color:{text_primary}; margin-top:14px;'>📊 Executive Command Center</div>", unsafe_allow_html=True)
        col_an1, col_an2 = st.columns([1.2, 1])
        with col_an1:
            dist_summary = filtered_df.groupby("district").agg(avg_att=("average_attendance_rate", "mean"), avg_risk=("retention_risk_indicator", "mean"), tot_students=("total_enrolled_students", "sum")).reset_index()
            fig_sc = px.scatter(dist_summary, x="avg_att", y="avg_risk", size="tot_students", color="avg_risk", text="district", color_continuous_scale=["#34d399", "#fbbf24", "#f43f5e"])
            fig_sc.update_traces(textposition="top center")
            fig_sc.update_layout(make_layout(height=340, coloraxis_showscale=False))
            st.plotly_chart(fig_sc, use_container_width=True)
        with col_an2:
            fig_b = px.histogram(filtered_df, x="retention_risk_indicator", nbins=15, title="Risk Distribution", color_discrete_sequence=["#6366f1"])
            fig_b.update_layout(make_layout(height=340))
            st.plotly_chart(fig_b, use_container_width=True)

    # ── SCHOOLS & STUDENTS VIEW (SCHOOL 360) ──
    elif st.session_state["nav_page"] in ["🏫 Schools", "👥 Students"]:
        st.markdown(f"<div style='font-size:20px; font-weight:800; color:{text_primary}; margin-top:14px;'>🏫 School 360° Diagnostic Scorecard</div>", unsafe_allow_html=True)
        s_list = sorted(filtered_df["school_name"].unique())
        sel_idx = st.session_state.get("selected_school_idx", 0)
        if sel_idx >= len(s_list): sel_idx = 0
        s_sel = st.selectbox("Select School", s_list, index=sel_idx)
        s_row = filtered_df[filtered_df["school_name"] == s_sel].iloc[0]
        
        sc_c1, sc_c2, sc_c3, sc_c4, sc_c5 = st.columns(5)
        sc_c1.metric("Attendance Risk", f"{s_row['attendance_risk']:.1f}")
        sc_c2.metric("Proxy Risk", f"{s_row['proxy_risk']:.1f}")
        sc_c3.metric("Academic Risk", f"{s_row['score_risk']:.1f}")
        sc_c4.metric("Infra Risk", f"{s_row['infrastructure_risk']:.1f}")
        sc_c5.metric("Total Risk Index", f"{s_row['retention_risk_indicator']:.2f}")

        st.markdown(
            f"""
            <div class="exact-panel" style="margin-top: 14px;">
                <div style="font-size: 14px; font-weight: 700; color: #38bdf8;">📋 School Profile & Diagnostic Details</div>
                <div style="font-size: 12.5px; color: {text_secondary}; margin-top: 6px; line-height: 1.6;">
                    <strong>School:</strong> {s_row['school_name']} (ID: {s_row['school_id']})<br/>
                    <strong>District:</strong> {s_row['district']} &nbsp;•&nbsp; <strong>Block:</strong> {s_row['block']}<br/>
                    <strong>Enrolled Students:</strong> {s_row['total_enrolled_students']:,}<br/>
                    <strong>Average Attendance Rate:</strong> {s_row['average_attendance_rate']:.1f}%<br/>
                    <strong>Average Converted Test Score:</strong> {s_row['average_test_score']:.1f}%<br/>
                    <strong>Facility Score:</strong> {s_row['average_facility_count']:.1f}/5.0 core facilities
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ── ATTENDANCE VIEW ──
    elif st.session_state["nav_page"] == "📅 Attendance":
        st.markdown(f"<div style='font-size:20px; font-weight:800; color:{text_primary}; margin-top:14px;'>📅 Attendance Analytics & Proxy Audit</div>", unsafe_allow_html=True)
        att_agg = filtered_df.sort_values("proxy_attendance_rate", ascending=False).head(20)[["school_id", "school_name", "district", "proxy_attendance_rate", "average_attendance_rate"]]
        st.dataframe(att_agg, use_container_width=True, hide_index=True)

    # ── TEST SCORES VIEW ──
    elif st.session_state["nav_page"] == "📝 Test Scores":
        st.markdown(f"<div style='font-size:20px; font-weight:800; color:{text_primary}; margin-top:14px;'>📝 Academic Performance Analytics</div>", unsafe_allow_html=True)
        filtered_school_ids = set(filtered_df["school_id"])
        test_sub = df_tests[df_tests["school_id"].isin(filtered_school_ids)]
        subj_agg = test_sub.groupby("subject")["score_percentage"].mean().reset_index().sort_values("score_percentage", ascending=False)
        fig_subj = px.bar(subj_agg, x="subject", y="score_percentage", text_auto=".1f", color="score_percentage", color_continuous_scale="Purples")
        fig_subj.update_layout(make_layout(height=320, coloraxis_showscale=False))
        st.plotly_chart(fig_subj, use_container_width=True)

    # ── MID-DAY MEAL VIEW ──
    elif st.session_state["nav_page"] == "🍱 Mid-Day Meal":
        st.markdown(f"<div style='font-size:20px; font-weight:800; color:{text_primary}; margin-top:14px;'>🍱 Mid-Day Meal Operations</div>", unsafe_allow_html=True)
        mdm_sum = pd.DataFrame({
            "Status": ["Paid", "Pending", "Due"],
            "Count": [
                int(filtered_df["paid_records"].sum()),
                int(filtered_df["pending_records"].sum()),
                int(filtered_df["due_records"].sum())
            ]
        })
        fig_m = px.pie(mdm_sum, names="Status", values="Count", hole=0.5, color_discrete_sequence=["#10b981", "#fbbf24", "#ef4444"])
        fig_m.update_layout(make_layout(height=300))
        st.plotly_chart(fig_m, use_container_width=True)

    # ── INFRASTRUCTURE VIEW ──
    elif st.session_state["nav_page"] == "🏢 Infrastructure":
        st.markdown(f"<div style='font-size:20px; font-weight:800; color:{text_primary}; margin-top:14px;'>🏢 Infrastructure Readiness</div>", unsafe_allow_html=True)
        infra_cov = {
            "⚡ Electricity": filtered_df["electricity_available"].mean(),
            "💧 Drinking Water": filtered_df["drinking_water_available"].mean(),
            "🚽 Functional Toilet": filtered_df["functional_toilet_available"].mean(),
            "🧱 Boundary Wall": filtered_df["boundary_wall_available"].mean(),
            "⚽ Playground": filtered_df["playground_available"].mean()
        }
        fig_ic = px.bar(pd.DataFrame(list(infra_cov.items()), columns=["Facility", "Coverage_%"]), x="Coverage_%", y="Facility", orientation="h", text_auto=".1f", color="Coverage_%", color_continuous_scale=["#ef4444", "#f59e0b", "#10b981"])
        fig_ic.update_layout(make_layout(height=300, coloraxis_showscale=False))
        st.plotly_chart(fig_ic, use_container_width=True)

    # ── RISK ANALYSIS VIEW ──
    elif st.session_state["nav_page"] == "⚠️ Risk Analysis":
        st.markdown(f"<div style='font-size:20px; font-weight:800; color:{text_primary}; margin-top:14px;'>⚠️ Priority Schools Intervention Matrix</div>", unsafe_allow_html=True)
        st.dataframe(filtered_df.sort_values("retention_risk_indicator", ascending=False)[["school_id", "school_name", "district", "average_attendance_rate", "average_test_score", "average_facility_count", "retention_risk_indicator"]].head(30), use_container_width=True, hide_index=True)

    # ── POLICY SIMULATOR VIEW ──
    elif st.session_state["nav_page"] == "🔮 Policy Simulator":
        st.markdown(f"<div style='font-size:20px; font-weight:800; color:{text_primary}; margin-top:14px;'>🔮 Policy Impact Simulator</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size:11px; color:{text_muted}; margin-bottom:12px;'>"
            "Scenario planning only — projected values are hypothetical sensitivity scenarios, not causal forecasts."
            "</div>",
            unsafe_allow_html=True
        )

        p_c1, p_c2, p_c3, p_c4 = st.columns(4)
        with p_c1:
            att_b = st.slider("Attendance Boost (+pp)", 0.0, 15.0, step=0.5, key="sim_att_val")
        with p_c2:
            sc_b = st.slider("Academic Score Boost (+pp)", 0.0, 15.0, step=0.5, key="sim_score_val")
        with p_c3:
            infra_b = st.slider("Facility Improvement (+)", 0.0, 2.0, step=0.1, key="sim_infra_val")
        with p_c4:
            proxy_b = st.slider("Proxy Attendance Reduction (-pp)", 0.0, 10.0, step=0.5, key="sim_proxy_val")

        base_r = filtered_df["retention_risk_indicator"].mean()

        baseline_components = {
            "Attendance": filtered_df["attendance_risk"].mean(),
            "Proxy": filtered_df["proxy_risk"].mean(),
            "Academic": filtered_df["score_risk"].mean(),
            "Infrastructure": filtered_df["infrastructure_risk"].mean()
        }

        projected_att_risk = max(0.0, baseline_components["Attendance"] - att_b)
        projected_proxy_risk = max(0.0, baseline_components["Proxy"] - proxy_b)
        projected_score_risk = max(0.0, baseline_components["Academic"] - sc_b)
        projected_infra_risk = max(0.0, baseline_components["Infrastructure"] - (infra_b / 5.0 * 100.0))
        projected_components = [
            projected_att_risk, projected_proxy_risk,
            projected_score_risk, projected_infra_risk
        ]
        proj_r = float(np.nanmean(projected_components))

        r1, r2, r3 = st.columns(3)
        r1.metric("Baseline Risk", f"{base_r:.2f}")
        r2.metric("Scenario Risk", f"{proj_r:.2f}", delta=f"{proj_r - base_r:+.2f}")
        r3.metric("Scenario Risk-Index Reduction", f"{max(0.0, base_r - proj_r):.2f}")

        scenario_df = pd.DataFrame({
            "Component": ["Attendance", "Proxy", "Academic", "Infrastructure"],
            "Baseline": [
                baseline_components["Attendance"],
                baseline_components["Proxy"],
                baseline_components["Academic"],
                baseline_components["Infrastructure"]
            ],
            "Scenario": projected_components
        }).melt(id_vars="Component", var_name="Scenario", value_name="Risk")
        fig_sim = px.bar(scenario_df, x="Component", y="Risk", color="Scenario", barmode="group", text_auto=".1f")
        fig_sim.update_layout(make_layout(height=330, yaxis=dict(range=[0, 100])))
        st.plotly_chart(fig_sim, use_container_width=True)

    # ── DATA RESCUE & AUDIT VIEW ──
    elif st.session_state["nav_page"] == "🛡️ Data Rescue & Audit":
        st.markdown(
            f"<div style='font-size:20px; font-weight:800; color:{text_primary}; margin-top:14px;'>"
            "🛡️ Data Rescue Engine & Quality Audit</div>",
            unsafe_allow_html=True
        )

        audit_rows = pd.DataFrame({
            "Dataset": ["School Master", "Attendance", "Test Scores", "MDM Procurement", "Infrastructure"],
            "Raw Rows": [618, 20800, 8000, 12360, 3150],
            "Cleaned Rows": [600, 20000, 8000, 12000, 3000],
            "Exact Duplicates Removed": [18, 800, 0, 360, 150]
        })
        st.dataframe(audit_rows, use_container_width=True, hide_index=True)

        st.markdown(
            f"""
            <div class="exact-panel" style="margin-top:12px;">
                <div style="font-size:14px; font-weight:700; color:{text_primary}; margin-bottom:8px;">
                    Relational Integrity
                </div>
                <div style="font-size:12px; color:{text_secondary}; line-height:1.65;">
                    ✔ <strong>School Master:</strong> 600 unique schools<br/>
                    ✔ <strong>Attendance:</strong> 20,000 rows; 600 unique School IDs; 0 unmapped IDs<br/>
                    ✔ <strong>Test Scores:</strong> 8,000 rows; 600 unique School IDs; 0 unmapped IDs<br/>
                    ✔ <strong>MDM Procurement:</strong> 12,000 rows; 600 unique School IDs; 0 unmapped IDs<br/>
                    ✔ <strong>Infrastructure:</strong> 3,000 rows; 598 unique School IDs; 0 unmapped IDs<br/>
                    ℹ <strong>Infrastructure coverage:</strong> 598 of 600 schools have infrastructure records.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="exact-panel" style="margin-top:12px;">
                <div style="font-size:14px; font-weight:700; color:{text_primary}; margin-bottom:8px;">
                    Key Cleaning Decisions
                </div>
                <div style="font-size:12px; color:{text_secondary}; line-height:1.65;">
                    • Standardized School IDs, dates, text labels and boolean facility values.<br/>
                    • Removed exact duplicate rows only; source records were otherwise retained for auditability.<br/>
                    • Standardized MDM grain names and converted KG, grams and verified 50-kg bag units to kilograms.<br/>
                    • Standardized test-score scales; Raw Marks and CGPA were converted to percentage where mathematically supported.<br/>
                    • Letter Grade records remain without percentage conversion because the source does not provide a defensible grade-to-percentage mapping.<br/>
                    • Missing MDM quantity/unit values were retained and explicitly flagged; no unsupported values were imputed.<br/>
                    • Attendance records where present students exceeded total students were flagged as invalid and retained.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="exact-panel" style="margin-top:12px;">
                <div style="font-size:14px; font-weight:700; color:{text_primary}; margin-bottom:8px;">
                    Analytical Limitations
                </div>
                <div style="font-size:12px; color:{text_secondary}; line-height:1.65;">
                    • Retention Risk Indicator is a composite analytical measure, not a measured dropout probability.<br/>
                    • Electricity/test-score comparison is observational and does not establish causation.<br/>
                    • Infrastructure summaries use the available inspection records; 2 schools have no infrastructure record.<br/>
                    • The attendance reference-window flag is a working validation rule, not an authoritative academic calendar.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ── REPORTS & EXPORT DATA VIEW ──
    elif st.session_state["nav_page"] in ["📑 Reports & Export", "📥 Export Data"]:
        st.markdown(f"<div style='font-size:20px; font-weight:800; color:{text_primary}; margin-top:14px;'>📥 Export Data & Executive Briefings</div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="exact-panel" style="margin-top: 14px;">
                <div style="font-size: 14px; font-weight: 700; color: #38bdf8; margin-bottom: 8px;">
                    Filtered School Analytics Export ({len(filtered_df):,} Schools)
                </div>
                <div style="font-size: 12px; color: {text_secondary}; margin-bottom: 12px;">
                    Download the active filtered school analytics dataset with calculated risk indicators, attendance, and facility counts.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Filtered Analytics CSV",
            data=csv_bytes,
            file_name="edupulse_filtered_analytics.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.dataframe(filtered_df.head(25), use_container_width=True, hide_index=True)

# ============================================================
# 14. FOOTER
# ============================================================

st.markdown(
    f"""
    <div style="text-align: center; color: {text_muted}; font-size: 11px; margin-top: 36px; padding-top: 14px; border-top: 1px solid {card_border};">
        🎓 <strong>EduPulse</strong> • State Education Intelligence Platform
    </div>
    """,
    unsafe_allow_html=True
)