import streamlit as st
import numpy as np
import pickle
import time
from pyswarm import pso

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CoolOpt · Smart Building Optimizer",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #050d1a !important;
    font-family: 'JetBrains Mono', monospace;
    color: #e0eeff;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 10% 20%, rgba(0,180,255,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 80%, rgba(0,255,180,0.05) 0%, transparent 60%),
        #050d1a !important;
}

[data-testid="stHeader"], [data-testid="stToolbar"], footer { display: none !important; }
[data-testid="block-container"] { padding: 2rem 2.5rem 3rem !important; max-width: 1400px; }

/* ── Hero ── */
.hero {
    display: flex;
    align-items: flex-end;
    gap: 1.5rem;
    margin-bottom: 0.25rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid rgba(0,180,255,0.15);
}
.hero-badge {
    background: linear-gradient(135deg, #00b4ff22, #00ffb422);
    border: 1px solid #00b4ff44;
    border-radius: 6px;
    padding: 0.25rem 0.75rem;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    color: #00b4ff;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    display: inline-block;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.2rem, 4vw, 3.8rem);
    font-weight: 800;
    line-height: 1;
    background: linear-gradient(135deg, #ffffff 0%, #00b4ff 50%, #00ffd4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
}
.hero-sub {
    font-size: 0.78rem;
    color: #6a8fa8;
    margin-top: 0.6rem;
    letter-spacing: 0.05em;
    font-weight: 300;
}

/* ── Section Labels ── */
.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #00b4ff;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, #00b4ff33, transparent);
}

/* ── Cards ── */
.card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(0,180,255,0.12);
    border-radius: 14px;
    padding: 1.5rem 1.75rem;
    position: relative;
    overflow: hidden;
    margin-bottom: 1.25rem;
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(to right, transparent, #00b4ff55, transparent);
}

/* ── Number inputs ── */
[data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stSlider"] label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.08em !important;
    color: #7aadcc !important;
    text-transform: uppercase !important;
}
[data-testid="stNumberInput"] input {
    background: rgba(0,180,255,0.05) !important;
    border: 1px solid rgba(0,180,255,0.2) !important;
    border-radius: 8px !important;
    color: #e0eeff !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
}
[data-testid="stNumberInput"] input:focus {
    border-color: rgba(0,180,255,0.5) !important;
    box-shadow: 0 0 0 2px rgba(0,180,255,0.1) !important;
}
[data-testid="stSelectbox"] > div > div {
    background: rgba(0,180,255,0.05) !important;
    border: 1px solid rgba(0,180,255,0.2) !important;
    border-radius: 8px !important;
    color: #e0eeff !important;
}

/* ── Slider ── */
[data-testid="stSlider"] [data-testid="stThumbValue"] {
    background: #00b4ff !important;
    color: #050d1a !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
}
[data-testid="stSlider"] [role="slider"] {
    background: #00b4ff !important;
}

/* ── THE Button ── */
.stButton > button {
    width: 100%;
    padding: 1.1rem 2rem !important;
    background: linear-gradient(135deg, #00b4ff, #00ffd4) !important;
    border: none !important;
    border-radius: 12px !important;
    color: #050d1a !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    cursor: pointer !important;
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease !important;
    box-shadow: 0 0 30px rgba(0,180,255,0.3), 0 4px 15px rgba(0,0,0,0.3) !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 50px rgba(0,180,255,0.5), 0 8px 25px rgba(0,0,0,0.4) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Result Cards ── */
.result-primary {
    background: linear-gradient(135deg, rgba(0,180,255,0.12), rgba(0,255,212,0.08));
    border: 1px solid rgba(0,180,255,0.3);
    border-radius: 14px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}
.result-primary::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(0,180,255,0.05) 0%, transparent 60%);
    animation: pulse 3s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.1); opacity: 1; }
}
.result-value {
    font-family: 'Syne', sans-serif;
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00b4ff, #00ffd4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}
.result-label {
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #6a8fa8;
    margin-top: 0.5rem;
}
.result-unit {
    font-size: 1rem;
    color: #00b4ff;
    font-family: 'JetBrains Mono';
    margin-top: 0.25rem;
}

/* ── Opt Card ── */
.opt-card {
    background: linear-gradient(135deg, rgba(0,255,180,0.08), rgba(0,180,255,0.05));
    border: 1px solid rgba(0,255,180,0.2);
    border-radius: 14px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 1rem;
}
.opt-value {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00ffb4, #00ffd4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}
.saving-badge {
    display: inline-block;
    background: rgba(0,255,180,0.15);
    border: 1px solid rgba(0,255,180,0.3);
    border-radius: 20px;
    padding: 0.25rem 0.9rem;
    font-size: 0.72rem;
    color: #00ffb4;
    letter-spacing: 0.08em;
    margin-top: 0.75rem;
}

/* ── Feature table ── */
.feat-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.75rem;
    margin-top: 1rem;
}
.feat-table th {
    color: #6a8fa8;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 500;
    padding: 0.5rem 0.75rem;
    border-bottom: 1px solid rgba(0,180,255,0.15);
    text-align: left;
}
.feat-table td {
    padding: 0.55rem 0.75rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    color: #c0d8ee;
    font-family: 'JetBrains Mono', monospace;
}
.feat-table tr:hover td {
    background: rgba(0,180,255,0.04);
}
.feat-name { color: #7aadcc; font-size: 0.7rem; letter-spacing: 0.05em; }
.bar-wrap { background: rgba(255,255,255,0.06); border-radius: 4px; height: 5px; width: 100%; margin-top: 3px; }
.bar-fill { height: 5px; border-radius: 4px; background: linear-gradient(to right, #00b4ff, #00ffd4); }
.bar-fill-opt { background: linear-gradient(to right, #00ffb4, #00ffd4); }

/* ── Progress ── */
.stProgress > div > div > div > div {
    background: linear-gradient(to right, #00b4ff, #00ffd4) !important;
    border-radius: 4px !important;
}
[data-testid="stStatusWidget"] { display: none !important; }

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(0,180,255,0.1) !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #6a8fa8 !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: #00b4ff !important;
}

/* ── Info text ── */
.info-text {
    font-size: 0.72rem;
    color: #4a6a88;
    line-height: 1.7;
    margin-top: 0.5rem;
}

/* ── Divider ── */
.h-divider { border: none; border-top: 1px solid rgba(0,180,255,0.1); margin: 2rem 0; }

/* ── Success / Error ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Load Model ─────────────────────────────────────────────────────────────────
@st.cache_resource
def load_artifacts():
    model = pickle.load(open("results/catboost_best_model.pkl", "rb"))
    scaler = pickle.load(open("results/scaler.pkl", "rb"))
    return model, scaler

try:
    model, scaler = load_artifacts()
    model_loaded = True
except Exception as e:
    model_loaded = False
    load_error = str(e)

# ─── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div>
    <span class="hero-badge">❄ Particle Swarm · CatBoost</span>
    <div class="hero-title">Computer Engineering Department, FPNO</div>
    <div class="hero-sub">Smart Building Cooling Load Predictor & Design Optimizer</div>
  </div>
</div>
""", unsafe_allow_html=True)

if not model_loaded:
    st.error(f"⚠️ Could not load model artifacts. Make sure `results/` folder exists.\n\n`{load_error}`")
    st.stop()

#  Layout: 3 columns
col_inputs, col_bounds, col_results = st.columns([1.1, 1.1, 1.0], gap="large")

FEATURE_META = {
    "X1": ("Relative Compactness", 0.62, 0.98, 0.75, "unitless"),
    "X2": ("Surface Area",         514.5, 808.5, 672.0, "m²"),
    "X3": ("Wall Area",            245.0, 416.5, 318.5, "m²"),
    "X4": ("Roof Area",            110.25, 220.5, 183.75, "m²"),
    "X5": ("Overall Height",       3.5, 7.0, 5.25, "m"),
    "X6": ("Orientation",          2, 5, None, "cardinal"),
    "X7": ("Glazing Area",         0.0, 0.4, 0.25, "ratio"),
    "X8": ("Glazing Distribution", 0, 5, None, "index"),
}

# Left Column: Building Design
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
    X8 = st.selectbox("Glazing Distribution (X8)",    [0, 1, 2, 3, 4, 5],
                       format_func=lambda v: {0:"None",1:"Uniform",2:"N",3:"E",4:"S",5:"W"}.get(v, str(v)) + f" ({v})")

    st.markdown('</div>', unsafe_allow_html=True)
    user_input = np.array([[X1, X2, X3, X4, X5, X6, X7, X8]])

# Middle Column: Optimization Bounds
with col_bounds:
    st.markdown('<div class="section-label">🎯 Optimization Bounds</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<p class="info-text">Define the search space for PSO. Tighter bounds = faster convergence. Wider bounds = more exploration.</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    X1_r = st.slider("Relative Compactness",  0.62, 0.98, (0.62, 0.98), step=0.01)
    X2_r = st.slider("Surface Area (m²)",     514.5, 808.5, (514.5, 808.5))
    X3_r = st.slider("Wall Area (m²)",        245.0, 416.5, (245.0, 416.5))
    X4_r = st.slider("Roof Area (m²)",        110.25, 220.5, (110.25, 220.5))
    X5_r = st.slider("Overall Height (m)",    3.5, 7.0, (3.5, 7.0), step=0.25)
    X6_r = st.slider("Orientation",           2, 5, (2, 5))
    X7_r = st.slider("Glazing Area ratio",    0.0, 0.4, (0.0, 0.4), step=0.05)
    X8_r = st.slider("Glazing Distribution",  0, 5, (0, 5))

    st.markdown('</div>', unsafe_allow_html=True)

# Right Column: Results
with col_results:
    st.markdown('<div class="section-label">⚡ Results</div>', unsafe_allow_html=True)

    # Single Action Button
    run_btn = st.button("❄  Predict & Optimize", use_container_width=True)

    if run_btn:
        user_scaled = scaler.transform(user_input)
        pred = model.predict(user_scaled)[0]
        st.session_state["pred"] = pred
        st.session_state["user_input"] = user_input

        # PSO
        lb_raw = np.array([[X1_r[0], X2_r[0], X3_r[0], X4_r[0], X5_r[0], X6_r[0], X7_r[0], X8_r[0]]])
        ub_raw = np.array([[X1_r[1], X2_r[1], X3_r[1], X4_r[1], X5_r[1], X6_r[1], X7_r[1], X8_r[1]]])
        lb = scaler.transform(lb_raw)[0]
        ub = scaler.transform(ub_raw)[0]

        def objective(x):
            return model.predict(np.array(x).reshape(1, -1))[0]

        progress_ph = st.empty()
        with progress_ph.container():
            st.markdown('<p class="info-text" style="text-align:center;margin-top:.5rem">Running PSO — 30 particles · 50 iterations</p>', unsafe_allow_html=True)
            prog = st.progress(0)
            for i in range(1, 51):
                prog.progress(i / 50)
                time.sleep(0.01)

        best_x_s, best_y = pso(objective, lb, ub, swarmsize=30, maxiter=50, debug=False)
        best_x = scaler.inverse_transform(best_x_s.reshape(1, -1))[0]
        best_x[5] = round(best_x[5])
        best_x[7] = round(best_x[7])

        st.session_state["opt_y"] = best_y
        st.session_state["opt_x"] = best_x
        progress_ph.empty()

    # Display Results
    if "pred" in st.session_state:
        pred = st.session_state["pred"]
        st.markdown(f"""
        <div class="result-primary">
            <div class="result-label">Predicted Cooling Load</div>
            <div class="result-value">{pred:.2f}</div>
            <div class="result-unit">kWh / m²</div>
        </div>
        """, unsafe_allow_html=True)

    if "opt_y" in st.session_state:
        opt_y = st.session_state["opt_y"]
        opt_x = st.session_state["opt_x"]
        pred  = st.session_state["pred"]
        saving = pred - opt_y
        pct    = (saving / pred * 100) if pred else 0

        st.markdown(f"""
        <div class="opt-card">
            <div class="result-label" style="color:#4aaa88">Optimized Minimum</div>
            <div class="opt-value">{opt_y:.2f}</div>
            <div class="result-unit" style="color:#00ffb4">kWh / m²</div>
            <div class="saving-badge">▼ {saving:.2f} saved · {pct:.1f}% reduction</div>
        </div>
        """, unsafe_allow_html=True)

        # Feature comparison table
        names  = ["X1 · Compactness","X2 · Surface","X3 · Wall","X4 · Roof","X5 · Height","X6 · Orient","X7 · Glazing","X8 · GlazDist"]
        orig   = st.session_state["user_input"][0]
        mins_  = [X1_r[0],X2_r[0],X3_r[0],X4_r[0],X5_r[0],X6_r[0],X7_r[0],X8_r[0]]
        maxs_  = [X1_r[1],X2_r[1],X3_r[1],X4_r[1],X5_r[1],X6_r[1],X7_r[1],X8_r[1]]

        rows = ""
        for i, (n, o, op) in enumerate(zip(names, orig, opt_x)):
            lo, hi = mins_[i], maxs_[i]
            rng = max(hi - lo, 1e-9)
            w_o  = max(0, min(100, int((o  - lo) / rng * 100)))
            w_op = max(0, min(100, int((op - lo) / rng * 100)))
            fmt  = ".0f" if i in (5,7) else ".3f" if i in (0,6) else ".2f"
            rows += f"""
            <tr>
              <td class="feat-name">{n}</td>
              <td>{o:{fmt}}<div class="bar-wrap"><div class="bar-fill" style="width:{w_o}%"></div></div></td>
              <td>{op:{fmt}}<div class="bar-wrap"><div class="bar-fill bar-fill-opt" style="width:{w_op}%"></div></div></td>
            </tr>"""

        st.markdown(f"""
        <table class="feat-table">
          <thead><tr>
            <th>Feature</th>
            <th style="color:#00b4ff">Current</th>
            <th style="color:#00ffb4">Optimal</th>
          </tr></thead>
          <tbody>{rows}</tbody>
        </table>
        """, unsafe_allow_html=True)

    elif "pred" not in st.session_state:
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem;color:#2a4a62;">
            <div style="font-size:2.5rem;margin-bottom:1rem">❄</div>
            <div style="font-family:'Syne',sans-serif;font-size:0.85rem;letter-spacing:0.1em;text-transform:uppercase">
                Press the button to predict<br>& optimize your design
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown('<hr class="h-divider">', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<p class="info-text">Model · CatBoost Regressor</p>', unsafe_allow_html=True)
with c2:
    st.markdown('<p class="info-text" style="text-align:center">Optimizer · Particle Swarm (PSO)<br>30 particles · 50 iterations</p>', unsafe_allow_html=True)
with c3:
    st.markdown('<p class="info-text" style="text-align:right">Dataset · UCI Energy Efficiency</p>', unsafe_allow_html=True)