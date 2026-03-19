"""
Emotional Intelligence Companion
Warm neutral · Clean cards · Polished UI
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
from src.database.connection import get_db_connection, init_connection_pool

st.set_page_config(page_title="Emotional Companion", page_icon="🌿",
                   layout="wide", initial_sidebar_state="collapsed")

DEFAULTS = {"current_page": "reflect", "show_analysis": False,
            "latest_result": None, "dark_mode": False}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

@st.cache(allow_output_mutation=True)
def init_db():
    init_connection_pool()
    return True
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
    "proud": "#E8845C", "pride": "#E8845C", "excitement": "#DE6B48",
    "joy": "#5BA0D0", "gratitude": "#4DBFA7", "fear": "#48A9A6",
    "anxiety": "#E4B54A", "anger": "#D35D6E", "sadness": "#7C8CC6",
    "love": "#CF6679", "disappointment": "#8CABA8", "optimism": "#E9B44C",
    "annoyance": "#C76B6B", "embarrassment": "#B388B0", "guilt": "#8A9EA0",
    "neutral": "#A0A9B0", "confusion": "#D4935D", "surprise": "#6BB5C9",
    "confident": "#8D7CC6",
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
# Theme
# ═══════════════════════════════════════════════════════════════════════════
def T():
    dark = st.session_state.dark_mode
    if dark:
        return dict(
            bg="#1a1a1f", card="#242429", card_border="#2e2e35",
            shadow="rgba(0,0,0,0.4)", shadow_hover="rgba(0,0,0,0.55)",
            text="#d4d4d8", text2="#a1a1aa", muted="#71717a", heading="#fafafa",
            input_bg="#2a2a30", input_border="#3a3a42",
            accent="#c4956a", accent_light="rgba(196,149,106,0.12)",
            divider="#2a2a30",
            tag_bg="rgba(196,149,106,0.15)", tag_text="#c4956a",
            pf="#a1a1aa", pg="rgba(255,255,255,0.05)",
            iframe_bg="#242429", streak_bg="#2a2a30",
            toggle_bg="#3a3a42", toggle_knob="#c4956a",
        )
    else:
        return dict(
            bg="#f0ece4", card="#ffffff", card_border="#e8e4dc",
            shadow="rgba(120,110,95,0.10)", shadow_hover="rgba(120,110,95,0.18)",
            text="#4a4543", text2="#6b6560", muted="#9a938c", heading="#2c2825",
            input_bg="#faf8f5", input_border="#ddd8d0",
            accent="#b07d4f", accent_light="rgba(176,125,79,0.10)",
            divider="#e8e4dc",
            tag_bg="rgba(176,125,79,0.12)", tag_text="#9a7040",
            pf="#6b6560", pg="rgba(0,0,0,0.04)",
            iframe_bg="#ffffff", streak_bg="#faf8f5",
            toggle_bg="#e8e4dc", toggle_knob="#b07d4f",
        )

# ═══════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════
def inject_css():
    t = T(); dark = st.session_state.dark_mode
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=JetBrains+Mono:wght@500;700&display=swap');
        * {{ font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif; }}

        .stApp {{ background: {t['bg']}; }}
        .block-container {{ padding-top: 0.5rem !important; padding-bottom: 2rem !important; max-width: 1180px; }}
        header[data-testid="stHeader"] {{ display: none !important; }}
        [data-testid="stSidebar"] {{ display: none; }}
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        [data-testid="stDecoration"] {{ display: none !important; }}
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{ display: none !important; }}
        iframe {{ background: transparent !important; border: none !important; }}

        .card {{
            background: {t['card']}; border: 1px solid {t['card_border']};
            border-radius: 18px; padding: 1.3rem 1.4rem; margin-bottom: 0.85rem;
            box-shadow: 0 2px 12px {t['shadow']}; transition: box-shadow 0.2s ease;
        }}
        .card:hover {{ box-shadow: 0 4px 20px {t['shadow_hover']}; }}

        .card-eq {{
            background: {t['card']}; border: 1px solid {t['card_border']};
            border-radius: 18px; padding: 1.3rem 1.4rem; margin-bottom: 0.85rem;
            box-shadow: 0 2px 12px {t['shadow']}; transition: box-shadow 0.2s ease;
            min-height: 195px; display: flex; flex-direction: column;
        }}
        .card-eq:hover {{ box-shadow: 0 4px 20px {t['shadow_hover']}; }}

        /* ---- header ---- */
        .header-row {{
            display: flex; justify-content: space-between; align-items: center;
            padding: 0.4rem 0 0.5rem;
        }}
        .header-left {{ display: flex; align-items: center; gap: 0.8rem; }}
        .header-brand {{ font-size: 1.1rem; font-weight: 700; color: {t['heading']}; }}
        .header-greeting {{ font-size: 0.88rem; color: {t['muted']}; font-weight: 500; }}
        .header-right {{ display: flex; align-items: center; gap: 0.7rem; }}

        /* ---- refresh btn (HTML) ---- */
        .refresh-btn {{
            display: inline-flex; align-items: center; gap: 0.3rem;
            padding: 0.35rem 0.7rem; border-radius: 10px; cursor: pointer;
            background: {t['card']}; border: 1px solid {t['card_border']};
            box-shadow: 0 1px 4px {t['shadow']};
            font-size: 0.78rem; font-weight: 600; color: {t['text2']};
            transition: all 0.15s;
        }}
        .refresh-btn:hover {{ background: {t['streak_bg']}; }}

        /* ---- dark/light toggle (CSS only) ---- */
        .theme-pill {{
            display: inline-flex; align-items: center;
            background: {t['toggle_bg']}; border-radius: 20px;
            padding: 3px; cursor: pointer; position: relative;
            width: 62px; height: 28px;
            border: 1px solid {t['card_border']};
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.08);
            transition: background 0.3s;
        }}
        .theme-pill-knob {{
            width: 22px; height: 22px; border-radius: 50%;
            background: {t['toggle_knob']};
            box-shadow: 0 1px 4px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
            display: flex; align-items: center; justify-content: center;
            font-size: 0.7rem;
            transform: translateX({'32px' if dark else '0px'});
        }}

        .section-title {{ font-size: 1.35rem; font-weight: 700; color: {t['heading']}; margin-bottom: 0.5rem; letter-spacing: -0.3px; }}
        .card-title {{ font-size: 0.98rem; font-weight: 600; color: {t['heading']}; margin-bottom: 0.45rem; }}

        /* ---- EI score ---- */
        .ei-box {{ display: flex; align-items: flex-end; gap: 0.15rem; margin: 0.4rem 0; }}
        .ei-num {{ font-size: 2.8rem; font-weight: 800; color: {t['heading']}; line-height: 1; font-family: 'JetBrains Mono', monospace; }}
        .ei-denom {{ font-size: 1rem; color: {t['muted']}; font-weight: 500; margin-bottom: 0.35rem; }}

        /* ---- tooltip ---- */
        .tip-wrap {{ position: relative; display: inline-flex; align-items: center; cursor: pointer; }}
        .tip-icon {{
            display: inline-flex; align-items: center; justify-content: center;
            width: 18px; height: 18px; border-radius: 50%;
            background: {t['accent_light']}; color: {t['accent']};
            font-size: 0.65rem; font-weight: 700; margin-left: 0.4rem;
            border: 1px solid {t['accent']}30; transition: background 0.2s;
        }}
        .tip-icon:hover {{ background: {t['accent']}25; }}
        .tip-bubble {{
            visibility: hidden; opacity: 0;
            position: absolute; left: 50%; top: calc(100% + 8px);
            transform: translateX(-50%); z-index: 999;
            width: 260px; padding: 0.75rem 0.9rem;
            background: {t['card']}; color: {t['text2']};
            border: 1px solid {t['card_border']}; border-radius: 12px;
            box-shadow: 0 6px 24px {t['shadow_hover']};
            font-size: 0.76rem; line-height: 1.5; font-weight: 400;
            transition: opacity 0.2s ease, visibility 0.2s ease;
            pointer-events: none;
        }}
        .tip-bubble::before {{
            content: ""; position: absolute; top: -6px; left: 50%; transform: translateX(-50%);
            border-left: 6px solid transparent; border-right: 6px solid transparent;
            border-bottom: 6px solid {t['card_border']};
        }}
        .tip-wrap:hover .tip-bubble {{ visibility: visible; opacity: 1; }}
        .tip-bubble strong {{ color: {t['heading']}; }}

        /* ---- streak ---- */
        .streak-num {{ font-size: 2.4rem; font-weight: 800; color: {t['heading']}; line-height: 1; font-family: 'JetBrains Mono', monospace; }}
        .streak-unit {{ font-size: 0.95rem; color: {t['muted']}; font-weight: 500; }}
        .streak-emotion {{ display: flex; align-items: center; gap: 0.4rem; margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid {t['divider']}; }}
        .streak-emotion-name {{ font-size: 0.9rem; font-weight: 700; color: {t['heading']}; }}
        .streak-emotion-sub {{ font-size: 0.74rem; color: {t['muted']}; margin-top: 0.1rem; }}

        /* ---- metrics bar ---- */
        .metrics-bar {{ display: flex; gap: 0.6rem; margin-top: 0.3rem; margin-bottom: 0.3rem; }}

        /* ---- insight items ---- */
        .insight-item {{
            display: flex; align-items: flex-start; gap: 0.55rem;
            padding: 0.5rem 0; border-bottom: 1px solid {t['divider']};
            font-size: 0.84rem; color: {t['text']}; line-height: 1.4;
        }}
        .insight-item:last-child {{ border-bottom: none; padding-bottom: 0; }}
        .insight-icon {{ font-size: 0.85rem; margin-top: 0.08rem; flex-shrink: 0; }}

        /* ---- reflection ---- */
        .reflection-card {{
            background: {t['card']}; border: 1px solid {t['card_border']};
            border-radius: 18px; padding: 1.2rem 1.4rem; margin-top: 0.5rem;
            box-shadow: 0 2px 12px {t['shadow']};
        }}
        .reflection-title {{ font-size: 0.95rem; font-weight: 600; color: {t['heading']}; margin-bottom: 0.3rem; }}
        .reflection-body {{ font-size: 0.84rem; color: {t['text2']}; line-height: 1.55; }}

        /* ---- analysis banner ---- */
        .analysis-banner {{
            background: {t['accent_light']}; border: 1px solid {t['accent']}30;
            border-radius: 16px; padding: 1rem 1.15rem; margin-top: 0.5rem;
        }}
        .analysis-emotion {{ font-size: 1.4rem; font-weight: 700; color: {t['heading']}; }}
        .analysis-conf {{ font-size: 0.78rem; color: {t['muted']}; margin-top: 0.1rem; }}
        .analysis-text {{ font-size: 0.84rem; color: {t['text2']}; margin-top: 0.5rem; line-height: 1.5; }}

        /* ---- history ---- */
        .history-card {{
            background: {t['card']}; border: 1px solid {t['card_border']};
            border-radius: 16px; padding: 0.9rem 1.1rem; margin-bottom: 0.55rem;
            box-shadow: 0 1px 8px {t['shadow']};
        }}
        .history-date {{ font-size: 0.68rem; color: {t['muted']}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.4px; }}
        .history-emotion-tag {{
            display: inline-block; border-radius: 8px; padding: 0.15rem 0.5rem;
            font-size: 0.74rem; font-weight: 600; background: {t['tag_bg']}; color: {t['tag_text']};
        }}
        .history-text {{ font-size: 0.84rem; color: {t['text']}; margin-top: 0.3rem; line-height: 1.45; }}
        .history-meta {{ font-size: 0.68rem; color: {t['muted']}; margin-top: 0.2rem; }}

        /* ---- stat highlight ---- */
        .stat-highlight {{
            background: {t['card']}; border: 1px solid {t['card_border']};
            border-radius: 14px; padding: 0.85rem 1rem; text-align: center;
            box-shadow: 0 1px 6px {t['shadow']};
        }}
        .stat-big {{ font-size: 1.85rem; font-weight: 800; color: {t['accent']}; font-family: 'JetBrains Mono', monospace; }}
        .stat-label {{ font-size: 0.62rem; color: {t['muted']}; text-transform: uppercase; letter-spacing: 0.6px; font-weight: 600; margin-top: 0.1rem; }}

        /* ---- Streamlit overrides ---- */
        .stTextArea>div>div>textarea {{
            background: {t['input_bg']} !important;
            border: 1.5px solid {t['input_border']} !important;
            border-radius: 14px !important; padding: 1rem !important;
            color: {t['heading']} !important; font-size: 0.9rem !important;
        }}
        .stTextArea>div>div>textarea:focus {{
            border-color: {t['accent']} !important;
            box-shadow: 0 0 0 3px {t['accent']}18 !important;
        }}
        .stTextArea label {{ font-size: 0 !important; height: 0 !important; margin: 0 !important; padding: 0 !important; }}

        .stButton>button {{
            background: {t['accent']} !important;
            color: #fff !important; border: none !important;
            border-radius: 12px !important; padding: 0.5rem 1.4rem !important;
            font-weight: 600 !important; font-size: 0.84rem !important;
            box-shadow: 0 2px 8px {t['accent']}30 !important;
            width: 100% !important; transition: all 0.2s ease !important;
        }}
        .stButton>button:hover {{
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 14px {t['accent']}45 !important;
        }}

        /* ---- nav: pill-shaped, text only, underline active ---- */
        .nav-active button {{
            background: transparent !important;
            color: {t['accent']} !important;
            box-shadow: none !important;
            border: none !important;
            border-bottom: 2.5px solid {t['accent']} !important;
            border-radius: 0 !important;
            font-weight: 700 !important;
            font-size: 0.9rem !important;
        }}
        .nav-inactive button {{
            background: transparent !important;
            color: {t['muted']} !important;
            box-shadow: none !important;
            border: none !important;
            border-bottom: 2.5px solid transparent !important;
            border-radius: 0 !important;
            font-weight: 500 !important;
            font-size: 0.9rem !important;
            opacity: 0.4 !important;
            transition: opacity 0.25s ease !important;
        }}
        .nav-inactive button:hover {{
            color: {t['text2']} !important;
            border-bottom: 2.5px solid {t['divider']} !important;
            transform: none !important;
            opacity: 0.85 !important;
        }}

        /* ---- toolbar buttons ---- */
        .tb .stButton button {{
            width: auto !important;
            padding: 0.35rem 0.8rem !important;
            font-size: 0.8rem !important;
            background: {t['card']} !important;
            color: {t['heading']} !important;
            box-shadow: 0 1px 6px {t['shadow']} !important;
            border: 1px solid {t['card_border']} !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
        }}
        .tb .stButton button:hover {{
            background: {'rgba(60,60,80,0.5)' if st.session_state.dark_mode else 'rgba(0,0,0,0.04)'} !important;
            transform: none !important;
        }}

        /* theme toggle: inverted colors */
        .theme-toggle .stButton button {{
            width: auto !important;
            padding: 0.35rem 0.8rem !important;
            font-size: 0.8rem !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
            background: {'#fafafa' if st.session_state.dark_mode else '#2c2825'} !important;
            color: {'#2c2825' if st.session_state.dark_mode else '#fafafa'} !important;
            border: none !important;
            box-shadow: 0 2px 8px {'rgba(0,0,0,0.15)' if st.session_state.dark_mode else 'rgba(0,0,0,0.25)'} !important;
        }}
        .theme-toggle .stButton button:hover {{
            opacity: 0.85 !important;
            transform: none !important;
        }}

        h1,h2,h3 {{ color: {t['heading']} !important; }}
        p {{ color: {t['text']} !important; }}
        hr {{ border-color: {t['divider']} !important; margin: 0.4rem 0 !important; }}
        .stAlert {{ border-radius: 12px !important; }}
        .stSelectbox label {{ color: {t['text']} !important; font-weight: 600 !important; font-size: 0.84rem !important; }}
    </style>
    """, unsafe_allow_html=True)


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

