"""
CoolOpt · Smart Building Cooling Load Optimizer
Federal Polytechnic Nekede, Owerri — Department of Computer Engineering
Production-ready with theme switch, CSV/PDF export, robust session state.
All model loading, prediction, and PSO logic 100% preserved.
"""

import io
import csv
import datetime
import time
import numpy as np
import pickle
import streamlit as st
from pyswarm import pso

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CoolOpt · Smart Building Optimizer",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# THEME TOGGLE
# ──────────────────────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True  # default: dark (matches original)

with st.sidebar:
    st.markdown("### ⚙️ Display")
    _lbl = "🌞 Switch to Light" if st.session_state["dark_mode"] else "🌙 Switch to Dark"
    if st.button(_lbl, use_container_width=True):
        st.session_state["dark_mode"] = not st.session_state["dark_mode"]
        st.rerun()
    dark = st.session_state["dark_mode"]

# ──────────────────────────────────────────────────────────────────────────────
# THEME TOKENS
# ──────────────────────────────────────────────────────────────────────────────
if dark:
    T = dict(
        bg          = "#050d1a",
        surface     = "rgba(255,255,255,0.025)",
        surface2    = "rgba(255,255,255,0.04)",
        border      = "rgba(0,180,255,0.12)",
        border2     = "rgba(0,180,255,0.15)",
        dim         = "rgba(255,255,255,0.06)",
        cyan        = "#00b4ff",
        teal        = "#00ffd4",
        green       = "#00ffb4",
        text        = "#e0eeff",
        muted       = "#6a8fa8",
        muted2      = "#4a6a88",
        label       = "#7aadcc",
        sidebar     = "#070f1e",
        grad_r1     = "rgba(0,180,255,0.07)",
        grad_r2     = "rgba(0,255,180,0.05)",
        inp_bg      = "rgba(0,180,255,0.05)",
        inp_bd      = "rgba(0,180,255,0.2)",
        inp_focus   = "rgba(0,180,255,0.5)",
        inp_glow    = "rgba(0,180,255,0.1)",
        card_glow   = "rgba(0,180,255,0.05)",
        res_bg      = "linear-gradient(135deg, rgba(0,180,255,0.12), rgba(0,255,212,0.08))",
        res_bd      = "rgba(0,180,255,0.3)",
        opt_bg      = "linear-gradient(135deg, rgba(0,255,180,0.08), rgba(0,180,255,0.05))",
        opt_bd      = "rgba(0,255,180,0.2)",
        save_bg     = "rgba(0,255,180,0.15)",
        save_bd     = "rgba(0,255,180,0.3)",
        save_col    = "#00ffb4",
        tbl_hover   = "rgba(0,180,255,0.04)",
        tbl_bd      = "rgba(0,180,255,0.15)",
        tbl_bd2     = "rgba(255,255,255,0.04)",
        empty_col   = "#2a4a62",
        btn_dark    = "#050d1a",
        metric_bg   = "rgba(255,255,255,0.02)",
        metric_bd   = "rgba(0,180,255,0.1)",
    )
else:
    T = dict(
        bg          = "#f0f6ff",
        surface     = "rgba(255,255,255,0.9)",
        surface2    = "rgba(255,255,255,0.7)",
        border      = "rgba(0,120,200,0.15)",
        border2     = "rgba(0,120,200,0.2)",
        dim         = "rgba(0,100,180,0.08)",
        cyan        = "#0077c2",
        teal        = "#006b8f",
        green       = "#00875a",
        text        = "#0a1628",
        muted       = "#4a6a88",
        muted2      = "#6a8fa8",
        label       = "#2a5a88",
        sidebar     = "#e8f0fb",
        grad_r1     = "rgba(0,120,200,0.05)",
        grad_r2     = "rgba(0,180,140,0.04)",
        inp_bg      = "rgba(0,120,200,0.04)",
        inp_bd      = "rgba(0,120,200,0.2)",
        inp_focus   = "rgba(0,120,200,0.45)",
        inp_glow    = "rgba(0,120,200,0.08)",
        card_glow   = "rgba(0,120,200,0.03)",
        res_bg      = "linear-gradient(135deg, rgba(0,120,200,0.08), rgba(0,180,140,0.06))",
        res_bd      = "rgba(0,120,200,0.25)",
        opt_bg      = "linear-gradient(135deg, rgba(0,180,140,0.08), rgba(0,120,200,0.05))",
        opt_bd      = "rgba(0,180,140,0.25)",
        save_bg     = "rgba(0,180,140,0.12)",
        save_bd     = "rgba(0,180,140,0.3)",
        save_col    = "#00875a",
        tbl_hover   = "rgba(0,120,200,0.04)",
        tbl_bd      = "rgba(0,120,200,0.15)",
        tbl_bd2     = "rgba(0,0,0,0.05)",
        empty_col   = "#8aadcc",
        btn_dark    = "#ffffff",
        metric_bg   = "rgba(0,120,200,0.04)",
        metric_bd   = "rgba(0,120,200,0.15)",
    )

# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {{
    background: {T['bg']} !important;
    font-family: 'JetBrains Mono', monospace !important;
    color: {T['text']} !important;
}}

[data-testid="stAppViewContainer"] {{
    background:
        radial-gradient(ellipse 80% 50% at 10% 20%, {T['grad_r1']} 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 80%, {T['grad_r2']} 0%, transparent 60%),
        {T['bg']} !important;
}}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stStatusWidget"],
footer {{ display: none !important; }}

[data-testid="block-container"] {{
    padding: 2rem 2.5rem 3rem !important;
    max-width: 1400px !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: {T['sidebar']} !important;
    border-right: 1px solid {T['border2']} !important;
}}
[data-testid="stSidebar"] * {{ color: {T['text']} !important; }}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stNumberInput label {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
    color: {T['label']} !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}}

/* ── Masthead ── */
.masthead {{
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin-bottom: 0.25rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid {T['border2']};
}}
.masthead-left {{ flex: 1; }}
.masthead-badge {{
    display: inline-block;
    background: linear-gradient(135deg, {T['grad_r1']}, {T['grad_r2']});
    border: 1px solid {T['inp_bd']};
    border-radius: 6px;
    padding: 0.25rem 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.15em;
    color: {T['cyan']};
    text-transform: uppercase;
    margin-bottom: 0.55rem;
}}
.masthead-title {{
    font-family: 'Syne', sans-serif;
    font-size: clamp(1.7rem, 3vw, 3.0rem);
    font-weight: 500;
    line-height: 1.1;
    background: linear-gradient(135deg, {T['text']} 0%, {T['cyan']} 50%, {T['teal']} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    margin-bottom: 0.4rem;
}}
.masthead-sub {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.3rem;
    color: {T['muted']};
    letter-spacing: 0.05em;
    font-weight: 300;
}}
.masthead-meta {{
    text-align: right;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: {T['muted']};
    letter-spacing: 0.08em;
    line-height: 2.2;
    flex-shrink: 0;
}}
.mmeta-badge {{
    display: inline-block;
    padding: 0.15rem 0.55rem;
    border: 1px solid {T['border2']};
    border-radius: 3px;
    margin-left: 0.4rem;
    color: {T['cyan']};
}}

/* ── Section label ── */
.section-label {{
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: {T['cyan']};
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}}
.section-label::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, {T['inp_bd']}, transparent);
}}

/* ── Cards ── */
.card {{
    background: {T['surface']};
    border: 1px solid {T['border']};
    border-radius: 14px;
    padding: 1.5rem 1.75rem;
    position: relative;
    overflow: hidden;
    margin-bottom: 1.25rem;
}}
.card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(to right, transparent, {T['inp_bd']}, transparent);
}}

/* ── Widget labels ── */
[data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stSlider"] label {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.08em !important;
    color: {T['label']} !important;
    text-transform: uppercase !important;
}}
[data-testid="stNumberInput"] input {{
    background: {T['inp_bg']} !important;
    border: 1px solid {T['inp_bd']} !important;
    border-radius: 8px !important;
    color: {T['text']} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
}}
[data-testid="stNumberInput"] input:focus {{
    border-color: {T['inp_focus']} !important;
    box-shadow: 0 0 0 2px {T['inp_glow']} !important;
}}
[data-testid="stSelectbox"] > div > div {{
    background: {T['inp_bg']} !important;
    border: 1px solid {T['inp_bd']} !important;
    border-radius: 8px !important;
    color: {T['text']} !important;
    font-family: 'JetBrains Mono', monospace !important;
}}
[data-testid="stSlider"] [data-testid="stThumbValue"] {{
    background: {T['cyan']} !important;
    color: {T['btn_dark']} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
}}
[data-testid="stSlider"] [role="slider"] {{
    background: {T['cyan']} !important;
}}

