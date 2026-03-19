"""
Emotional Intelligence Companion
Glassmorphism Edition · Warm neutral · Polished UI
Compatible with Streamlit 1.12.0
"""
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import sys, os

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)
try:
    from src.database.connection import get_db_connection, init_connection_pool
except ImportError:
    pass

st.set_page_config(page_title="Emotional Companion", page_icon="🌿",
                   layout="wide", initial_sidebar_state="collapsed")

DEFAULTS = {"current_page": "reflect", "show_analysis": False,
            "latest_result": None, "dark_mode": False, "user_name": None}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

@st.cache_resource
def init_db():
    try:
        init_connection_pool()
        return True
    except:
        return False
init_db()

# ═══════════════════════════════════════════════════════════════════════════
EMOTION_EMOJIS = {
    "joy": "😊", "excitement": "🎉", "gratitude": "🙏", "proud": "💪",
    "confident": "✨", "optimism": "🌟", "love": "❤️", "sadness": "😔",
    "anger": "😤", "annoyance": "😒", "anxiety": "😰", "fear": "😨",
    "disappointment": "😞", "embarrassment": "😳", "guilt": "😓",
    "neutral": "😐", "confusion": "🤔", "surprise": "😮", "pride": "💪",
}
EMOTION_COLORS = {
    "proud": "#FF6B6B", "pride": "#FF6B6B", "excitement": "#FF8C42",
    "joy": "#4ECDC4", "gratitude": "#45B7D1", "fear": "#6C5CE7",
    "anxiety": "#FDCB6E", "anger": "#E74C3C", "sadness": "#74B9FF",
    "love": "#FD79A8", "disappointment": "#636E72", "optimism": "#00B894",
    "annoyance": "#D63031", "embarrassment": "#E17055", "guilt": "#81ECEC",
    "neutral": "#B2BEC3", "confusion": "#A29BFE", "surprise": "#55E6C1",
    "confident": "#6C5CE7",
}
POSITIVE_EMOTIONS = {"joy","excitement","gratitude","proud","pride","optimism","love","confident","surprise"}
NEGATIVE_EMOTIONS = {"sadness","anger","annoyance","anxiety","fear","disappointment","embarrassment","guilt"}
JOURNAL_PROMPTS = [
    "What made you smile today?", "Was anything weighing on your mind?",
    "What are you grateful for today?", "Describe one moment that stayed with you.",
    "How did you handle a challenge today?", "What emotion surprised you today?",
]
AI_REFLECTIONS = {
    "joy": "You're radiating positivity! Joy can be a powerful motivator — use this energy to tackle something you've been putting off.",
    "proud": "You seem proud and accomplished. This suggests you're making progress in something meaningful.",
    "pride": "You've felt confident and proud recently. This suggests you're making progress in something meaningful.",
    "excitement": "Your excitement is contagious! Channel this momentum into your goals while staying grounded.",
    "gratitude": "Gratitude deepens emotional resilience. You're building a strong foundation for well-being.",
    "optimism": "Your optimistic outlook is a strength. It helps you see possibilities where others see obstacles.",
    "love": "Love and connection are at the heart of well-being. Nurture these bonds that matter to you.",
    "sadness": "It's okay to feel sad. Allow yourself to process these emotions without judgment — they carry wisdom.",
    "anger": "Anger often signals a boundary being crossed. Reflect on what triggered it and how you can address it.",
    "annoyance": "Small frustrations can accumulate. Consider what underlying need isn't being met.",
    "anxiety": "Anxiety often comes from uncertainty. Try breaking down what you can control right now.",
    "fear": "Consider setting aside time to process fear with compassion for yourself.",
    "disappointment": "Disappointment shows you care about outcomes. Use it to recalibrate your expectations.",
    "embarrassment": "Everyone experiences embarrassment. It often fades faster than we expect.",
    "guilt": "Guilt can be a compass for your values. Reflect on what you'd do differently next time.",
    "neutral": "A calm, balanced state can be a great starting point for deeper reflection.",
    "confusion": "Confusion often precedes clarity. Give yourself space to process and things will become clearer.",
    "surprise": "Surprises keep life interesting! Reflect on what this unexpected moment revealed.",
    "confident": "Your confidence is shining through. Trust yourself — you have the skills to handle what's ahead.",
}

# ═══════════════════════════════════════════════════════════════════════════
# Glassmorphism Theme Config
# ═══════════════════════════════════════════════════════════════════════════
def T():
    dark = st.session_state.dark_mode
    if dark:
        return dict(
            bg_image="url('https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?q=80&w=2560&auto=format&fit=crop')",
            card="rgba(15, 15, 25, 0.60)", card_border="rgba(255,255,255,0.10)",
            shadow="rgba(0,0,0,0.35)", shadow_hover="rgba(0,0,0,0.55)",
            text="#d4d4d8", text2="#e4e4e7", muted="#a1a1aa", heading="#ffffff",
            input_bg="rgba(255, 255, 255, 0.18)", input_border="rgba(255,255,255,0.15)",
            accent="#ffffff", accent_light="rgba(255,255,255,0.10)",
            accent_btn="rgba(255,255,255,0.18)", accent_btn_text="#ffffff",
            divider="rgba(255,255,255,0.08)",
            tag_bg="rgba(255,255,255,0.12)", tag_text="#e4e4e7",
            pf="#d4d4d8", pg="rgba(255,255,255,0.06)",
            iframe_bg="transparent", streak_bg="rgba(0,0,0,0.2)",
            toggle_bg="rgba(255,255,255,0.9)", toggle_text="#1a1a25",
            stat_color="#ffffff",
        )
    else:
        return dict(
            bg_image="url('https://images.unsplash.com/photo-1579546929518-9e396f3cc809?q=80&w=2560&auto=format&fit=crop')",
            card="rgba(255,255,255,0.42)", card_border="rgba(255,255,255,0.55)",
            shadow="rgba(31,38,135,0.10)", shadow_hover="rgba(31,38,135,0.20)",
            text="#2a2530", text2="#3a3540", muted="#5a5565", heading="#1a1520",
            input_bg="rgba(255,255,255,0.55)", input_border="rgba(255,255,255,0.7)",
            accent="#1a1520", accent_light="rgba(0,0,0,0.06)",
            accent_btn="rgba(255, 255, 255, 0.65)", # <--- UPDATED
            accent_btn_text="#1a1520",             # <--- UPDATED
            divider="rgba(0,0,0,0.06)",
            tag_bg="rgba(0,0,0,0.07)", tag_text="#3a3540",
            pf="#3a3540", pg="rgba(0,0,0,0.05)",
            iframe_bg="transparent", streak_bg="rgba(255,255,255,0.3)",
            toggle_bg="rgba(20,15,30,0.85)", toggle_text="#ffffff",
            stat_color="#1a1520",
        )

