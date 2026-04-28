# ─────────────────────────────────────────────
#  app.py — Entry point
#  Run: streamlit run app.py
# ─────────────────────────────────────────────

import sys, os #Testing git = Commiting changes"

# Windows cp1252 fix — force UTF-8 output so emojis in HTML never crash
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import streamlit as st

st.set_page_config(
    page_title            = "Car Price Predictor 2026",
    page_icon             = "🚗",
    layout                = "wide",
    initial_sidebar_state = "expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1,h2,h3,h4 { font-family:'Syne',sans-serif !important; color:#e8eaf6 !important; }
[data-testid="stAppViewContainer"] { background:#0d1018; }
[data-testid="stHeader"] { background:transparent; }

/* ── SIDEBAR ── */
div[data-testid="stSidebar"] { background:#0a0d15 !important; border-right:1px solid #1e2535; }
div[data-testid="stSidebar"] * { color:#c0cfe0 !important; }
div[data-testid="stSidebar"] .stRadio label { font-size:0.92rem !important; padding:7px 0; cursor:pointer; }
div[data-testid="stSidebar"] .stRadio label:hover { color:#ffffff !important; }

/* ── ALL LABELS — HIGH CONTRAST ── */
label,
.stSelectbox label,
.stSlider label,
.stNumberInput label,
.stMultiSelect label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span {
    color:#d8e4f0 !important;
    font-size:0.88rem !important;
    font-weight:500 !important;
}

/* ── SELECTBOX ── */
.stSelectbox > div > div {
    background:#141929 !important;
    border:1px solid #3a4560 !important;
    border-radius:10px !important;
    color:#e8eaf6 !important;
}
div[data-baseweb="select"] > div { background:#141929 !important; border-color:#3a4560 !important; }
div[data-baseweb="select"] span  { color:#e8eaf6 !important; }
div[data-baseweb="popover"]      { background:#1a1f2e !important; }
div[data-baseweb="menu"]         { background:#1a1f2e !important; border:1px solid #3a4560 !important; }
div[data-baseweb="option"]       { background:#1a1f2e !important; color:#e8eaf6 !important; }
div[data-baseweb="option"]:hover { background:#2a3550 !important; }

/* ── SLIDER ── */
.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"] { color:#90a4ae !important; font-size:0.78rem !important; }
.stSlider output, .stSlider [data-testid="stThumbValue"] { color:#e8eaf6 !important; font-weight:600 !important; }
div[data-baseweb="slider"] [role="slider"] { background:#3f51b5 !important; border-color:#64b5f6 !important; }

/* ── NUMBER INPUT ── */
.stNumberInput input {
    background:#141929 !important; border:1px solid #3a4560 !important;
    border-radius:8px !important; color:#e8eaf6 !important; font-size:0.95rem !important;
}
.stNumberInput button { background:#1a1f2e !important; border-color:#3a4560 !important; color:#e8eaf6 !important; }

/* ── MULTISELECT ── */
.stMultiSelect > div > div { background:#141929 !important; border-color:#3a4560 !important; }
.stMultiSelect span { color:#e8eaf6 !important; }

/* ── MARKDOWN TEXT ── */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span { color:#c8d5e8 !important; }
[data-testid="stMarkdownContainer"] strong { color:#e8eaf6 !important; }
[data-testid="stMarkdownContainer"] code { color:#64b5f6 !important; background:#1a1f2e !important; }

/* ── HERO ── */
.hero-box {
    background:linear-gradient(135deg,#1a1f2e 0%,#141929 60%,#0f1420 100%);
    border:1px solid #2a3550; border-radius:24px;
    padding:2.4rem 3rem; margin-bottom:1.8rem;
    position:relative; overflow:hidden;
}
.hero-box::before {
    content:''; position:absolute; top:-80px; right:-80px;
    width:280px; height:280px;
    background:radial-gradient(circle,rgba(63,81,181,0.2) 0%,transparent 70%);
    border-radius:50%;
}
.hero-title { font-family:'Syne',sans-serif; font-size:2.6rem; font-weight:800; color:#e8eaf6; margin:0; line-height:1.1; }
.hero-sub   { color:#a0b4d0; font-size:1.05rem; margin-top:0.5rem; max-width:700px; }
.hero-badge { display:inline-block; background:rgba(63,81,181,0.2); border:1px solid #3f51b5;
              border-radius:20px; padding:3px 14px; font-size:0.72rem; color:#9ba8d0;
              letter-spacing:.1em; text-transform:uppercase; margin-bottom:0.8rem; }
.hero-stats { display:flex; gap:2rem; margin-top:1.4rem; }
.hero-stat  { text-align:center; }
.hero-stat-num   { font-family:'Syne',sans-serif; font-size:1.5rem; font-weight:700; color:#64b5f6; }
.hero-stat-label { font-size:0.7rem; color:#7a90a8; letter-spacing:.05em; text-transform:uppercase; }

/* ── SECTION HEAD ── */
.section-head {
    font-family:'Syne',sans-serif; font-size:1rem; font-weight:700;
    color:#c8d5e8; border-left:3px solid #3f51b5;
    padding-left:0.75rem; margin:1.8rem 0 1rem 0; letter-spacing:.01em;
}

/* ── SPEC LOCKED CARD ── */
.spec-locked {
    background:#0f1420; border:1px solid #2a3550; border-radius:12px;
    padding:0.8rem 1rem; margin-bottom:0.5rem;
}
.spec-locked-label {
    font-size:0.65rem; color:#7a90a8; text-transform:uppercase;
    letter-spacing:.09em; margin-bottom:4px;
}
.spec-locked-value {
    font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:700; color:#64b5f6;
}

/* ── INFO/WARN BOXES ── */
.info-box {
    background:rgba(63,81,181,0.1); border:1px solid rgba(63,81,181,0.3);
    border-radius:12px; padding:0.85rem 1.1rem;
    font-size:0.85rem; color:#b0c0d8; margin:0.6rem 0;
}
.info-box b { color:#9ba8d0; }
.warn-box {
    background:rgba(255,183,77,0.08); border:1px solid rgba(255,183,77,0.3);
    border-radius:12px; padding:0.85rem 1.1rem;
    font-size:0.85rem; color:#b0c0d8; margin:0.6rem 0;
}

/* ── RESULT CARD ── */
.result-wrapper {
    background:linear-gradient(145deg,#141929,#1a1f2e);
    border:1px solid #2a3550; border-radius:24px;
    padding:2.4rem 2rem; text-align:center;
}
.result-label  { font-size:0.72rem; color:#7a90a8; letter-spacing:.14em; text-transform:uppercase; }
.result-price  { font-family:'Syne',sans-serif; font-size:3.8rem; font-weight:800; color:#64b5f6; line-height:1.05; margin:0.3rem 0; }
.result-sub    { font-size:0.82rem; color:#7a90a8; margin-top:0.25rem; }
.result-band   { font-size:0.8rem; color:#9ba8d0; margin-top:0.6rem; }
.year-tag      { display:inline-block; background:rgba(100,181,246,0.12); border:1px solid rgba(100,181,246,0.3);
                 border-radius:20px; padding:3px 16px; font-size:0.72rem; color:#64b5f6; letter-spacing:.08em; margin-bottom:0.8rem; }
.segment-badge { display:inline-block; padding:4px 16px; border-radius:20px; font-size:0.78rem; font-weight:600; margin-top:0.6rem; }

/* ── INSIGHT CARDS ── */
.insight-row { display:flex; align-items:flex-start; gap:0.75rem; padding:0.75rem 1rem;
               border-radius:10px; margin-bottom:0.5rem; border:1px solid transparent; }
.insight-positive { background:rgba(129,199,132,0.08); border-color:rgba(129,199,132,0.25); }
.insight-negative { background:rgba(239,154,154,0.08); border-color:rgba(239,154,154,0.25); }
.insight-neutral  { background:rgba(100,181,246,0.07); border-color:rgba(100,181,246,0.18); }
.insight-icon  { font-size:1.1rem; margin-top:1px; }
.insight-text  { font-size:0.84rem; color:#b8c8d8; line-height:1.4; }
.insight-label { font-weight:600; color:#e8eaf6; font-size:0.86rem; }
.insight-pct   { font-size:0.7rem; color:#7a90a8; }

/* ── COMPARE CARDS ── */
.compare-winner { background:linear-gradient(135deg,rgba(129,199,132,0.12),rgba(129,199,132,0.04));
                  border:1px solid rgba(129,199,132,0.35); border-radius:14px; padding:1.2rem; text-align:center; }
.compare-loser  { background:#141929; border:1px solid #232b40; border-radius:14px; padding:1.2rem; text-align:center; }

/* ── BUTTONS ── */
.stButton > button {
    width:100%; background:linear-gradient(135deg,#3f51b5 0%,#1a237e 100%);
    color:#fff !important; border:none; border-radius:14px;
    padding:0.9rem 1rem; font-family:'Syne',sans-serif; font-size:1rem;
    font-weight:700; letter-spacing:.03em; cursor:pointer;
    transition:opacity .2s, transform .1s, box-shadow .2s;
    box-shadow:0 4px 24px rgba(63,81,181,0.35);
}
.stButton > button:hover  { opacity:0.9; transform:translateY(-2px); }
.stButton > button:active { transform:translateY(0); }
.stButton > button p { color:#fff !important; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] { background:#141929; border-radius:14px; padding:5px; gap:2px; }
.stTabs [data-baseweb="tab"]      { border-radius:10px; color:#90a4ae !important; font-family:'DM Sans'; padding:0.5rem 1rem; }
.stTabs [aria-selected="true"]    { background:#1a1f2e !important; color:#e8eaf6 !important; }
.stTabs [data-baseweb="tab"] p    { color:inherit !important; }

/* ── METRIC TILES ── */
div[data-testid="metric-container"] {
    background:#141929; border:1px solid #2a3550;
    border-radius:14px; padding:0.9rem 1.1rem;
}
div[data-testid="metric-container"] label { color:#90a4ae !important; font-size:0.72rem !important; text-transform:uppercase; letter-spacing:.05em; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color:#e8eaf6 !important; font-family:'Syne',sans-serif !important; font-size:1.3rem !important; }
div[data-testid="metric-container"] div[data-testid="stMetricDelta"] { color:#ef9a9a !important; }

/* ── EXPANDER ── */
.streamlit-expanderHeader { background:#141929 !important; border:1px solid #2a3550 !important; border-radius:10px !important; color:#c0d0e0 !important; }
[data-testid="stExpander"] summary p { color:#c0d0e0 !important; }

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] { border:1px solid #2a3550 !important; border-radius:12px; overflow:hidden; }
[data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th { color:#c8d5e8 !important; }

/* ── HR ── */
hr { border-color:#1e2535 !important; margin:1.4rem 0 !important; }

/* ── CAPTION ── */
.stCaption p { color:#607080 !important; }
</style>
""", unsafe_allow_html=True)

from utils.data_loader import load_car_lookup, load_raw_dataframe, load_model_artifacts
from components.hero    import render as render_hero
from components.sidebar import render as render_sidebar
from pages              import predict, visualization, compare, about

artifacts_ok = False
missing_msg  = ""
car_lookup   = {}

try:
    car_lookup = load_car_lookup()
    # load_model_artifacts auto-retrains if pkl version mismatches numpy/sklearn
    with st.spinner("⚙️ Loading model… (first run may retrain for your Python version)"):
        preprocessor, model = load_model_artifacts()
    df           = load_raw_dataframe()
    artifacts_ok = True
except FileNotFoundError as e:
    missing_msg = str(e)
except Exception as e:
    missing_msg = str(e)

page = render_sidebar(car_lookup, artifacts_ok, missing_msg)
render_hero()

if not artifacts_ok:
    st.markdown(f"""
<div style="background:rgba(239,83,80,0.08);border:1px solid rgba(239,83,80,0.35);
border-radius:16px;padding:1.6rem 2rem;margin:1rem 0;">
<div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;
color:#ef9a9a;margin-bottom:0.8rem;">⚠️ Could not load model files</div>
<div style="font-size:0.88rem;color:#c0c8d8;margin-bottom:1rem;">
The <code style="color:#64b5f6;background:#1a1f2e;padding:1px 6px;border-radius:4px;">.pkl</code>
files were saved with a different NumPy/scikit-learn version.<br>
<strong style="color:#e8eaf6;">Fix:</strong> Run the one-time retrain script below to regenerate them for your Python version.
</div>
<div style="background:#0f1420;border:1px solid #2a3550;border-radius:10px;
padding:0.9rem 1.2rem;font-family:monospace;font-size:0.88rem;color:#81c784;">
# Step 1 — install dependencies<br>
pip install -r requirements.txt<br><br>
# Step 2 — regenerate model files for YOUR Python/NumPy version<br>
python retrain_model.py<br><br>
# Step 3 — launch the app<br>
streamlit run app.py
</div>
<div style="font-size:0.78rem;color:#7a90a8;margin-top:0.8rem;">
Error detail: <code style="color:#ef9a9a;">{missing_msg}</code>
</div>
</div>
""", unsafe_allow_html=True)
    st.stop()

if page == "🔮  Predict Price":
    predict.render(car_lookup, preprocessor, model)
elif page == "🔀  Compare Cars":
    compare.render(car_lookup, preprocessor, model)
elif page == "📊  Visualizations":
    visualization.render(df)
elif page == "ℹ️  About":
    about.render()