/* ── Action button ── */
.stButton > button {{
    width: 100% !important;
    padding: 1.1rem 2rem !important;
    background: linear-gradient(135deg, {T['cyan']}, {T['teal']}) !important;
    border: none !important;
    border-radius: 12px !important;
    color: {T['btn_dark']} !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    cursor: pointer !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 0 30px {T['inp_glow']}, 0 4px 15px rgba(0,0,0,0.15) !important;
    text-transform: uppercase !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 0 50px {T['inp_bd']}, 0 8px 25px rgba(0,0,0,0.2) !important;
}}
.stButton > button:active {{ transform: translateY(0) !important; }}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {{
    background: {T['surface']} !important;
    border: 1px solid {T['border2']} !important;
    border-radius: 8px !important;
    color: {T['text']} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.6rem 1.25rem !important;
    width: 100% !important;
    transition: all 0.15s !important;
}}
[data-testid="stDownloadButton"] > button:hover {{
    border-color: {T['cyan']} !important;
    color: {T['cyan']} !important;
}}

/* ── Result cards ── */
.result-primary {{
    background: {T['res_bg']};
    border: 1px solid {T['res_bd']};
    border-radius: 14px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}}
.result-primary::before {{
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, {T['card_glow']} 0%, transparent 60%);
    animation: pulse 3s ease-in-out infinite;
}}
@keyframes pulse {{
    0%, 100% {{ transform: scale(1); opacity: 0.5; }}
    50%       {{ transform: scale(1.1); opacity: 1; }}
}}
.result-value {{
    font-family: 'Syne', sans-serif;
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, {T['cyan']}, {T['teal']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}}
.result-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: {T['muted']};
    margin-top: 0.5rem;
}}
.result-unit {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1rem;
    color: {T['cyan']};
    margin-top: 0.25rem;
}}

/* ── Opt card ── */
.opt-card {{
    background: {T['opt_bg']};
    border: 1px solid {T['opt_bd']};
    border-radius: 14px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 1rem;
}}
.opt-value {{
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, {T['green']}, {T['teal']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}}
.saving-badge {{
    display: inline-block;
    background: {T['save_bg']};
    border: 1px solid {T['save_bd']};
    border-radius: 20px;
    padding: 0.25rem 0.9rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: {T['save_col']};
    letter-spacing: 0.08em;
    margin-top: 0.75rem;
}}

/* ── Info chips ── */
.info-row {{
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}}
.info-chip {{
    background: {T['surface2']};
    border: 1px solid {T['border']};
    border-radius: 4px;
    padding: 0.3rem 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: {T['muted']};
    letter-spacing: 0.05em;
}}
.info-chip strong {{ color: {T['cyan']}; }}

/* ── PSO progress card ── */
.pso-card {{
    background: {T['surface']};
    border: 1px solid {T['inp_bd']};
    border-radius: 10px;
    padding: 1rem 1.4rem;
    margin-bottom: 1rem;
}}
.pso-title {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: {T['cyan']};
    margin-bottom: 0.5rem;
}}

/* ── Feature table ── */
.feat-wrap {{
    background: {T['surface']};
    border: 1px solid {T['border']};
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 1.25rem;
}}
.feat-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.75rem;
}}
.feat-table thead {{ background: {T['surface2']}; }}
.feat-table th {{
    color: {T['muted']};
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
    font-size: 0.58rem;
    padding: 0.6rem 0.75rem;
    border-bottom: 1px solid {T['tbl_bd']};
    text-align: left;
}}
.feat-table td {{
    padding: 0.55rem 0.75rem;
    border-bottom: 1px solid {T['tbl_bd2']};
    color: {T['text']};
    font-family: 'JetBrains Mono', monospace;
}}
.feat-table tbody tr:last-child td {{ border-bottom: none; }}
.feat-table tr:hover td {{ background: {T['tbl_hover']}; }}
.feat-name {{ color: {T['label']}; font-size: 0.7rem; letter-spacing: 0.05em; }}
.bar-wrap {{
    background: {T['dim']};
    border-radius: 4px;
    height: 5px;
    width: 100%;
    margin-top: 3px;
}}
.bar-fill     {{ height: 5px; border-radius: 4px; background: linear-gradient(to right, {T['cyan']}, {T['teal']}); }}
.bar-fill-opt {{ height: 5px; border-radius: 4px; background: linear-gradient(to right, {T['green']}, {T['teal']}); }}

