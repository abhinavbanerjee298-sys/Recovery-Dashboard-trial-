# recovery_dashboard.py
import math
import numpy as np
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Sleep → Recovery | Game Mode (High-Contrast)", layout="wide", page_icon="🎮")

# ===== Sidebar toggles first (so we can theme based on them) =====
with st.sidebar:
    st.subheader("🎛️ Display & Game Settings")
    high_contrast = st.toggle("High contrast mode (WCAG-friendly)", value=True)
    confetti_on = st.toggle("Confetti for milestones", value=True)
    streak_days = st.number_input("🔥 Streak (days)", min_value=0, max_value=365, value=0, step=1)
    show_debug = st.checkbox("Show math internals", value=False)
    st.markdown("---")
    continuity_mode = st.radio("Continuity input", ["Wake count", "WASO minutes"], index=0)

# ===== THEME / CSS (contrast-safe) =====
if high_contrast:
    # Color-blind & WCAG-conscious palette
    bg_grad = "linear-gradient(135deg, #0b0f1a 0%, #0a0e17 100%)"
    text_primary = "#f8fafc"     # near-white
    text_secondary = "#cbd5e1"   # slate-300
    card_bg = "rgba(255,255,255,0.08)"
    chip_bg  = "rgba(255,255,255,0.14)"
    border_faint = "rgba(255,255,255,0.18)"
    track_bg = "#0f172a"         # very dark slate
    track_muted = "#111827"      # donut track
    good = "#22c55e"             # green-500 (bright)
    mid  = "#f59e0b"             # amber-500 (bright)
    bad  = "#ef4444"             # red-500 (bright)
    accent = "#a78bfa"           # violet-400
    accent2 = "#06b6d4"          # cyan-400
    accent3 = "#60a5fa"          # blue-400
else:
    # Original-ish but still improved contrasts
    bg_grad = "linear-gradient(135deg, #111827 0%, #0b1220 100%)"
    text_primary = "#e5e7eb"
    text_secondary = "#cbd5e1"
    card_bg = "rgba(255,255,255,0.06)"
    chip_bg  = "rgba(255,255,255,0.10)"
    border_faint = "rgba(255,255,255,0.12)"
    track_bg = "#0f172a"
    track_muted = "#1f2937"
    good = "#22c55e"
    mid  = "#f59e0b"
    bad  = "#ef4444"
    accent = "#8b5cf6"
    accent2 = "#06b6d4"
    accent3 = "#22c55e"

st.markdown(f"""
<style>
:root{{
  --bg1: {bg_grad};
  --text: {text_primary};
  --text2: {text_secondary};
  --card: {card_bg};
  --chip: {chip_bg};
  --border: {border_faint};
  --track: {track_bg};
  --muted: {track_muted};
  --good: {good};
  --mid: {mid};
  --bad: {bad};
  --accent: {accent};
  --accent2: {accent2};
  --accent3: {accent3};
}}
html, body, [data-testid="stAppViewContainer"]{{
  background: var(--bg1);
  color: var(--text);
}}
h1, h2, h3, h4, label, .stSlider label, .stSelectbox label, .stRadio label, .stNumberInput label {{
  color: var(--text);
}}
.block-container{{ padding-top: 1.1rem; }}

.header{{
  background:
    radial-gradient(900px 260px at 20% -10%, color-mix(in oklab, var(--accent) 25%, transparent), transparent),
    radial-gradient(900px 240px at 90% -15%, color-mix(in oklab, var(--accent3) 25%, transparent), transparent);
  border-radius: 18px; padding: 14px 16px; border: 1px solid var(--border);
}}
.small{{ font-size: 12.5px; color: var(--text2); }}

.neon-card{{
  background: var(--card); border: 1px solid var(--border);
  border-radius: 16px; padding: 14px 16px;
  box-shadow: 0 10px 24px rgba(0,0,0,0.28), inset 0 0 0 1px rgba(255,255,255,0.04);
}}

.badge{{
  display:inline-block; padding:6px 10px; border-radius:999px; font-weight:800;
  background: color-mix(in oklab, var(--accent) 16%, transparent);
  color: #ffffff; border:1px solid var(--border); margin-right:8px; margin-bottom:6px;
}}

.chip{{
  display:inline-block; padding:6px 10px; border-radius:999px; font-weight:700; color:#ffffff;
  border:1px solid rgba(0,0,0,0.2); margin:4px 6px 0 0;
}}
.chip.ok  {{ background: var(--good); }}
.chip.warn{{ background: var(--mid);  }}
.chip.crit{{ background: var(--bad);  }}

.donut-wrap{{ display:flex; align-items:center; justify-content:center; }}
.donut{{
  --size: 180px; width: var(--size); height: var(--size); border-radius:50%;
  background: conic-gradient(var(--arc) var(--val), var(--muted) 0deg);
  display:grid; place-items:center;
  box-shadow: inset 0 0 0 10px var(--track), 0 10px 20px rgba(0,0,0,0.35);
}}
.donut > div{{ text-align:center; }}
.donut .big{{ font-size: 30px; font-weight: 900; color:#ffffff; text-shadow: 0 1px 2px rgba(0,0,0,0.9); }}
.donut .label{{ font-size: 14px; color: var(--text2); }}

.rule{{ height:10px; border-radius:6px; background: var(--track); overflow:hidden; }}
.rule > div{{ height:100%; border-radius:6px; }}

.quest{{
  display:flex; align-items:center; gap:12px;
  background: var(--card); padding:10px 12px; border-radius:14px;
  border:1px solid var(--border); color: var(--text);
}}
.quest .title{{ font-weight:800; color: var(--text); }}
.quest .small{{ color: var(--text2); }}

[data-baseweb="slider"] .rc-slider-track{{ background-color: var(--accent2) !important; }}
[data-baseweb="slider"] .rc-slider-handle{{ border-color: var(--accent2) !important; }}
</style>
""", unsafe_allow_html=True)