@st.cache(ttl=60, allow_output_mutation=True)
def load_all_entries():
    try:
        with get_db_connection() as conn:
            return pd.read_sql("""
                SELECT r.entry_id, r.user_id, r.raw_text, r.created_at,
                       p.cleaned_text, p.word_count, p.quality_score,
                       e.emotion, e.confidence
                FROM raw_journal_entries r
                LEFT JOIN processed_entries p ON r.entry_id = p.entry_id
                LEFT JOIN emotion_predictions e ON r.entry_id = e.entry_id
                ORDER BY r.created_at DESC;
            """, conn)
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()


# ═══════════════════════════════════════════════════════════════════════════
# Chart builders
# ═══════════════════════════════════════════════════════════════════════════
CHART_H = 260  # uniform chart height

def _pb():
    t = T()
    return dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans, sans-serif", color=t["pf"], size=12))

def chart_emotion_bar(df, horizontal=False, top_n=7):
    if df.empty or "emotion" not in df.columns: return None
    c = df["emotion"].value_counts().head(top_n)
    if horizontal: c = c.sort_values()
    colors = [EMOTION_COLORS.get(e, "#b07d4f") for e in c.index]
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
    t = T(); cm = {"Positive": "#5BA0D0", "Negative": "#D35D6E", "Neutral": "#A0A9B0"}
    fig = go.Figure()
    for s in ["Positive", "Negative", "Neutral"]:
        sub = daily[daily["sentiment"] == s].sort_values("date")
        if sub.empty: continue
        fig.add_trace(go.Scatter(x=sub["date"], y=sub["count"], name=s, mode="lines+markers",
            line=dict(color=cm[s], width=2.5, shape="spline"), marker=dict(size=6)))
    fig.update_layout(**_pb(), height=CHART_H, margin=dict(t=12, b=30, l=35, r=12),
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=t["pg"], title="Entries"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"))
    return fig

def chart_emotion_donut(df):
    if df.empty or "emotion" not in df.columns: return None
    c = df["emotion"].value_counts().head(10)
    colors = [EMOTION_COLORS.get(e, "#b07d4f") for e in c.index]
    labs = [f"{EMOTION_EMOJIS.get(e,'')} {e.title()}" for e in c.index]
    fig = go.Figure(go.Pie(labels=labs, values=c.values, hole=0.55,
        marker=dict(colors=colors, line=dict(color="rgba(0,0,0,0)", width=2)),
        textinfo="percent", textfont=dict(size=11)))
    fig.update_layout(**_pb(), height=CHART_H, margin=dict(t=8, b=8, l=8, r=8),
        showlegend=True, legend=dict(font=dict(size=10)))
    return fig

def chart_confidence_hist(df):
    if df.empty or "confidence" not in df.columns: return None
    t = T()
    fig = go.Figure(go.Histogram(x=df["confidence"].dropna(), nbinsx=20,
        marker_color="rgba(176,125,79,0.5)", marker_line=dict(color="rgba(176,125,79,0.8)", width=1)))
    fig.update_layout(**_pb(), height=CHART_H, margin=dict(t=8, b=30, l=35, r=12),
        xaxis=dict(title="Confidence", showgrid=False),
        yaxis=dict(title="Count", showgrid=True, gridcolor=t["pg"]), bargap=0.05)
    return fig

def chart_word_scatter(df):
    if df.empty or "word_count" not in df.columns: return None
    tmp = df.dropna(subset=["word_count"]).copy()
    tmp["date"] = pd.to_datetime(tmp["created_at"])
    tmp["sentiment"] = tmp["emotion"].apply(get_sentiment) if "emotion" in tmp.columns else "Neutral"
    t = T(); cm = {"Positive": "#5BA0D0", "Negative": "#D35D6E", "Neutral": "#A0A9B0"}
    fig = go.Figure()
    for s in ["Positive", "Negative", "Neutral"]:
        sub = tmp[tmp["sentiment"] == s]
        if sub.empty: continue
        fig.add_trace(go.Scatter(x=sub["date"], y=sub["word_count"], mode="markers", name=s,
            marker=dict(size=8, color=cm[s], opacity=0.7)))
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
        colorscale=[[0,"rgba(176,125,79,0.05)"],[1,"rgba(176,125,79,0.75)"]], showscale=False))
    fig.update_layout(**_pb(), height=CHART_H, margin=dict(t=8, b=22, l=70, r=8),
        xaxis=dict(showgrid=False, dtick=3), yaxis=dict(showgrid=False, autorange="reversed"))
    return fig