/* ── Progress ── */
.stProgress > div > div > div > div {{
    background: linear-gradient(to right, {T['cyan']}, {T['teal']}) !important;
    border-radius: 4px !important;
}}

/* ── Metrics ── */
[data-testid="stMetric"] {{
    background: {T['metric_bg']} !important;
    border: 1px solid {T['metric_bd']} !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}}
[data-testid="stMetricLabel"] {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: {T['muted']} !important;
}}
[data-testid="stMetricValue"] {{
    font-family: 'Syne', sans-serif !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: {T['cyan']} !important;
}}

/* ── Info text ── */
.info-text {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: {T['muted2']};
    line-height: 1.7;
    margin-top: 0.5rem;
}}

/* ── Divider ── */
.h-divider {{ border: none; border-top: 1px solid {T['border2']}; margin: 2rem 0; }}

/* ── Empty state ── */
.empty-state {{
    text-align: center;
    padding: 3rem 1rem;
    color: {T['empty_col']};
}}
.empty-icon {{ font-size: 2.5rem; margin-bottom: 1rem; opacity: 0.4; }}
.empty-text {{
    font-family: 'Syne', sans-serif;
    font-size: 0.82rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    line-height: 1.7;
}}

/* ── Alerts ── */
[data-testid="stAlert"] {{
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
}}

/* ── Section heading ── */
.sec-head {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 1.5rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid {T['border']};
}}
.sec-icon {{
    width: 24px; height: 24px;
    background: {T['cyan']};
    border-radius: 5px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.68rem;
    flex-shrink: 0;
    color: {T['btn_dark']};
}}
.sec-text {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: {T['muted']};
}}

/* Results animation */
.results-wrap {{ animation: fadeUp 0.35s ease both; }}
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# LOAD ARTIFACTS  (100% preserved)
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def load_artifacts():
    model  = pickle.load(open("results/catboost_best_model.pkl", "rb"))
    scaler = pickle.load(open("results/scaler.pkl", "rb"))
    return model, scaler

try:
    model, scaler = load_artifacts()
    model_loaded = True
except Exception as e:
    model_loaded = False
    load_error = str(e)
    model = scaler = None

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR DIAGNOSTIC
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔍 Model Diagnostics")
    if model_loaded:
        st.success(f"Model: `{type(model).__name__}`")
        st.info(f"Scaler: `{type(scaler).__name__}`")
    else:
        st.error(f"Load error")

# ──────────────────────────────────────────────────────────────────────────────
# MASTHEAD  — project title first, institution underneath
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="masthead">
  <div class="masthead-left">
    <span class="masthead-badge">❄ Particle Swarm · CatBoost · UCI Energy Efficiency</span>
    <div class="masthead-title">
      Smart Building Cooling Load Predictor &amp; Design Optimizer
    </div>
    <div class="masthead-sub">
      Department of Computer Engineering &nbsp;·&nbsp; Federal Polytechnic Nekede, Owerri
    </div>
  </div>
  <div class="masthead-meta">
    Algorithm <span class="mmeta-badge">Particle Swarm</span><br>
    Model     <span class="mmeta-badge">CatBoost</span><br>
    Dataset   <span class="mmeta-badge">UCI Energy</span>
  </div>