# ═══════════════════════════════════════════════════════════════════════════
# CSS Injection
# ═══════════════════════════════════════════════════════════════════════════
def inject_css():
    t = T(); dark = st.session_state.dark_mode
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=JetBrains+Mono:wght@500;700&display=swap');
        * {{ font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif; }}

        /* Main Background */
        .stApp {{ 
            background-image: {t['bg_image']} !important; 
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        
        .block-container {{ padding-top: 0.5rem !important; padding-bottom: 2rem !important; max-width: 1180px; }}
        header[data-testid="stHeader"], [data-testid="stSidebar"], #MainMenu, footer, [data-testid="stDecoration"] {{ display: none !important; }}
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{ display: none !important; }}
        iframe {{ background: transparent !important; border: none !important; }}

        /* FIX: Remove Streamlit's hidden text area label that causes vertical gaps */
        .stTextArea > label {{ display: none !important; }}

        /* Widget Text Fix for Dark/Light backgrounds */
        .stSelectbox label, .stDateInput label, .stTextInput label {{ color: {t['text']} !important; font-weight: 600 !important; margin-bottom: 0.2rem; }}
        div[data-baseweb="select"] > div {{ background-color: {t['input_bg']} !important; border-color: {t['input_border']} !important; color: {t['heading']} !important; }}

        /* Glass Cards */
        .card, .card-eq, .reflection-card, .history-card, .stat-highlight, .analysis-banner {{
            background: {t['card']}; 
            backdrop-filter: blur(16px) saturate(180%);
            -webkit-backdrop-filter: blur(16px) saturate(180%);
            border: 1px solid {t['card_border']};
            box-shadow: 0 8px 32px {t['shadow']}; 
            transition: all 0.3s ease;
        }}

        .card, .reflection-card, .analysis-banner {{ border-radius: 20px; padding: 1.4rem 1.6rem; margin-bottom: 1rem; }}
        .card:hover, .card-eq:hover {{ box-shadow: 0 12px 40px {t['shadow_hover']}; transform: translateY(-2px); }}

        /* Strict equal height for Reflect cards */
        .card-eq {{
            border-radius: 20px; padding: 1.4rem 1.6rem; margin-bottom: 1rem;
            height: 240px !important; display: flex; flex-direction: column; justify-content: flex-start;
            overflow: hidden;
        }}
        
        .history-card {{ border-radius: 18px; padding: 1.1rem 1.3rem; margin-bottom: 0.75rem; }}
        .stat-highlight {{ border-radius: 18px; padding: 1rem 1.2rem; text-align: center; }}

        .section-title {{ font-size: 1.45rem; font-weight: 700; color: {t['heading']}; margin-bottom: 0.8rem; letter-spacing: -0.3px; }}
        .card-title {{ font-size: 1.05rem; font-weight: 600; color: {t['heading']}; margin-bottom: 0.6rem; }}

        .ei-box {{ display: flex; align-items: flex-end; gap: 0.15rem; margin: 0.4rem 0; }}
        .ei-num, .streak-num {{ font-size: 3.2rem; font-weight: 800; color: {t['heading']}; line-height: 1; font-family: 'JetBrains Mono', monospace; }}
        .ei-denom, .streak-unit {{ font-size: 1rem; color: {t['muted']}; font-weight: 500; margin-bottom: 0.45rem; }}

        .tip-wrap {{ position: relative; display: inline-flex; align-items: center; cursor: pointer; }}
        .tip-icon {{
            display: inline-flex; align-items: center; justify-content: center; width: 18px; height: 18px; border-radius: 50%;
            background: {t['accent_light']}; color: {t['heading']}; font-size: 0.65rem; font-weight: 700; margin-left: 0.4rem; border: 1px solid {t['divider']}; 
        }}
        .tip-bubble {{
            visibility: hidden; opacity: 0; position: absolute; left: 50%; top: calc(100% + 8px); transform: translateX(-50%); z-index: 999;
            width: 260px; padding: 0.75rem 0.9rem; background: {t['card']}; backdrop-filter: blur(20px); color: {t['text2']};
            border: 1px solid {t['card_border']}; border-radius: 12px; box-shadow: 0 6px 24px {t['shadow_hover']};
            font-size: 0.76rem; line-height: 1.5; font-weight: 500; transition: all 0.2s ease; pointer-events: none;
        }}
        .tip-wrap:hover .tip-bubble {{ visibility: visible; opacity: 1; }}

        .metrics-bar {{ display: flex; gap: 0.8rem; margin-top: 0.5rem; margin-bottom: 0.5rem; }}
        .insight-item {{ display: flex; align-items: flex-start; gap: 0.65rem; padding: 0.6rem 0; border-bottom: 1px solid {t['divider']}; font-size: 0.88rem; color: {t['text']}; line-height: 1.4; font-weight: 500; }}
        .insight-item:last-child {{ border-bottom: none; padding-bottom: 0; }}
        .insight-icon {{ font-size: 0.95rem; margin-top: 0.08rem; flex-shrink: 0; }}

        .stat-big {{ font-size: 2.1rem; font-weight: 800; color: {t['heading']}; font-family: 'JetBrains Mono', monospace; }}
        .stat-label {{ font-size: 0.65rem; color: {t['muted']}; text-transform: uppercase; letter-spacing: 0.8px; font-weight: 700; margin-top: 0.2rem; }}

        .stTextArea>div>div>textarea {{
            background: {t['input_bg']} !important;
            backdrop-filter: blur(8px) !important;
            border: 1.5px solid {t['input_border']} !important;
            border-radius: 16px !important; padding: 1.2rem !important;
            color: #1a1520 !important; font-size: 0.95rem !important;
        }}
        .stTextArea>div>div>textarea:focus {{ border-color: {t['heading']} !important; box-shadow: 0 0 0 4px {t['accent_light']} !important; }}
        
        .stButton>button {{
            background: {t['accent_btn']} !important; color: {t['accent_btn_text']} !important; border: 1px solid {t['card_border']} !important;
            backdrop-filter: blur(10px) !important;
            border-radius: 14px !important; padding: 0.6rem 1.6rem !important; font-weight: 600 !important; font-size: 0.88rem !important;
            box-shadow: 0 4px 16px {t['shadow']} !important; width: 100% !important; transition: all 0.25s ease !important;
        }}
        .stButton>button:hover {{ transform: translateY(-2px) !important; box-shadow: 0 8px 24px {t['shadow_hover']} !important; }}

        .nav-active button {{
            background: {t['card']} !important; backdrop-filter: blur(12px) !important;
            color: {t['heading']} !important; border: 1px solid {t['card_border']} !important; border-bottom: 3px solid {t['heading']} !important;
            border-radius: 14px !important; font-weight: 700 !important; font-size: 0.95rem !important; box-shadow: 0 4px 12px {t['shadow']} !important;
        }}
        .nav-inactive button {{
            background: transparent !important; color: {t['muted']} !important; border: 1px solid transparent !important;
            border-bottom: 3px solid transparent !important; border-radius: 14px !important; font-weight: 500 !important;
            font-size: 0.95rem !important; opacity: 0.4 !important; transition: all 0.25s ease !important;
        }}
        .nav-inactive button:hover {{ background: {t['card']} !important; color: {t['heading']} !important; opacity: 0.8 !important; }}

        .tb .stButton button {{
            width: auto !important; padding: 0.4rem 1rem !important; font-size: 0.85rem !important;
            background: {t['card']} !important; backdrop-filter: blur(10px) !important; color: {t['heading']} !important;
            border: 1px solid {t['card_border']} !important; border-radius: 12px !important;
        }}
        
        .theme-toggle .stButton button {{
            width: auto !important; padding: 0.4rem 1rem !important; font-size: 0.85rem !important; font-weight: 700 !important;
            border-radius: 12px !important; border: none !important; background: {t['toggle_bg']} !important; color: {t['toggle_text']} !important;
            backdrop-filter: blur(10px) !important;
        }}
        h1,h2,h3,h4,h5 {{ color: {t['heading']} !important; }}
        p, div {{ color: {t['text']} !important; }}
        hr {{ border-color: {t['divider']} !important; margin: 0.6rem 0 !important; }}

        /* ---- Filter widgets (selectbox, date input) ---- */
        .stSelectbox > div > div,
        .stDateInput > div > div > input,
        .stDateInput > div > div,
        [data-baseweb="input"] > div,
        [data-baseweb="select"] > div {{
            background: {t['input_bg']} !important;
            color: {t['heading']} !important;
            border-color: {t['input_border']} !important;
            border-radius: 12px !important;
        }}
        .stSelectbox label,
        .stDateInput label {{
            color: {t['text']} !important;
            font-weight: 600 !important;
            font-size: 0.84rem !important;
        }}
        .stSelectbox svg {{ fill: {t['heading']} !important; }}
        [data-baseweb="select"] span,
        [data-baseweb="input"] input {{
            color: {t['heading']} !important;
        }}
        /* FIX 2: History Date Picker Text and Placeholder color */
        input[data-testid="stDateInputView"] {{ color: {t['heading']} !important; }}
        div[data-baseweb="input"] input {{ color: {t['heading']} !important; -webkit-text-fill-color: {t['heading']} !important; }}

        .stSelectbox label, .stDateInput label, .stTextInput label {{ color: {t['text']} !important; font-weight: 600 !important; margin-bottom: 0.2rem; }}
        div[data-baseweb="select"] > div {{ background-color: {t['input_bg']} !important; border-color: {t['input_border']} !important; color: {t['heading']} !important; }}

        .card, .card-eq, .reflection-card, .history-card, .stat-highlight, .analysis-banner {{
            background: {t['card']}; 
            backdrop-filter: blur(16px) saturate(180%);
            -webkit-backdrop-filter: blur(16px) saturate(180%);
            border: 1px solid {t['card_border']};
            box-shadow: 0 8px 32px {t['shadow']}; 
            transition: all 0.3s ease;
        }}

        .card, .reflection-card, .analysis-banner {{ border-radius: 20px; padding: 1.4rem 1.6rem; margin-bottom: 1rem; }}
        .card:hover, .card-eq:hover {{ box-shadow: 0 12px 40px {t['shadow_hover']}; transform: translateY(-2px); }}

        .card-eq {{
            border-radius: 20px; padding: 1.4rem 1.6rem; margin-bottom: 1rem;
            height: 240px !important; display: flex; flex-direction: column; justify-content: flex-start;
            overflow: hidden;
        }}
        
        .history-card {{ border-radius: 18px; padding: 1.1rem 1.3rem; margin-bottom: 0.75rem; }}
        .stat-highlight {{ border-radius: 18px; padding: 1rem 1.2rem; text-align: center; }}

        .section-title {{ font-size: 1.45rem; font-weight: 700; color: {t['heading']}; margin-bottom: 0.8rem; letter-spacing: -0.3px; }}
        .card-title {{ font-size: 1.05rem; font-weight: 600; color: {t['heading']}; margin-bottom: 0.6rem; }}

        /* FIX 1: Text Area Background for Dark Mode */
        .stTextArea>div>div>textarea {{
            background: {t['input_bg']} !important;
            backdrop-filter: blur(8px) !important;
            border: 1.5px solid {t['input_border']} !important;
            border-radius: 16px !important; padding: 1.2rem !important;
            color: {t['heading']} !important; font-size: 0.95rem !important;
        }}
        
        .stButton>button {{
            background: {t['accent_btn']} !important; color: {t['accent_btn_text']} !important; border: 1px solid {t['card_border']} !important;
            backdrop-filter: blur(10px) !important;
            border-radius: 14px !important; padding: 0.6rem 1.6rem !important; font-weight: 600 !important; font-size: 0.88rem !important;
            box-shadow: 0 4px 16px {t['shadow']} !important; width: 100% !important; transition: all 0.25s ease !important;
        }}

        /* FIX 3: Selectbox Dropdown and Date Picker Calendar */
        div[data-baseweb="popover"] > div,
        ul[role="listbox"],
        div[data-baseweb="calendar"] {{
            background-color: {t['card']} !important;
            border: 1px solid {t['card_border']} !important;
            backdrop-filter: blur(20px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
            border-radius: 12px !important;
        }}
        
        /* Fixes the individual options in the "Filter" and "Sort" dropdowns */
        li[role="option"] {{
            color: {t['heading']} !important;
            background-color: transparent !important;
            transition: background 0.2s ease !important;
        }}

        /* Highlight the item when hovering or when it is already selected */
        li[role="option"]:hover, 
        li[role="option"][aria-selected="true"] {{
            background-color: {t['accent_light']} !important;
            color: {t['heading']} !important;
        }}

        /* Date Picker Calendar Overrides */
        div[data-baseweb="calendar"] * {{
            color: {t['heading']} !important; 
            background-color: transparent !important;
        }}

        /* Calendar specific hover for dates */
        div[data-baseweb="calendar"] [role="gridcell"]:hover {{
            background-color: {t['accent_light']} !important;
            border-radius: 8px !important;
        }}

        /* Navigation Focus Effect */
        .nav-active button {{
            background: {t['card']} !important; 
            backdrop-filter: blur(12px) !important;
            color: {t['heading']} !important; 
            border: 1px solid {t['card_border']} !important; 
            border-bottom: 3px solid {t['heading']} !important;
            border-radius: 14px !important; 
            font-weight: 700 !important; 
            font-size: 0.95rem !important; 
            box-shadow: 0 4px 12px {t['shadow']} !important;
            opacity: 1 !important; /* Fully visible */
        }}

        .nav-inactive button {{
            background: transparent !important; 
            color: {t['muted']} !important; 
            border: 1px solid transparent !important;
            border-bottom: 3px solid transparent !important; 
            border-radius: 14px !important; 
            font-weight: 500 !important;
            font-size: 0.95rem !important; 
            
            /* THIS IS THE CHANGE: Faded by default */
            opacity: 0.25 !important; 
            filter: blur(0.5px); /* Optional: slight blur for more 'distance' */
            transition: all 0.4s ease !important;
        }}

        .nav-inactive button:hover {{
            background: {t['card']} !important; 
            color: {t['heading']} !important; 
            
            /* Normal look on hover */
            opacity: 1 !important; 
            filter: blur(0px);
            border: 1px solid {t['card_border']} !important;
        }}

        .theme-toggle .stButton button {{
            border-radius: 12px !important; border: none !important; background: {t['toggle_bg']} !important; color: {t['toggle_text']} !important;
        }}

        h1,h2,h3,h4,h5 {{ color: {t['heading']} !important; }}
        p, div {{ color: {t['text']} !important; }}

        /* FIX: Textarea text always dark (background is always light) */
        .stTextArea textarea {{ color: #1a1520 !important; -webkit-text-fill-color: #1a1520 !important; }}
        .stTextArea textarea::placeholder {{ color: #8a8590 !important; -webkit-text-fill-color: #8a8590 !important; }}

        /* FIX: Dropdown/selectbox options always readable */
        ul[role="listbox"] {{ background: #ffffff !important; }}
        li[role="option"] {{ color: #1a1520 !important; }}
        li[role="option"]:hover, li[role="option"][aria-selected="true"] {{ background-color: #f0f0f0 !important; color: #1a1520 !important; }}

        /* FIX: Text input (welcome screen name input) */
        .stTextInput input, .stTextInput div[data-baseweb="input"] input {{ color: #1a1520 !important; -webkit-text-fill-color: #1a1520 !important; background: {t['input_bg']} !important; }}
        div[data-baseweb="input"] {{ background: rgba(255,255,255,0.55) !important; }}
    </style>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# Welcome Screen — Name Prompt
# ═══════════════════════════════════════════════════════════════════════════
def page_welcome():
    inject_css()
    t = T()

    # Theme toggle on welcome screen too
    _, _, theme_col = st.columns([1, 4, 1])
    with theme_col:
        st.markdown('<div class="theme-toggle" style="display:flex;justify-content:flex-end;">', unsafe_allow_html=True)
        if st.button("☀️ Light" if st.session_state.dark_mode else "🌙 Dark", key="btn_theme_welcome"):
            st.session_state.dark_mode = not st.session_state.dark_mode; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Centered welcome card
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown(f"""<div class="card" style="text-align:center;padding:2.5rem 2rem;">
            <div style="font-size:2.8rem;margin-bottom:0.6rem;">🌿</div>
            <div style="font-size:1.8rem;font-weight:800;color:{t['heading']};letter-spacing:-0.5px;">Emotional Companion</div>
            <div style="font-size:0.95rem;color:{t['muted']};margin-top:0.4rem;margin-bottom:1.8rem;">
                Your personal space for emotional reflection and growth.
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f'<div style="text-align:center;font-size:1.1rem;font-weight:600;color:{t["heading"]};margin-bottom:0.5rem;">What should I call you?</div>', unsafe_allow_html=True)
        name_input = st.text_input("Your name", placeholder="Enter your name...", key="welcome_name_input")

        if st.button("Let's Begin ✨", key="btn_start"):
            if name_input.strip():
                st.session_state.user_name = name_input.strip()
                st.rerun()
            else:
                st.warning("Please enter your name to continue.")

# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════
def get_greeting():
    h = datetime.now().hour
    return "Morning" if 5 <= h < 12 else "Afternoon" if h < 17 else "Evening"

def calculate_streak(df):
    if df.empty or "created_at" not in df.columns: return 0
    ud = sorted(pd.to_datetime(df["created_at"]).dt.date.unique(), reverse=True)
    if not ud: return 0
    s, c = 1, ud[0]
    for i in range(1, len(ud)):
        if ud[i] == c - timedelta(days=1): s += 1; c = ud[i]
        else: break
    return s

def get_emotional_balance(df):
    if "emotion" not in df.columns or df.empty: return 0
    p = df["emotion"].value_counts() / len(df)
    ent = -sum(x * np.log(x) for x in p if x > 0)
    mx = np.log(len(p)) if len(p) > 0 else 1
    return int((ent / mx * 100) if mx > 0 else 0)

def calculate_ei_score(df):
    if df.empty: return 0
    bal = get_emotional_balance(df)
    cla = int(df["confidence"].mean() * 100) if "confidence" in df.columns and not df["confidence"].isna().all() else 0
    stk = min(calculate_streak(df) * 5, 20)
    exp = min(int(df["word_count"].mean()), 20) if "word_count" in df.columns and not df["word_count"].isna().all() else 0
    return int(min(0.35 * bal + 0.30 * cla + 0.20 * stk + 0.15 * exp, 100))

def get_sentiment(em):
    if em in POSITIVE_EMOTIONS: return "Positive"
    if em in NEGATIVE_EMOTIONS: return "Negative"
    return "Neutral"

# FIX: Removed the @st.cache decorator completely for instant loading
def load_all_entries():
    try:
        uname = st.session_state.get("user_name") or "Anonymous"
        with get_db_connection() as conn:
            return pd.read_sql("""
                SELECT r.entry_id, r.user_id, r.raw_text, r.created_at,
                       p.cleaned_text, p.word_count, p.quality_score,
                       e.emotion, e.confidence
                FROM raw_journal_entries r
                LEFT JOIN processed_entries p ON r.entry_id = p.entry_id
                LEFT JOIN emotion_predictions e ON r.entry_id = e.entry_id
                WHERE r.user_id = %(uname)s
                ORDER BY r.created_at DESC;
            """, conn, params={"uname": uname})
    except Exception as e:
        return pd.DataFrame()

# ═══════════════════════════════════════════════════════════════════════════
# Chart builders
# ═══════════════════════════════════════════════════════════════════════════
CHART_H = 260 

def _pb():
    t = T()
    return dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans, sans-serif", color=t["pf"], size=12))

def chart_emotion_bar(df, horizontal=False, top_n=7):
    if df.empty or "emotion" not in df.columns: return None
    c = df["emotion"].value_counts().head(top_n)
    if horizontal: c = c.sort_values()
    colors = [EMOTION_COLORS.get(e, "#6C5CE7") for e in c.index]
    labs = [e.title() for e in c.index]; t = T()
    if horizontal:
        fig = go.Figure(go.Bar(x=c.values, y=labs, orientation="h", marker_color=colors,
            text=c.values, textposition="outside", textfont=dict(size=11, color=t["pf"])))
    else:
        fig = go.Figure(go.Bar(x=labs, y=c.values, marker_color=colors,
            text=c.values, textposition="outside", textfont=dict(size=11, color=t["pf"])))
    fig.update_layout(**_pb(), height=CHART_H, margin=dict(t=8, b=30, l=8, r=30),
        xaxis=dict(showgrid=not horizontal, gridcolor=t["pg"], zeroline=False),
        yaxis=dict(showgrid=horizontal, gridcolor=t["pg"]), showlegend=False, bargap=0.3)
    return fig

def chart_emotion_timeline(df):
    if df.empty or "emotion" not in df.columns: return None
    tmp = df.copy(); tmp["date"] = pd.to_datetime(tmp["created_at"]).dt.date
    tmp["sentiment"] = tmp["emotion"].apply(get_sentiment)
    daily = tmp.groupby(["date", "sentiment"]).size().reset_index(name="count")
    t = T(); cm = {"Positive": "#4ECDC4", "Negative": "#FF6B6B", "Neutral": "#A29BFE"}
    fig = go.Figure()
    for s in ["Positive", "Negative", "Neutral"]:
        sub = daily[daily["sentiment"] == s].sort_values("date")
        if sub.empty: continue
        fig.add_trace(go.Scatter(x=sub["date"], y=sub["count"], name=s, mode="lines+markers",
            line=dict(color=cm[s], width=3, shape="spline"), marker=dict(size=7)))
    fig.update_layout(**_pb(), height=CHART_H, margin=dict(t=12, b=30, l=35, r=12),
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=t["pg"], title="Entries"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"))
    return fig

def chart_emotion_donut(df):
    if df.empty or "emotion" not in df.columns: return None
    c = df["emotion"].value_counts().head(10)
    colors = [EMOTION_COLORS.get(e, "#6C5CE7") for e in c.index]
    labs = [f"{EMOTION_EMOJIS.get(e,'')} {e.title()}" for e in c.index]
    fig = go.Figure(go.Pie(labels=labs, values=c.values, hole=0.6,
        marker=dict(colors=colors, line=dict(color="rgba(255,255,255,0.1)", width=2)),
        textinfo="percent", textfont=dict(size=12)))
    fig.update_layout(**_pb(), height=CHART_H, margin=dict(t=8, b=8, l=8, r=8),
        showlegend=True, legend=dict(font=dict(size=11)))
    return fig

def chart_confidence_hist(df):
    if df.empty or "confidence" not in df.columns: return None
    t = T()
    fig = go.Figure(go.Histogram(x=df["confidence"].dropna(), nbinsx=20,
        marker_color="rgba(108,92,231,0.5)", marker_line=dict(color="rgba(108,92,231,0.8)", width=1)))
    fig.update_layout(**_pb(), height=CHART_H, margin=dict(t=8, b=30, l=35, r=12),
        xaxis=dict(title="Confidence", showgrid=False),
        yaxis=dict(title="Count", showgrid=True, gridcolor=t["pg"]), bargap=0.08)
    return fig

def chart_word_scatter(df):
    if df.empty or "word_count" not in df.columns: return None
    tmp = df.dropna(subset=["word_count"]).copy()
    tmp["date"] = pd.to_datetime(tmp["created_at"])
    tmp["sentiment"] = tmp["emotion"].apply(get_sentiment) if "emotion" in tmp.columns else "Neutral"
    t = T(); cm = {"Positive": "#4ECDC4", "Negative": "#FF6B6B", "Neutral": "#A29BFE"}
    fig = go.Figure()
    for s in ["Positive", "Negative", "Neutral"]:
        sub = tmp[tmp["sentiment"] == s]
        if sub.empty: continue
        fig.add_trace(go.Scatter(x=sub["date"], y=sub["word_count"], mode="markers", name=s,
            marker=dict(size=9, color=cm[s], opacity=0.8)))
    fig.update_layout(**_pb(), height=CHART_H, margin=dict(t=8, b=30, l=40, r=12),
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=t["pg"], title="Words"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"))
    return fig

def chart_heatmap(df):
    if df.empty or "created_at" not in df.columns: return None
    tmp = df.copy(); tmp["dt"] = pd.to_datetime(tmp["created_at"])
    tmp["dow"] = tmp["dt"].dt.day_name(); tmp["hour"] = tmp["dt"].dt.hour
    piv = tmp.groupby(["dow", "hour"]).size().reset_index(name="count")
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    piv["dow"] = pd.Categorical(piv["dow"], categories=days, ordered=True)
    mat = piv.pivot_table(index="dow", columns="hour", values="count", fill_value=0).reindex(days)
    fig = go.Figure(go.Heatmap(z=mat.values, x=[f"{h}:00" for h in mat.columns], y=mat.index,
        colorscale=[[0,"rgba(108,92,231,0.05)"],[1,"rgba(108,92,231,0.75)"]], showscale=False))
    fig.update_layout(**_pb(), height=CHART_H, margin=dict(t=8, b=22, l=70, r=8),
        xaxis=dict(showgrid=False, dtick=3), yaxis=dict(showgrid=False, autorange="reversed"))
    return fig

CARD_H = CHART_H + 110

def render_chart_card(title, fig, height=None, fallback="Not enough data yet"):
    t = T()
    h = height or CARD_H
    if fig:
        inner = fig.to_html(full_html=False, include_plotlyjs="cdn", config={"displayModeBar": False})
    else:
        inner = f'<p style="color:{t["muted"]};padding:2.5rem;text-align:center;font-size:0.95rem;">{fallback}</p>'
        h = 130
        
    html = f"""<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@600&display=swap" rel="stylesheet">
<style>*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{background:transparent;font-family:'DM Sans',sans-serif;overflow:hidden;}}
.c{{
    background: {t['card']}; 
    border: 1px solid {t['card_border']}; 
    border-radius: 20px; 
    padding: 1.2rem 1.4rem;
    box-shadow: 0 6px 24px {t['shadow']};
    height: 100%;
}}
.t{{font-size:1.05rem;font-weight:600;color:{t['heading']};margin-bottom:0.4rem;}}
.js-plotly-plot .plotly .main-svg{{background:transparent !important;}}
</style></head><body><div class="c"><div class="t">{title}</div>{inner}</div></body></html>"""
    components.html(html, height=h, scrolling=False)

# ═══════════════════════════════════════════════════════════════════════════
# Navigation
# ═══════════════════════════════════════════════════════════════════════════
def render_nav():
    c1, c2, c3, c4 = st.columns(4)
    for key, label, col in [("reflect","Reflect",c1),("snapshot","Snapshot",c2),
                             ("insights","Insights",c3),("history","History",c4)]:
        with col:
            cls = "nav-active" if st.session_state.current_page == key else "nav-inactive"
            st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
            if st.button(label, key=f"nav_{key}"):
                st.session_state.current_page = key; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# PAGE: Reflect
# ═══════════════════════════════════════════════════════════════════════════
def page_reflect(df):
    t = T()
    ei = calculate_ei_score(df); stk = calculate_streak(df); bal = get_emotional_balance(df)

    if "journal_prompt" not in st.session_state:
        st.session_state.journal_prompt = JOURNAL_PROMPTS[datetime.now().minute % len(JOURNAL_PROMPTS)]
    prompt = st.session_state.journal_prompt

    greeting = get_greeting()
    uname = st.session_state.user_name or "Friend"
    st.markdown(f'<div class="section-title">Good {greeting}, {uname} 👋<br><span style="font-size: 1.1rem; color: {t["muted"]}; font-weight: 500;">Ready to express yourself?</span></div>', unsafe_allow_html=True)

    if "ta_key" not in st.session_state:
        st.session_state.ta_key = 0
    
    st.markdown(f'<div class="card-title">Write a New Journal Entry</div>', unsafe_allow_html=True)
    entry_text = st.text_area("Write your thoughts here", height=130, placeholder=prompt, key=f"ta_{st.session_state.ta_key}")

    col_s1, col_btn, col_s2 = st.columns([1, 1, 1])
    with col_btn:
        analyze_clicked = st.button("Analyze Emotions")

    if analyze_clicked:
        wc = len(entry_text.strip().split()) if entry_text.strip() else 0
        if wc >= 5:
            with st.spinner("Analyzing with Glassmorphic precision..."):
                try:
                    from src.etl.pipeline import process_journal_entry
                    result = process_journal_entry(st.session_state.user_name or "Anonymous", entry_text.strip(), "manual")
                    if result.get("success"):
                        st.session_state.show_analysis = True
                        st.session_state.latest_result = result
                        
                        # With caching completely removed from load_all_entries, 
                        # this rerun will instantly fetch the new data.
                        st.rerun()
                    else: st.error("Analysis failed.")
                except Exception as ex:
                    import traceback
                    st.error(f"Error: {ex}")
                    st.code(traceback.format_exc())
        else: st.warning(f"Please write at least 5 words. (You wrote {wc})")

    if st.session_state.show_analysis and st.session_state.latest_result:
        r = st.session_state.latest_result
        em = r.get("emotion","neutral"); ej = EMOTION_EMOJIS.get(em,"✨")
        ref = AI_REFLECTIONS.get(em, "Thank you for sharing.")
        st.markdown(f'<div class="analysis-banner">'
                    f'<div style="font-size: 1.6rem; font-weight: 700; color: {t["heading"]};">{ej} {em.title()}</div>'
                    f'<div style="font-size: 0.85rem; color: {t["muted"]}; margin-top: 0.2rem;">Confidence: {int(r.get("confidence",0)*100)}% · Words: {r.get("word_count",0)}</div>'
                    f'<div style="font-size: 0.95rem; color: {t["text"]}; margin-top: 0.8rem; line-height: 1.5;">{ref}</div></div>', unsafe_allow_html=True)
        if st.button("Clear Result"):
            st.session_state.show_analysis = False; st.session_state.latest_result = None
            st.session_state.ta_key += 1
            st.rerun()

    c_ei, c_patterns, c_streak = st.columns([1, 1.2, 1])

    with c_ei:
        st.markdown(f"""
        <div class="card-eq">
            <div class="card-title" style="display:flex;align-items:center;">Emotional Intelligence
                <div class="tip-wrap"><div class="tip-icon">i</div>
                    <div class="tip-bubble">
                        <strong>EI Score</strong> (0–100) measures emotional self-awareness.<br><br>
                        <strong>Balance</strong> (35%) — emotion diversity<br>
                        <strong>Clarity</strong> (30%) — model confidence<br>
                        <strong>Consistency</strong> (20%) — streak length
                    </div>
                </div>
            </div>
            <div class="ei-box"><div class="ei-num">{ei}</div><div class="ei-denom">/ 100</div></div>
        </div>""", unsafe_allow_html=True)

    with c_patterns:
        if len(df) >= 3 and "emotion" in df.columns:
            top_em = df["emotion"].mode()[0]; ej = EMOTION_EMOJIS.get(top_em, "✨")
            n_em = df["emotion"].nunique()
            st.markdown(f"""
            <div class="card-eq">
                <div class="card-title">Patterns and Insights</div>
                <div class="insight-item"><div class="insight-icon">{ej}</div><div>{top_em.title()} is rising consistently this week</div></div>
                <div class="insight-item"><div class="insight-icon">✨</div><div>Excitement often appears after moments of uncertainty</div></div>
                <div class="insight-item"><div class="insight-icon">🎯</div><div>Consider processing emotions ({n_em} detected)</div></div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="card-eq"><div class="card-title">Patterns and Insights</div>'
                        f'<p style="color:{t["muted"]};">Keep journaling to reveal patterns!</p></div>', unsafe_allow_html=True)

    with c_streak:
        st.markdown(f"""
        <div class="card-eq">
            <div class="card-title">Journaling Streak</div>
            <div style="display:flex;align-items:flex-end;gap:0.25rem;margin:0.2rem 0;">
                <div class="streak-num">{stk}</div><div class="streak-unit">days</div>
            </div>
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# PAGE: Snapshot
# ═══════════════════════════════════════════════════════════════════════════
def page_snapshot(df):
    st.markdown('<div class="section-title">Emotional Snapshot</div>', unsafe_allow_html=True)
    if df.empty: st.info("No entries yet. Head to Reflect!"); return

    total = len(df); n_em = df["emotion"].nunique() if "emotion" in df.columns else 0
    avg_c = int(df["confidence"].mean()*100) if "confidence" in df.columns and not df["confidence"].isna().all() else 0
    avg_w = int(df["word_count"].mean()) if "word_count" in df.columns and not df["word_count"].isna().all() else 0
    
    st.markdown(f"""<div class="metrics-bar">
        <div class="stat-highlight" style="flex:1;"><div class="stat-big">{total}</div><div class="stat-label">Total Entries</div></div>
        <div class="stat-highlight" style="flex:1;"><div class="stat-big">{n_em}</div><div class="stat-label">Emotions Detected</div></div>
        <div class="stat-highlight" style="flex:1;"><div class="stat-big">{avg_c}%</div><div class="stat-label">Avg Confidence</div></div>
        <div class="stat-highlight" style="flex:1;"><div class="stat-big">{avg_w}</div><div class="stat-label">Avg Word Count</div></div>
    </div>""", unsafe_allow_html=True)

    ca, cb = st.columns([1, 1])
    with ca: render_chart_card("Emotion Distribution", chart_emotion_donut(df))
    with cb: render_chart_card("Sentiment Timeline", chart_emotion_timeline(df))
    cc, cd = st.columns([1, 1])
    with cc: render_chart_card("Confidence Distribution", chart_confidence_hist(df))
    with cd: render_chart_card("Top Emotions", chart_emotion_bar(df, horizontal=True, top_n=10))

# ═══════════════════════════════════════════════════════════════════════════
# PAGE: Insights
# ═══════════════════════════════════════════════════════════════════════════
def page_insights(df):
    t = T()
    st.markdown('<div class="section-title">Deep Insights</div>', unsafe_allow_html=True)
    if df.empty: st.info("No entries yet. Head to Reflect!"); return

    if "emotion" in df.columns:
        pr = int(df["emotion"].apply(lambda e: e in POSITIVE_EMOTIONS).sum() / len(df) * 100)
        nr = int(df["emotion"].apply(lambda e: e in NEGATIVE_EMOTIONS).sum() / len(df) * 100)
        st.markdown(f"""<div class="metrics-bar">
            <div class="stat-highlight" style="flex:1;"><div class="stat-big" style="color:#4ECDC4;">{pr}%</div><div class="stat-label">Positive</div></div>
            <div class="stat-highlight" style="flex:1;"><div class="stat-big" style="color:#FF6B6B;">{nr}%</div><div class="stat-label">Negative</div></div>
            <div class="stat-highlight" style="flex:1;"><div class="stat-big" style="color:#A29BFE;">{100-pr-nr}%</div><div class="stat-label">Neutral</div></div>
        </div>""", unsafe_allow_html=True)

    ca, cb = st.columns([1, 1])
    with ca: render_chart_card("Writing Patterns", chart_word_scatter(df))
    with cb: render_chart_card("Activity Heatmap", chart_heatmap(df))

    if "emotion" in df.columns:
        c_dive, c_take = st.columns([1, 1])
        with c_dive:
            top4 = df["emotion"].value_counts().head(4)
            rows = ""
            for em, cnt in top4.items():
                ej = EMOTION_EMOJIS.get(em,"✨"); co = EMOTION_COLORS.get(em,"#6C5CE7")
                sub = df[df["emotion"] == em]
                ac = int(sub["confidence"].mean()*100) if "confidence" in sub.columns and not sub["confidence"].isna().all() else 0
                pct = int(cnt/len(df)*100)
                rows += f"""<div style="display:flex;align-items:center;gap:0.7rem;padding:0.8rem 0;border-bottom:1px solid {t['divider']};">
                    <div style="font-size:1.6rem;width:2.5rem;text-align:center;">{ej}</div>
                    <div style="flex:1;">
                        <div style="font-weight:600;color:{t['heading']};font-size:0.95rem;">{em.title()}</div>
                        <div style="font-size:0.75rem;color:{t['muted']};">{cnt} entries · {ac}% confidence</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:1.2rem;font-weight:800;color:{co};font-family:'JetBrains Mono',monospace;">{pct}%</div>
                    </div>
                </div>"""
            st.markdown(f'<div class="card" style="height:380px; overflow:hidden;"><div class="card-title">Emotion Deep Dive</div>{rows}</div>', unsafe_allow_html=True)

        with c_take:
            if len(df) >= 5:
                top_em = df["emotion"].mode()[0]; tej = EMOTION_EMOJIS.get(top_em,"✨")
                stk = calculate_streak(df); bal = get_emotional_balance(df)
                rp = df.head(7)["emotion"].apply(lambda e: e in POSITIVE_EMOTIONS).sum()
                trend = "improving" if rp >= 4 else "mixed" if rp >= 2 else "challenging"
                trend_co = "#00B894" if trend == "improving" else "#FDCB6E" if trend == "mixed" else "#D35D6E"

                st.markdown(f"""<div class="card" style="height:380px; overflow:hidden;">
                    <div class="card-title">Key Takeaways</div>
                    <div style="display:flex;flex-direction:column;gap:1.2rem;margin-top:1rem;">
                        <div style="display:flex;align-items:center;gap:1rem;">
                            <div style="width:45px;height:45px;border-radius:14px;background:{t['accent_light']};display:flex;align-items:center;justify-content:center;font-size:1.4rem;">{tej}</div>
                            <div><div style="font-size:0.75rem;color:{t['muted']};text-transform:uppercase;letter-spacing:0.8px;font-weight:700;">Dominant</div>
                            <div style="font-weight:700;color:{t['heading']};font-size:1.1rem;">{top_em.title()}</div></div>
                        </div>
                        <div style="display:flex;align-items:center;gap:1rem;">
                            <div style="width:45px;height:45px;border-radius:14px;background:rgba(222,107,72,0.15);display:flex;align-items:center;justify-content:center;font-size:1.4rem;">🔥</div>
                            <div><div style="font-size:0.75rem;color:{t['muted']};text-transform:uppercase;letter-spacing:0.8px;font-weight:700;">Streak</div>
                            <div style="font-weight:700;color:{t['heading']};font-size:1.1rem;">{stk} days</div></div>
                        </div>
                        <div style="display:flex;align-items:center;gap:1rem;">
                            <div style="width:45px;height:45px;border-radius:14px;background:{trend_co}20;display:flex;align-items:center;justify-content:center;font-size:1.4rem;">📈</div>
                            <div><div style="font-size:0.75rem;color:{t['muted']};text-transform:uppercase;letter-spacing:0.8px;font-weight:700;">Trend</div>
                            <div style="font-weight:700;color:{trend_co};font-size:1.1rem;">{trend.title()}</div></div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# PAGE: History
# ═══════════════════════════════════════════════════════════════════════════
def page_history(df):
    t = T()
    st.markdown('<div class="section-title">Journal History</div>', unsafe_allow_html=True)
    if df.empty: st.info("No entries yet. Head to Reflect!"); return

    f1, f2, f3 = st.columns([1, 1, 1])
    with f1:
        elist = sorted(df["emotion"].dropna().unique().tolist()) if "emotion" in df.columns else []
        sel_em = st.selectbox("Filter by emotion", ["All Emotions"] + elist, key="hf")
    with f2:
        sel_sort = st.selectbox("Sort by", ["Newest First","Oldest First","Highest Confidence","Longest Entries"], key="hs")
    with f3:
        if "created_at" in df.columns and not df.empty:
            sel_date = st.date_input("Filter by date", value=[], key="hd")
        else:
            sel_date = []
    
    st.markdown("<br>", unsafe_allow_html=True)

    filt = df.copy()
    if sel_em != "All Emotions" and "emotion" in filt.columns: filt = filt[filt["emotion"] == sel_em]
    if sel_date:
        filt["_date"] = pd.to_datetime(filt["created_at"]).dt.date
        if len(sel_date) == 1: filt = filt[filt["_date"] == sel_date[0]]
        elif len(sel_date) == 2: filt = filt[(filt["_date"] >= sel_date[0]) & (filt["_date"] <= sel_date[1])]
        filt = filt.drop(columns=["_date"])
    
    if sel_sort == "Oldest First": filt = filt.sort_values("created_at", ascending=True)
    elif sel_sort == "Highest Confidence" and "confidence" in filt.columns: filt = filt.sort_values("confidence", ascending=False)
    elif sel_sort == "Longest Entries" and "word_count" in filt.columns: filt = filt.sort_values("word_count", ascending=False)

    st.markdown(f'<p style="color:{t["muted"]};font-size:0.85rem;font-weight:600;margin-bottom:1rem;">Showing {len(filt)} of {len(df)} entries</p>', unsafe_allow_html=True)

    for _, row in filt.head(25).iterrows():
        em = row.get("emotion","unknown") if pd.notna(row.get("emotion")) else "unknown"
        ej = EMOTION_EMOJIS.get(em,"❓"); co = EMOTION_COLORS.get(em,"#6C5CE7")
        cp = int(row["confidence"]*100) if pd.notna(row.get("confidence")) else 0
        wc = int(row["word_count"]) if pd.notna(row.get("word_count")) else 0
        txt = str(row.get("cleaned_text") if pd.notna(row.get("cleaned_text")) else row.get("raw_text",""))
        pre = txt[:220] + "..." if len(txt) > 220 else txt
        dt = pd.to_datetime(row["created_at"]).strftime("%B %d, %Y · %I:%M %p") if pd.notna(row.get("created_at")) else ""
        
        st.markdown(f'<div class="history-card"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem;">'
                    f'<div style="font-size:0.75rem;color:{t["muted"]};font-weight:700;text-transform:uppercase;letter-spacing:0.5px;">{dt}</div>'
                    f'<div style="display:inline-block;border-radius:10px;padding:0.25rem 0.6rem;font-size:0.8rem;font-weight:700;background:{co}25;color:{co};">{ej} {em.title()} · {cp}%</div></div>'
                    f'<div style="font-size:0.95rem;color:{t["text"]};line-height:1.6;">{pre}</div>'
                    f'<div style="font-size:0.75rem;color:{t["muted"]};margin-top:0.6rem;font-weight:500;">{wc} words</div></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════
def main():
    # ── Gate: Show welcome screen if no name yet ──
    if not st.session_state.user_name:
        page_welcome()
        return

    inject_css()
    t = T()

    # ── Header ──
    ref_col, brand_col, theme_col = st.columns([1, 4, 1])
    with ref_col:
        st.markdown('<div class="tb">', unsafe_allow_html=True)
        if st.button("↻ Refresh", key="btn_refresh"):
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with brand_col:
        st.markdown(f'<div style="text-align:center;font-size:2.1rem;font-weight:800;color:{t["heading"]};padding:0.3rem 0;letter-spacing:-0.5px;text-shadow: 0 2px 10px rgba(0,0,0,0.1);">Emotional Companion</div>', unsafe_allow_html=True)
    with theme_col:
        st.markdown('<div class="theme-toggle" style="display:flex;justify-content:flex-end;">', unsafe_allow_html=True)
        if st.button("☀️ Light" if st.session_state.dark_mode else "🌙 Dark", key="btn_theme"):
            st.session_state.dark_mode = not st.session_state.dark_mode; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    render_nav()
    st.markdown("<br>", unsafe_allow_html=True)

    df = load_all_entries()
    pg = st.session_state.current_page
    if pg == "reflect": page_reflect(df)
    elif pg == "snapshot": page_snapshot(df)
    elif pg == "insights": page_insights(df)
    elif pg == "history": page_history(df)

if __name__ == "__main__":
    main()