CARD_H = CHART_H + 100  # card = chart + title + padding

def render_chart_card(title, fig, height=None, fallback="Not enough data yet"):
    t = T()
    h = height or CARD_H
    if fig:
        inner = fig.to_html(full_html=False, include_plotlyjs="cdn", config={"displayModeBar": False})
    else:
        inner = f'<p style="color:{t["muted"]};padding:2.5rem;text-align:center;font-size:0.88rem;">{fallback}</p>'
        h = 120
    html = f"""<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@600&display=swap" rel="stylesheet">
<style>*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{background:{t['iframe_bg']};font-family:'DM Sans',sans-serif;overflow:hidden;}}
.c{{background:{t['card']};border:1px solid {t['card_border']};border-radius:18px;padding:1.1rem 1.2rem;
box-shadow:0 2px 12px {t['shadow']};}}
.t{{font-size:0.98rem;font-weight:600;color:{t['heading']};margin-bottom:0.2rem;}}
.js-plotly-plot .plotly .main-svg{{background:transparent !important;}}
</style></head><body><div class="c"><div class="t">{title}</div>{inner}</div></body></html>"""
    components.html(html, height=h, scrolling=False)


# ═══════════════════════════════════════════════════════════════════════════
# Navigation (text-only, underline active)
# ═══════════════════════════════════════════════════════════════════════════
def render_nav():
    c1, c2, c3, c4 = st.columns(4)
    for key, label, col in [("reflect","Reflect",c1),("snapshot","Snapshot",c2),
                             ("insights","Insights",c3),("history","History",c4)]:
        with col:
            cls = "nav-active" if st.session_state.current_page == key else "nav-inactive"
            st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
            if st.button(label, key=f"nav_{key}"):
                st.session_state.current_page = key; st.experimental_rerun()
            st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: Reflect