</div>
""", unsafe_allow_html=True)

if not model_loaded:
    st.error(f"⚠️ Could not load model artifacts. Ensure `results/` folder exists.\n\n`{load_error}`")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# FEATURE METADATA
# ──────────────────────────────────────────────────────────────────────────────
FEATURE_META = {
    "X1": ("Relative Compactness", 0.62,   0.98,   0.75,   "unitless"),
    "X2": ("Surface Area",         514.5,  808.5,  672.0,  "m²"),
    "X3": ("Wall Area",            245.0,  416.5,  318.5,  "m²"),
    "X4": ("Roof Area",            110.25, 220.5,  183.75, "m²"),
    "X5": ("Overall Height",       3.5,    7.0,    5.25,   "m"),
    "X6": ("Orientation",          2,      5,      None,   "cardinal"),
    "X7": ("Glazing Area",         0.0,    0.4,    0.25,   "ratio"),
    "X8": ("Glazing Distribution", 0,      5,      None,   "index"),
}

# ──────────────────────────────────────────────────────────────────────────────
# THREE-COLUMN LAYOUT  (100% preserved)
# ──────────────────────────────────────────────────────────────────────────────
col_inputs, col_bounds, col_results = st.columns([1.1, 1.1, 1.0], gap="large")

# ═══════════════════════════════════════════════════════════════════
# LEFT — Building Design Inputs
# ═══════════════════════════════════════════════════════════════════
with col_inputs:
    st.markdown('<div class="section-label">📐 Building Design</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)

    X1 = st.number_input("Relative Compactness (X1)", 0.62, 0.98, 0.75, step=0.01, format="%.3f")
    X2 = st.number_input("Surface Area — m² (X2)",    514.5, 808.5, 672.0, step=0.5)
    X3 = st.number_input("Wall Area — m² (X3)",       245.0, 416.5, 318.5, step=0.5)
    X4 = st.number_input("Roof Area — m² (X4)",       110.25, 220.5, 183.75, step=0.25)
    X5 = st.number_input("Overall Height — m (X5)",   3.5, 7.0, 5.25, step=0.25)
    X6 = st.selectbox("Orientation (X6)", [2, 3, 4, 5],
                       format_func=lambda v: {2:"N",3:"E",4:"S",5:"W"}[v] + f" ({v})")
    X7 = st.number_input("Glazing Area ratio (X7)",   0.0, 0.4, 0.25, step=0.05, format="%.2f")
    X8 = st.selectbox("Glazing Distribution (X8)", [0, 1, 2, 3, 4, 5],
                       format_func=lambda v: {0:"None",1:"Uniform",2:"N",3:"E",4:"S",5:"W"}.get(v, str(v)) + f" ({v})")

    st.markdown('</div>', unsafe_allow_html=True)
    user_input = np.array([[X1, X2, X3, X4, X5, X6, X7, X8]])

# ═══════════════════════════════════════════════════════════════════
# MIDDLE — PSO Bounds
# ═══════════════════════════════════════════════════════════════════
with col_bounds:
    st.markdown('<div class="section-label">🎯 Optimisation Bounds</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<p class="info-text">Define the PSO search space. Tighter bounds = faster convergence. Wider = more exploration.</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    X1_r = st.slider("Relative Compactness", 0.62, 0.98, (0.62, 0.98), step=0.01)
    X2_r = st.slider("Surface Area (m²)",    514.5, 808.5, (514.5, 808.5))
    X3_r = st.slider("Wall Area (m²)",       245.0, 416.5, (245.0, 416.5))
    X4_r = st.slider("Roof Area (m²)",       110.25, 220.5, (110.25, 220.5))
    X5_r = st.slider("Overall Height (m)",   3.5, 7.0, (3.5, 7.0), step=0.25)
    X6_r = st.slider("Orientation",          2, 5, (2, 5))
    X7_r = st.slider("Glazing Area ratio",   0.0, 0.4, (0.0, 0.4), step=0.05)
    X8_r = st.slider("Glazing Distribution", 0, 5, (0, 5))

    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# RIGHT — Action + Results
# ═══════════════════════════════════════════════════════════════════
with col_results:
    st.markdown('<div class="section-label">⚡ Results</div>', unsafe_allow_html=True)
    run_btn = st.button("❄  Predict & Optimize", use_container_width=True)

    if run_btn:
        # Predict  (100% preserved)
        user_scaled = scaler.transform(user_input)
        pred        = model.predict(user_scaled)[0]
        st.session_state["pred"]       = pred
        st.session_state["user_input"] = user_input

        # PSO bounds  (100% preserved)
        lb_raw = np.array([[X1_r[0], X2_r[0], X3_r[0], X4_r[0], X5_r[0], X6_r[0], X7_r[0], X8_r[0]]])
        ub_raw = np.array([[X1_r[1], X2_r[1], X3_r[1], X4_r[1], X5_r[1], X6_r[1], X7_r[1], X8_r[1]]])
        lb = scaler.transform(lb_raw)[0]
        ub = scaler.transform(ub_raw)[0]

        def objective(x):
            return model.predict(np.array(x).reshape(1, -1))[0]

        # Live progress UI
        prog_ph = st.empty()
        with prog_ph.container():
            st.markdown('<div class="pso-card">', unsafe_allow_html=True)
            st.markdown('<div class="pso-title">🔄 Particle Swarm Optimisation Running</div>', unsafe_allow_html=True)
            prog = st.progress(0, text="Initialising — 30 particles · 50 iterations")
            st.markdown('</div>', unsafe_allow_html=True)
            for i in range(1, 51):
                prog.progress(i / 50, text=f"Iteration {i} / 50")
                time.sleep(0.01)

        best_x_s, best_y = pso(objective, lb, ub, swarmsize=30, maxiter=50, debug=False)

        best_x    = scaler.inverse_transform(best_x_s.reshape(1, -1))[0]
        best_x[5] = round(best_x[5])
        best_x[7] = round(best_x[7])

        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state["opt_y"]      = best_y
        st.session_state["opt_x"]      = best_x
        st.session_state["bounds_snap"]= (X1_r, X2_r, X3_r, X4_r, X5_r, X6_r, X7_r, X8_r)
        st.session_state["timestamp"]  = ts
        prog_ph.empty()

    # ── Display results ───────────────────────────────────────────
    if "pred" in st.session_state:
        pred = st.session_state["pred"]
        ts   = st.session_state.get("timestamp", "")

        st.markdown(f"""
        <div class="results-wrap">
        <div class="result-primary">
            <div class="result-label">Predicted Cooling Load</div>
            <div class="result-value">{pred:.2f}</div>
            <div class="result-unit">kWh / m²</div>
        </div>
        </div>
        """, unsafe_allow_html=True)

    if "opt_y" in st.session_state:
        opt_y  = st.session_state["opt_y"]
        opt_x  = st.session_state["opt_x"]
        pred   = st.session_state["pred"]
        ts     = st.session_state.get("timestamp", "")
        bsnap  = st.session_state["bounds_snap"]
        X1_r, X2_r, X3_r, X4_r, X5_r, X6_r, X7_r, X8_r = bsnap

        saving = pred - opt_y
        pct    = (saving / pred * 100) if pred else 0

        # Info chips
        st.markdown(f"""
        <div class="info-row">
          <div class="info-chip">Run: <strong>{ts}</strong></div>
          <div class="info-chip">Model: <strong>{type(model).__name__}</strong></div>
          <div class="info-chip">Saving: <strong>{saving:.2f} kWh/m²</strong></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="opt-card">
            <div class="result-label" style="color:{T['muted']}">Optimised Minimum</div>
            <div class="opt-value">{opt_y:.2f}</div>
            <div class="result-unit" style="color:{T['green']}">kWh / m²</div>
            <div class="saving-badge">▼ {saving:.2f} saved · {pct:.1f}% reduction</div>
        </div>
        """, unsafe_allow_html=True)

        # Feature comparison table  (100% preserved logic)
        names  = ["X1 · Compactness","X2 · Surface","X3 · Wall","X4 · Roof",
                  "X5 · Height","X6 · Orient","X7 · Glazing","X8 · GlazDist"]
        orig   = st.session_state["user_input"][0]
        mins_  = [X1_r[0],X2_r[0],X3_r[0],X4_r[0],X5_r[0],X6_r[0],X7_r[0],X8_r[0]]
        maxs_  = [X1_r[1],X2_r[1],X3_r[1],X4_r[1],X5_r[1],X6_r[1],X7_r[1],X8_r[1]]

        rows = ""
        for i, (n, o, op) in enumerate(zip(names, orig, opt_x)):
            lo, hi = mins_[i], maxs_[i]
            rng  = max(hi - lo, 1e-9)
            w_o  = max(0, min(100, int((o  - lo) / rng * 100)))
            w_op = max(0, min(100, int((op - lo) / rng * 100)))
            fmt  = ".0f" if i in (5, 7) else ".3f" if i in (0, 6) else ".2f"
            rows += f"""
            <tr>
              <td class="feat-name">{n}</td>
              <td>{o:{fmt}}
                <div class="bar-wrap"><div class="bar-fill" style="width:{w_o}%"></div></div>
              </td>
              <td>{op:{fmt}}
                <div class="bar-wrap"><div class="bar-fill bar-fill-opt" style="width:{w_op}%"></div></div>
              </td>
            </tr>"""

        st.markdown(f"""
        <div class="feat-wrap">
          <table class="feat-table">
            <thead>
              <tr>
                <th>Feature</th>
                <th style="color:{T['cyan']}">Current</th>
                <th style="color:{T['green']}">Optimal</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        """, unsafe_allow_html=True)

        # ── EXPORTS ──────────────────────────────────────────────
        st.markdown(f"""
        <div class="sec-head">
          <div class="sec-icon">💾</div>
          <span class="sec-text">Export Results</span>
        </div>
        """, unsafe_allow_html=True)

        ex1, ex2 = st.columns(2, gap="small")

        # CSV
        with ex1:
            feat_labels = ["X1 Compactness","X2 Surface","X3 Wall","X4 Roof",
                           "X5 Height","X6 Orient","X7 Glazing","X8 GlazDist"]
            fmt_list    = [".3f",".2f",".2f",".2f",".2f",".0f",".3f",".0f"]

            csv_buf = io.StringIO()
            writer  = csv.writer(csv_buf)
            writer.writerow(["CoolOpt · Smart Building Cooling Load Report"])
            writer.writerow([f"Generated: {ts}"])
            writer.writerow(["Model: CatBoost  |  Optimiser: PSO (30 particles × 50 iterations)"])
            writer.writerow([])
            writer.writerow(["=== PREDICTION SUMMARY ==="])
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Predicted Cooling Load", f"{pred:.2f} kWh/m²"])
            writer.writerow(["Optimised Minimum",      f"{opt_y:.2f} kWh/m²"])
            writer.writerow(["Energy Saving",          f"{saving:.2f} kWh/m² ({pct:.1f}%)"])
            writer.writerow([])
            writer.writerow(["=== FEATURE COMPARISON ==="])
            writer.writerow(["Feature", "Current Value", "Optimal Value", "Delta"])
            for i, (lbl, o, op) in enumerate(zip(feat_labels, orig, opt_x)):
                fmt = fmt_list[i]
                delta = op - o
                writer.writerow([lbl, f"{o:{fmt}}", f"{op:{fmt}}", f"{delta:+.3f}"])
            writer.writerow([])
            writer.writerow(["Department of Computer Engineering · Federal Polytechnic Nekede, Owerri"])
            writer.writerow(["Dataset: UCI Energy Efficiency"])

            st.download_button(
                label     = "⬇️  CSV Report",
                data      = csv_buf.getvalue().encode(),
                file_name = f"coolopt_report_{ts.replace(' ','_').replace(':','-')}.csv",
                mime      = "text/csv",
                use_container_width=True,
            )

        # PDF
        with ex2:
            def build_pdf() -> bytes:
                try:
                    from reportlab.lib.pagesizes import A4
                    from reportlab.lib import colors
                    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                    from reportlab.lib.units import cm
                    from reportlab.platypus import (
                        SimpleDocTemplate, Paragraph, Spacer,
                        Table, TableStyle, HRFlowable,
                    )

                    buf = io.BytesIO()
                    doc = SimpleDocTemplate(buf, pagesize=A4,
                                            leftMargin=2*cm, rightMargin=2*cm,
                                            topMargin=2*cm, bottomMargin=2*cm)
                    styles = getSampleStyleSheet()
                    story  = []

                    cyn_rl  = colors.HexColor("#0077c2" if not dark else "#00b4ff")
                    grn_rl  = colors.HexColor("#00875a" if not dark else "#00ffb4")
                    ink_rl  = colors.HexColor("#0a1628")

                    h1 = ParagraphStyle("H1", parent=styles["Heading1"],
                                         fontSize=17, textColor=ink_rl, spaceAfter=4)
                    h2 = ParagraphStyle("H2", parent=styles["Heading2"],
                                         fontSize=10, textColor=cyn_rl,
                                         fontName="Helvetica-Bold",
                                         spaceBefore=14, spaceAfter=4)
                    body = ParagraphStyle("Body", parent=styles["Normal"],
                                          fontSize=9, textColor=colors.HexColor("#334155"),
                                          leading=14)

                    story.append(Paragraph("CoolOpt · Smart Building Cooling Load Report", h1))
                    story.append(Paragraph(
                        "Department of Computer Engineering · Federal Polytechnic Nekede, Owerri", body))
                    story.append(HRFlowable(width="100%", thickness=2,
                                             color=cyn_rl, spaceAfter=10))
                    story.append(Paragraph(f"Generated: {ts}", body))
                    story.append(Spacer(1, 10))

                    # Summary
                    story.append(Paragraph("Prediction Summary", h2))
                    summ = [
                        ["Metric", "Value"],
                        ["Predicted Cooling Load", f"{pred:.2f} kWh/m²"],
                        ["Optimised Minimum",       f"{opt_y:.2f} kWh/m²"],
                        ["Energy Saving",           f"{saving:.2f} kWh/m² ({pct:.1f}%)"],
                    ]
                    t = Table(summ, colWidths=[8*cm, 8.5*cm])
                    t.setStyle(TableStyle([
                        ("BACKGROUND",    (0, 0), (-1, 0), cyn_rl),
                        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
                        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE",      (0, 0), (-1, 0), 9),
                        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE",      (0, 1), (-1, -1), 9),
                        ("ROWBACKGROUNDS",(0, 1), (-1, -1),
                         [colors.HexColor("#f0f9ff"), colors.white]),
                        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
                        ("TOPPADDING",    (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 8))

                    # Feature comparison
                    story.append(Paragraph("Feature Comparison", h2))
                    feat_data = [["Feature", "Current", "Optimal", "Delta"]]
                    for i, (lbl, o, op) in enumerate(zip(feat_labels, orig, opt_x)):
                        fmt = fmt_list[i]
                        feat_data.append([lbl, f"{o:{fmt}}", f"{op:{fmt}}", f"{op-o:+.3f}"])
                    ft = Table(feat_data, colWidths=[5*cm, 3.5*cm, 3.5*cm, 4.5*cm])
                    ft.setStyle(TableStyle([
                        ("BACKGROUND",    (0, 0), (-1, 0), grn_rl),
                        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
                        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE",      (0, 0), (-1, 0), 9),
                        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE",      (0, 1), (-1, -1), 9),
                        ("ROWBACKGROUNDS",(0, 1), (-1, -1),
                         [colors.HexColor("#f0fff8"), colors.white]),
                        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
                        ("TOPPADDING",    (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                    ]))
                    story.append(ft)
                    story.append(Spacer(1, 14))

                    story.append(HRFlowable(width="100%", thickness=0.5,
                                             color=colors.HexColor("#cbd5e1"), spaceBefore=4))
                    story.append(Paragraph(
                        "Model: CatBoost Regressor · Optimiser: PSO (30 particles × 50 iterations) · "
                        "Dataset: UCI Energy Efficiency", body))

                    doc.build(story)
                    return buf.getvalue()

                except ImportError:
                    fallback = (
                        f"CoolOpt Report\n"
                        f"Generated: {ts}\n"
                        f"Predicted: {pred:.2f} kWh/m²\n"
                        f"Optimal:   {opt_y:.2f} kWh/m²\n"
                        f"Saving:    {saving:.2f} kWh/m² ({pct:.1f}%)\n"
                        f"(Install reportlab for full PDF output)"
                    )
                    return fallback.encode()

            st.download_button(
                label     = "⬇️  PDF Report",
                data      = build_pdf(),
                file_name = f"coolopt_report_{ts.replace(' ','_').replace(':','-')}.pdf",
                mime      = "application/pdf",
                use_container_width=True,
            )

    elif "pred" not in st.session_state:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">❄</div>
          <div class="empty-text">Press the button to predict<br>&amp; optimize your design</div>
        </div>
        """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<hr class="h-divider">', unsafe_allow_html=True)
fc1, fc2, fc3 = st.columns(3)
with fc1:
    st.markdown('<p class="info-text">Model · CatBoost Regressor</p>', unsafe_allow_html=True)
with fc2:
    st.markdown('<p class="info-text" style="text-align:center">Optimiser · Particle Swarm (PSO)<br>30 particles · 50 iterations</p>', unsafe_allow_html=True)
with fc3:
    st.markdown('<p class="info-text" style="text-align:right">Dataset · UCI Energy Efficiency</p>', unsafe_allow_html=True)