# ===== Header =====
st.markdown(f"""
<div class="header">
  <h1>🎮 Sleep → Recovery: <span style="color:var(--accent)">Game Mode</span></h1>
  <div class="small">Science-backed CRI & MRI with high-contrast UI, levels, XP, and quests. {datetime.now().strftime("%b %d, %Y")}</div>
  <div style="margin-top:10px;">
    <span class="badge">⚗️ Science framework locked</span>
    <span class="badge">🧠 CRI</span>
    <span class="badge">💪 MRI</span>
    <span class="badge">🏆 Badges</span>
    <span class="badge">🔥 Streaks</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ===== Inputs =====
sleep_col, env_col = st.columns(2)
with sleep_col:
    st.markdown("#### 😴 Sleep")
    TST = st.slider("Average total sleep (h)", 4.0, 10.0, 7.8, 0.1)
    SWS = st.slider("Average deep sleep (SWS, h)", 0.3, 3.0, 1.6, 0.1)
    REM = st.slider("Average REM (h)", 0.3, 3.0, 1.8, 0.1)
    if continuity_mode == "WASO minutes":
        WASO_min = st.slider("WASO (min/night)", 0, 180, 35, 5)
        wake_count = None
    else:
        wake_count = st.slider("Awakenings/night", 0, 6, 1, 1)
        WASO_min = None
    BT_SD = st.slider("Bedtime variability (SD, h)", 0.0, 3.0, 0.6, 0.05)
    WU_SD = st.slider("Wake-time variability (SD, h)", 0.0, 3.0, 0.7, 0.05)
    SleepScore = st.slider("Noise Sleep Score (/100)", 0, 100, 82, 1)

with env_col:
    st.markdown("#### 🏠 Environment & Habits")
    Temp = st.slider("Bedroom temperature (°C)", 15, 30, 23)
    RH = st.slider("Bedroom humidity (%)", 20, 80, 50)
    Screens = st.slider("Screen time after 9 PM (h)", 0.0, 4.0, 0.8, 0.1)
    LastMeal_h = st.slider("Last meal (h before bed)", 0.0, 5.0, 2.0, 0.25)
    earplugs = st.selectbox("Earplugs worn", [0,1,2], index=0, format_func=lambda x: f"{x} earplug(s)")

# ===== Science-backed math (unchanged) =====
def clamp(x, lo, hi): return max(lo, min(hi, x))
def f_qty(TST):
    val = math.exp(-0.5 * ((TST - 8.0)/1.0)**2)
    return clamp(val, 0.4, 1.0)
def f_sws(SWS): return clamp(SWS / 1.6, 0.2, 1.15)
def f_rem(REM): return clamp(REM / 1.8, 0.2, 1.10)
def f_cont(WASO_min, wake_count):
    if WASO_min is not None:
        return 1.0 - min(WASO_min, 90)/300.0
    else:
        return 1.0 - min(wake_count, 5)*0.06
def f_reg(BT_SD, WU_SD):
    base = math.exp(-((BT_SD/1.0)**2 + (WU_SD/1.0)**2)/2.0)
    return max(0.5, base)
def pen_screens(Screens): return 1.0 - min(Screens, 3.0)*0.04
def bonus_temp(Temp): return 1.05 if 20 <= Temp <= 25 else 1.00
def bonus_rh(RH): return 1.03 if 40 <= RH <= 60 else 1.00
def bonus_ear(earplugs): return 1.02 if earplugs >= 1 else 1.00
def bonus_meal(LastMeal_h): return 1.02 if LastMeal_h >= 2 else 0.99
def scaled_watch(SleepScore): return 0.5 + 0.5*(SleepScore/100.0)

fq = f_qty(TST); fsws = f_sws(SWS); frem = f_rem(REM)
fcont = f_cont(WASO_min, wake_count); freg = f_reg(BT_SD, WU_SD)

gm_cog = (fq**0.30) * (frem**0.25) * (fsws**0.15) * (fcont**0.15) * (freg**0.15)
CRI_raw = gm_cog * pen_screens(Screens) * bonus_temp(Temp) * bonus_rh(RH) * bonus_meal(LastMeal_h)

gm_musc = (fq**0.35) * (fsws**0.25) * (frem**0.10) * (fcont**0.15) * (freg**0.15)
MRI_raw = gm_musc * pen_screens(Screens) * bonus_temp(Temp) * bonus_rh(RH) * bonus_ear(earplugs) * bonus_meal(LastMeal_h)

def soft_cap(raw, watch_scaled):
    raw = clamp(raw, 0, 1.5)
    watch_scaled = clamp(watch_scaled, 0.5, 1.0)
    return 2.0 / (1.0/max(raw,1e-9) + 1.0/max(watch_scaled,1e-9))

CRI = round(clamp(soft_cap(CRI_raw, scaled_watch(SleepScore)), 0, 1.0) * 100, 1)
MRI = round(clamp(soft_cap(MRI_raw, scaled_watch(SleepScore)), 0, 1.0) * 100, 1)
Overall = round((CRI*0.45 + MRI*0.55), 1)

def tier(score):
    if score >= 92: return "Diamond", "💎", "#67e8f9"
    if score >= 85: return "Platinum", "🥇", "#60a5fa"
    if score >= 78: return "Gold", "🏆", "#facc15"
    if score >= 68: return "Silver", "🥈", "#a3a3a3"
    return "Bronze", "🥉", "#f97316"

tierCRI, iconCRI, colCRI = tier(CRI)
tierMRI, iconMRI, colMRI = tier(MRI)
tierOVR, iconOVR, colOVR = tier(Overall)

def donut(label, value, color, subtitle):
    val = max(0.0, min(100.0, value))
    st.markdown(f"""
    <div class="neon-card">
      <div class="donut-wrap">
        <div class="donut" style="--val:{val*3.6}deg; --arc:{color};">
          <div>
            <div class="big">{val:.1f}%</div>
            <div class="label">{label}</div>
            <div class="small">{subtitle}</div>
          </div>
        </div>
      </div>
      <div class="rule" style="margin-top:12px;">
        <div style="width:{val}%; background:{color};"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("### 🧪 Your Weekly Recovery (High-Contrast HUD)")
g1, g2, g3 = st.columns(3)
with g1: donut("🧠 CRI", CRI, colCRI, f"{iconCRI} {tierCRI}")
with g2: donut("💪 MRI", MRI, colMRI, f"{iconMRI} {tierMRI}")
with g3: donut("⚡ Overall", Overall, colOVR, f"{iconOVR} {tierOVR}")

if confetti_on and (CRI >= 90 or MRI >= 90 or Overall >= 90):
    st.balloons()

# ===== Chips: What helped/hurt (SOLID backgrounds + white text) =====
helped, hurt = [], []
def chip(lbl, cls): return f'<span class="chip {cls}">{lbl}</span>'

if 7.5 <= TST <= 8.5: helped.append("8h-ish total sleep")
else: hurt.append(("Total sleep off target", "warn"))
if SWS >= 1.5: helped.append("SWS ≥ 1.5h")
else: hurt.append(("Low deep sleep", "warn"))
if REM >= 1.6: helped.append("Good REM")
else: hurt.append(("REM could improve", "warn"))
if (WASO_min is not None and WASO_min <= 45) or (wake_count is not None and wake_count <= 2):
    helped.append("Low fragmentation")
else:
    hurt.append(("Fragmented sleep", "crit"))
if BT_SD <= 0.8 and WU_SD <= 0.8: helped.append("Regular schedule")
else: hurt.append(("Irregular schedule", "crit"))
if 20 <= Temp <= 25: helped.append("Comfortable temp")
else: hurt.append(("Room temp suboptimal", "warn"))
if 40 <= RH <= 60: helped.append("Humidity on point")
else: hurt.append(("Humidity off-range", "warn"))
if Screens <= 1.0: helped.append("Low late screens")
else: hurt.append(("Late screens high", "warn"))
if LastMeal_h >= 2: helped.append("Sensible meal timing")
else: hurt.append(("Late/heavy meal?", "warn"))

st.markdown("### 🎯 What boosted you")
st.markdown('<div class="neon-card">' + " ".join([chip(h, "ok") for h in helped]) + "</div>", unsafe_allow_html=True)

st.markdown("### 🧨 What dragged you")
st.markdown('<div class="neon-card">' + " ".join([chip(h[0], h[1]) for h in hurt]) + "</div>", unsafe_allow_html=True)

# ===== Quests (unchanged, now higher contrast text) =====
st.markdown("### 🗺️ Quests (earn XP)")
qcol1, qcol2 = st.columns(2)
with qcol1:
    st.markdown(f"""
    <div class="quest">
      <div>🌙</div>
      <div><div class="title">Bed/Wake within ±60 min</div>
      <div class="small">Keep BT_SD & WU_SD ≤ 1.0 h this week</div></div>
    </div>""", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="quest" style="margin-top:10px;">
      <div>📵</div>
      <div><div class="title">Screens ≤ 45 min after 9 PM</div>
      <div class="small">Helps REM & continuity</div></div>
    </div>""", unsafe_allow_html=True)
with qcol2:
    st.markdown(f"""
    <div class="quest">
      <div>❄️</div>
      <div><div class="title">Cool, comfy nights</div>
      <div class="small">Keep 20–25°C and 40–60% RH</div></div>
    </div>""", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="quest" style="margin-top:10px;">
      <div>🍽️</div>
      <div><div class="title">Last meal ≥ 2h before bed</div>
      <div class="small">Small, consistent bonus</div></div>
    </div>""", unsafe_allow_html=True)

# ===== XP / Levels =====
def xp_from_scores(CRI, MRI, streak_days):
    base = (max(0, CRI-60) + max(0, MRI-60)) * 0.8
    streak_bonus = min(streak_days, 30) * 2.5
    quest_bonus = 0
    if BT_SD <= 1.0 and WU_SD <= 1.0: quest_bonus += 10
    if Screens <= 0.75: quest_bonus += 10
    if 20 <= Temp <= 25 and 40 <= RH <= 60: quest_bonus += 10
    if LastMeal_h >= 2: quest_bonus += 5
    return int(base + streak_bonus + quest_bonus)

XP = xp_from_scores(CRI, MRI, streak_days)

def level_from_xp(xp):
    if xp >= 180: return "Level 5 — Apex Sleeper", "🦾"
    if xp >= 130: return "Level 4 — Circadian Ninja", "🥷"
    if xp >= 90:  return "Level 3 — Rhythm Rider", "🏄"
    if xp >= 60:  return "Level 2 — Consistency Champ", "🏅"
    return "Level 1 — Sleep Explorer", "🧭"

lvl_label, lvl_icon = level_from_xp(XP)

st.markdown("### 🧩 Progress & Rewards")
p1, p2, p3 = st.columns([1,1,1])
st.markdown(
    f'<div class="neon-card"><div style="font-weight:800;">{lvl_icon} {lvl_label}</div>'
    f'<div class="small">XP this week: <b style="color:#fff">{XP}</b></div></div>',
    unsafe_allow_html=True)
st.markdown(
    f'<div class="neon-card"><div style="font-weight:800;">🔥 Streak</div>'
    f'<div class="small">{streak_days} day(s)</div></div>',
    unsafe_allow_html=True)
nxt = "Hit Overall ≥ 90% to push a tier!" if Overall < 90 else "You’re at the top. Maintain!"
st.markdown(
    f'<div class="neon-card"><div style="font-weight:800;">🏆 Tier Hint</div>'
    f'<div class="small">{nxt}</div></div>',
    unsafe_allow_html=True)

# ===== Debug =====
if show_debug:
    st.markdown("### 🧮 Internals")
    st.write({
        "f_qty": round(fq,3), "f_sws": round(fsws,3), "f_rem": round(frem,3),
        "f_cont": round(fcont,3), "f_reg": round(freg,3),
        "pen_screens": round(pen_screens(Screens),3),
        "bonus_temp": round(bonus_temp(Temp),3),
        "bonus_rh": round(bonus_rh(RH),3),
        "bonus_ear": round(bonus_ear(earplugs),3),
        "bonus_meal": round(bonus_meal(LastMeal_h),3),
        "CRI_raw": round(CRI_raw,3), "MRI_raw": round(MRI_raw,3),
        "CRI": CRI, "MRI": MRI, "Overall": Overall,
        "WatchScaled": round(scaled_watch(SleepScore),3)
    })

st.caption("High-contrast colors applied. If anything is still hard to read on your display, toggle High contrast mode in the sidebar.")