# ═══════════════════════════════════════════════════════════════════════════
def page_reflect(df):
    t = T()
    ei = calculate_ei_score(df); stk = calculate_streak(df); bal = get_emotional_balance(df)
    dom = df["emotion"].mode()[0] if not df.empty and "emotion" in df.columns and len(df["emotion"].dropna()) > 0 else ""

    # Stable prompt
    if "journal_prompt" not in st.session_state:
        st.session_state.journal_prompt = JOURNAL_PROMPTS[datetime.now().minute % len(JOURNAL_PROMPTS)]
    prompt = st.session_state.journal_prompt

    # ── Journal entry ──
    greeting = get_greeting()
    st.markdown(f'<p style="color:{t["muted"]};font-size:0.92rem;margin-bottom:0.1rem;">Good {greeting}, Parth 👋</p>'
                f'<div class="section-title">What\'s on your mind?</div>'
                f'<p style="color:{t["muted"]};font-size:0.84rem;margin:-0.3rem 0 0.5rem;"></p>',
                unsafe_allow_html=True)

    # Key-swap trick: changing key forces a fresh empty text area
    if "ta_key" not in st.session_state:
        st.session_state.ta_key = 0
    entry_text = st.text_area("Write your thoughts here", height=120, placeholder=prompt,
                              key=f"ta_{st.session_state.ta_key}")

    col_s1, col_btn, col_s2 = st.columns([1, 1, 1])
    with col_btn:
        analyze_clicked = st.button("Analyze Emotions")

    if analyze_clicked:
        wc = len(entry_text.strip().split()) if entry_text.strip() else 0
        if wc >= 5:
            with st.spinner("Analyzing..."):
                try:
                    from src.etl.pipeline import process_journal_entry
                    result = process_journal_entry("Parth", entry_text.strip(), "manual")
                    if result.get("success"):
                        st.session_state.show_analysis = True
                        st.session_state.latest_result = result
                       # st.session_state.journal_prompt = JOURNAL_PROMPTS[(datetime.now().minute + 1) % len(JOURNAL_PROMPTS)]
                        st.experimental_rerun()
                    else: st.error("Analysis failed.")
                except Exception as ex: st.error(f"Error: {ex}")
        else: st.warning(f"Please write at least 5 words. (You wrote {wc})")

    if st.session_state.show_analysis and st.session_state.latest_result:
        r = st.session_state.latest_result
        em = r.get("emotion","neutral"); ej = EMOTION_EMOJIS.get(em,"✨")
        ref = AI_REFLECTIONS.get(em, "Thank you for sharing.")
        st.markdown(f'<div class="analysis-banner">'
                    f'<div class="analysis-emotion">{ej} {em.title()}</div>'
                    f'<div class="analysis-conf">Confidence: {int(r.get("confidence",0)*100)}% · Words: {r.get("word_count",0)} · Quality: {int(r.get("quality_score",0)*100) if r.get("quality_score") else "N/A"}%</div>'
                    f'<div class="analysis-text">{ref}</div></div>', unsafe_allow_html=True)
        if st.button("Clear Result"):
            st.session_state.show_analysis = False; st.session_state.latest_result = None
            st.session_state.ta_key += 1  # swap key → fresh empty text area
            st.experimental_rerun()

    # ── Chart ──
    #render_chart_card("Recent Emotions", chart_emotion_bar(df, horizontal=False, top_n=6),
     #                 fallback="No data yet — start journaling!")

    # ── EI | Streak | Patterns (equal height) ──
    c_ei, c_streak, c_patterns = st.columns([1, 1, 1.2])

    with c_ei:
        st.markdown(f"""
        <div class="card-eq">
            <div class="card-title" style="display:flex;align-items:center;">Emotional Intelligence
                <div class="tip-wrap"><div class="tip-icon">i</div>
                    <div class="tip-bubble">
                        <strong>EI Score</strong> (0–100) measures emotional self-awareness.<br><br>
                        <strong>Balance</strong> (35%) — emotion diversity<br>
                        <strong>Clarity</strong> (30%) — model confidence<br>
                        <strong>Consistency</strong> (20%) — streak length<br>
                        <strong>Expression</strong> (15%) — avg word count
                    </div>
                </div>
            </div>
            <div class="ei-box"><div class="ei-num">{ei}</div><div class="ei-denom">/ 100</div></div>
        </div>""", unsafe_allow_html=True)

    with c_streak:
        st.markdown(f"""
        <div class="card-eq">
            <div class="card-title">Journaling Streak</div>
            <div style="display:flex;align-items:flex-end;gap:0.25rem;margin:0.2rem 0;">
                <div class="streak-num">{stk}</div><div class="streak-unit">days</div>
            </div>
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



# ═══════════════════════════════════════════════════════════════════════════
# PAGE: Snapshot
# ═══════════════════════════════════════════════════════════════════════════
def page_snapshot(df):
    t = T()
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
            <div class="stat-highlight" style="flex:1;"><div class="stat-big" style="color:#5BA0D0;">{pr}%</div><div class="stat-label">Positive</div></div>
            <div class="stat-highlight" style="flex:1;"><div class="stat-big" style="color:#D35D6E;">{nr}%</div><div class="stat-label">Negative</div></div>
            <div class="stat-highlight" style="flex:1;"><div class="stat-big" style="color:#A0A9B0;">{100-pr-nr}%</div><div class="stat-label">Neutral</div></div>
        </div>""", unsafe_allow_html=True)

    ca, cb = st.columns([1, 1])
    with ca: render_chart_card("Writing Patterns", chart_word_scatter(df))
    with cb: render_chart_card("Activity Heatmap", chart_heatmap(df))

    # ── Deep Dive + Takeaways side by side (equal width, matched height) ──
    if "emotion" in df.columns:
        c_dive, c_take = st.columns([1, 1])

        with c_dive:
            top4 = df["emotion"].value_counts().head(4)
            rows = ""
            for em, cnt in top4.items():
                ej = EMOTION_EMOJIS.get(em,"✨"); co = EMOTION_COLORS.get(em,"#b07d4f")
                sub = df[df["emotion"] == em]
                ac = int(sub["confidence"].mean()*100) if "confidence" in sub.columns and not sub["confidence"].isna().all() else 0
                pct = int(cnt/len(df)*100)
                rows += f"""<div style="display:flex;align-items:center;gap:0.7rem;padding:0.65rem 0;border-bottom:1px solid {t['divider']};">
                    <div style="font-size:1.5rem;width:2rem;text-align:center;">{ej}</div>
                    <div style="flex:1;">
                        <div style="font-weight:600;color:{t['heading']};font-size:0.88rem;">{em.title()}</div>
                        <div style="font-size:0.7rem;color:{t['muted']};">{cnt} entries · {ac}% confidence</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:1.1rem;font-weight:700;color:{co};font-family:'JetBrains Mono',monospace;">{pct}%</div>
                    </div>
                </div>"""
            st.markdown(f'<div class="card" style="min-height:310px;"><div class="card-title">Emotion Deep Dive</div>{rows}</div>', unsafe_allow_html=True)

        with c_take:
            if len(df) >= 5:
                top_em = df["emotion"].mode()[0]; tej = EMOTION_EMOJIS.get(top_em,"✨")
                stk = calculate_streak(df); bal = get_emotional_balance(df)
                rp = df.head(7)["emotion"].apply(lambda e: e in POSITIVE_EMOTIONS).sum()
                trend = "improving" if rp >= 4 else "mixed" if rp >= 2 else "challenging"
                trend_co = "#4DBFA7" if trend == "improving" else "#E4B54A" if trend == "mixed" else "#D35D6E"

                st.markdown(f"""<div class="card" style="min-height:310px;">
                    <div class="card-title">Key Takeaways</div>
                    <div style="display:flex;flex-direction:column;gap:0.9rem;margin-top:0.4rem;">
                        <div style="display:flex;align-items:center;gap:0.7rem;">
                            <div style="width:40px;height:40px;border-radius:11px;background:{t['accent_light']};display:flex;align-items:center;justify-content:center;font-size:1.15rem;">{tej}</div>
                            <div><div style="font-size:0.68rem;color:{t['muted']};text-transform:uppercase;letter-spacing:0.5px;font-weight:600;">Dominant</div>
                            <div style="font-weight:700;color:{t['heading']};font-size:0.95rem;">{top_em.title()}</div></div>
                        </div>
                        <div style="display:flex;align-items:center;gap:0.7rem;">
                            <div style="width:40px;height:40px;border-radius:11px;background:rgba(222,107,72,0.1);display:flex;align-items:center;justify-content:center;font-size:1.15rem;">🔥</div>
                            <div><div style="font-size:0.68rem;color:{t['muted']};text-transform:uppercase;letter-spacing:0.5px;font-weight:600;">Streak</div>
                            <div style="font-weight:700;color:{t['heading']};font-size:0.95rem;">{stk} days</div></div>
                        </div>
                        <div style="display:flex;align-items:center;gap:0.7rem;">
                            <div style="width:40px;height:40px;border-radius:11px;background:rgba(77,191,167,0.1);display:flex;align-items:center;justify-content:center;font-size:1.15rem;">⚖️</div>
                            <div><div style="font-size:0.68rem;color:{t['muted']};text-transform:uppercase;letter-spacing:0.5px;font-weight:600;">Balance</div>
                            <div style="font-weight:700;color:{t['heading']};font-size:0.95rem;">{bal}%</div></div>
                        </div>
                        <div style="display:flex;align-items:center;gap:0.7rem;">
                            <div style="width:40px;height:40px;border-radius:11px;background:{trend_co}15;display:flex;align-items:center;justify-content:center;font-size:1.15rem;">📈</div>
                            <div><div style="font-size:0.68rem;color:{t['muted']};text-transform:uppercase;letter-spacing:0.5px;font-weight:600;">Trend</div>
                            <div style="font-weight:700;color:{trend_co};font-size:0.95rem;">{trend.title()}</div></div>
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
        # Date filter
        if "created_at" in df.columns and not df.empty:
            min_date = pd.to_datetime(df["created_at"]).min().date()
            max_date = pd.to_datetime(df["created_at"]).max().date()
            sel_date = st.date_input("Filter by date", value=[], key="hd")
        else:
            sel_date = []

    filt = df.copy()
    if sel_em != "All Emotions" and "emotion" in filt.columns: filt = filt[filt["emotion"] == sel_em]
    # Apply date filter
    if sel_date:
        filt["_date"] = pd.to_datetime(filt["created_at"]).dt.date
        if len(sel_date) == 1:
            filt = filt[filt["_date"] == sel_date[0]]
        elif len(sel_date) == 2:
            filt = filt[(filt["_date"] >= sel_date[0]) & (filt["_date"] <= sel_date[1])]
        filt = filt.drop(columns=["_date"])
    if sel_sort == "Oldest First": filt = filt.sort_values("created_at", ascending=True)
    elif sel_sort == "Highest Confidence" and "confidence" in filt.columns: filt = filt.sort_values("confidence", ascending=False)
    elif sel_sort == "Longest Entries" and "word_count" in filt.columns: filt = filt.sort_values("word_count", ascending=False)

    st.markdown(f'<p style="color:{t["muted"]};font-size:0.78rem;">{len(filt)} of {len(df)} entries</p>', unsafe_allow_html=True)

    for _, row in filt.head(25).iterrows():
        em = row.get("emotion","unknown") if pd.notna(row.get("emotion")) else "unknown"
        ej = EMOTION_EMOJIS.get(em,"❓"); co = EMOTION_COLORS.get(em,"#b07d4f")
        cp = int(row["confidence"]*100) if pd.notna(row.get("confidence")) else 0
        wc = int(row["word_count"]) if pd.notna(row.get("word_count")) else 0
        txt = str(row.get("cleaned_text") if pd.notna(row.get("cleaned_text")) else row.get("raw_text",""))
        pre = txt[:220] + "..." if len(txt) > 220 else txt
        dt = pd.to_datetime(row["created_at"]).strftime("%B %d, %Y · %I:%M %p") if pd.notna(row.get("created_at")) else ""
        st.markdown(f'<div class="history-card"><div style="display:flex;justify-content:space-between;align-items:flex-start;">'
                    f'<div class="history-date">{dt}</div>'
                    f'<div class="history-emotion-tag" style="background:{co}18;color:{co};">{ej} {em.title()} · {cp}%</div></div>'
                    f'<div class="history-text">{pre}</div><div class="history-meta">{wc} words</div></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════
def main():
    inject_css()
    t = T()

    # ── Header: Refresh | Brand (centered) | Toggle ──
    ref_col, brand_col, theme_col = st.columns([1, 4, 1])
    with ref_col:
        st.markdown('<div class="tb">', unsafe_allow_html=True)
        if st.button("↻ Refresh", key="btn_refresh"):
            try: st.caching.clear_cache()
            except AttributeError:
                try: st.legacy_caching.clear_cache()
                except: pass
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with brand_col:
        st.markdown(f'<div style="text-align:center;font-size:1.15rem;font-weight:700;color:{t["heading"]};padding:0.55rem 0 0;">Emotional Companion</div>', unsafe_allow_html=True)
    with theme_col:
        dark = st.session_state.dark_mode
        st.markdown('<div class="theme-toggle">', unsafe_allow_html=True)
        if st.button("☀️ Light" if dark else "🌙 Dark", key="btn_theme"):
            st.session_state.dark_mode = not dark; st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    render_nav()
    st.markdown("---")

    df = load_all_entries()
    pg = st.session_state.current_page
    if pg == "reflect": page_reflect(df)
    elif pg == "snapshot": page_snapshot(df)
    elif pg == "insights": page_insights(df)
    elif pg == "history": page_history(df)

if __name__ == "__main__":
    main()