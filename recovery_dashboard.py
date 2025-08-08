st.markdown("""
<style>
:root{
  /* Base palette */
  --bg1: linear-gradient(135deg, #0d1117 0%, #0a0f1a 100%);
  --text: #f8fafc;           /* Near-white main text */
  --text-dim: #cbd5e1;       /* Secondary text */
  --text-dimmer: #94a3b8;    /* Tertiary */
  --card: rgba(255,255,255,0.12);  /* More opaque than before */
  --card-border: rgba(255,255,255,0.18);
  --chip: rgba(255,255,255,0.14);
  --chip-border: rgba(255,255,255,0.28);

  /* Accents */
  --good: #10b981;
  --mid:  #f59e0b;
  --bad:  #ef4444;
  --accent:  #8b5cf6;
  --accent2: #06b6d4;
  --accent3: #22c55e;

  /* Gauges & rails */
  --rail: #273042;           /* darker rail for contrast */
  --donut-inner: #111827;    /* inner donut background */
  --donut-shadow: rgba(0,0,0,0.45);
}

/* App background & global text */
html, body, [data-testid="stAppViewContainer"]{
  background: var(--bg1);
  color: var(--text);
}
h1, h2, h3, h4, h5, h6 { color: var(--text); }
p, span, label, div { color: var(--text-dim); }

/* Streamlit widget label & help text contrast */
[data-baseweb="input"] label,
[data-baseweb="slider"] label,
[data-baseweb="select"] label,
.css-10trblm, .stSlider label, .stSelectbox label, .stNumberInput label {
  color: var(--text) !important;
}
.small { color: var(--text-dimmer); }

/* Links */
a, a:visited { color: #7dd3fc; }
a:hover { color: #bae6fd; }

/* Cards / header */
.neon-card{
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: 18px;
  padding: 16px 18px;
  box-shadow: 0 10px 28px var(--donut-shadow), inset 0 0 0 1px rgba(255,255,255,0.06);
  color: var(--text);
}
.header{
  background:
    radial-gradient(900px 260px at 20% -10%, rgba(139,92,246,0.35), transparent),
    radial-gradient(900px 260px at 90% -15%, rgba(34,197,94,0.28), transparent);
  border-radius: 20px;
  padding: 16px 18px;
  border: 1px solid var(--card-border);
}

/* Badges & chips (more readable) */
.badge{
  display:inline-block; padding:6px 10px; border-radius:999px; font-weight:700;
  background: rgba(255,255,255,0.14);
  border:1px solid var(--chip-border);
  color: var(--text);
  margin-right:8px; margin-bottom:6px;
}
.chip{
  display:inline-block; padding:7px 12px; border-radius:999px; font-weight:700;
  background: var(--chip);
  border:1px solid var(--chip-border);
  color: var(--text);
  margin:6px 8px 0 0;
}
.ok   { box-shadow: inset 0 0 0 2px rgba(16,185,129,0.35); }
.warn { box-shadow: inset 0 0 0 2px rgba(245,158,11,0.35); }
.crit { box-shadow: inset 0 0 0 2px rgba(239,68,68,0.35); }

/* Donut gauges: crisper text and backgrounds */
.donut-wrap{ display:flex; align-items:center; justify-content:center; }
.donut{
  --size: 180px; width: var(--size); height: var(--size); border-radius:50%;
  background: conic-gradient(var(--arc) var(--val), #1f2735 0deg);
  display:grid; place-items:center;
  box-shadow: 0 0 0 10px var(--donut-inner) inset, 0 10px 24px var(--donut-shadow);
}
.donut > div{ text-align:center; }
.donut .big{
  font-size: 32px; font-weight: 900; letter-spacing: 0.2px;
  color: var(--text);           /* force bright white number */
  text-shadow: 0 0 12px rgba(255,255,255,0.12);
}
.donut .label{ font-size: 15px; color: var(--text); opacity:0.95; }
.rule{ height:12px; border-radius:6px; background: var(--rail); overflow:hidden; }
.rule > div{ height:100%; border-radius:6px; }

/* Streamlit slider track/handle contrast */
.stSlider [data-baseweb="slider"] > div > div {
  background: var(--rail) !important;
}
.stSlider [data-baseweb="slider"] > div > div > div {
  background: linear-gradient(90deg, var(--accent2), var(--accent)) !important;
}
.stSlider [role="slider"]{
  border: 2px solid rgba(255,255,255,0.55) !important;
  box-shadow: 0 0 0 4px rgba(139,92,246,0.25) !important;
}

/* Selects / inputs */
.stSelectbox div, .stNumberInput div, .stTextInput div {
  color: var(--text) !important;
}

/* Expanders (if you use them later) */
.streamlit-expanderHeader { color: var(--text) !important; }

/* Tables (future-proof) */
tbody, th, td { color: var(--text) !important; }

/* Buttons */
.stButton>button{
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  color: #0b1020; font-weight: 800; border: 0; border-radius: 10px;
}
.stButton>button:hover{ filter: brightness(1.1); }

/* Make metric labels readable if used */
.css-1ht1j8u, .css-1xarl3l { color: var(--text) !important; }
</style>
""", unsafe_allow_html=True)
