# recovery_dashboard.py
import math
import numpy as np
import streamlit as st
from datetime import datetime

# =========================================
# Page config + Theme
# =========================================
st.set_page_config(page_title="Sleep → Recovery | Game Mode", layout="wide", page_icon="🎮")

# Custom CSS for neon cards, gradients, chips, and animated donut gauges
st.markdown("""
<style>
:root{
  --bg1: linear-gradient(135deg, #111827 0%, #0b1220 100%);
  --card: rgba(255,255,255,0.06);
  --chip: rgba(255,255,255,0.10);
  --good: #10b981;
  --mid: #f59e0b;
  --bad: #ef4444;
  --accent: #8b5cf6;
  --accent2: #06b6d4;
  --accent3: #22c55e;
}
html, body, [data-testid="stAppViewContainer"]{
  background: var(--bg1);
  color: #e5e7eb;
}
h1, h2, h3, h4 { color: #f3f4f6; }
.block-container{ padding-top: 1.2rem; }
.neon-card{
  background: var(--card);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 18px;
  padding: 16px 18px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.25), inset 0 0 0 1px rgba(255,255,255,0.04);
}
.header{
  background: radial-gradient(1000px 300px at 20% -10%, rgba(139,92,246,0.25), transparent),
              radial-gradient(900px 280px at 90% -15%, rgba(34,197,94,0.20), transparent);
  border-radius: 20px;
  padding: 16px 18px;
  border: 1px solid rgba(255,255,255,0.08);
}
.badge{
  display:inline-block; padding:6px 10px; border-radius:999px; font-weight:700;
  background: linear-gradient(135deg, rgba(255,255,255,0.10), rgba(255,255,255,0.05));
  border:1px solid rgba(255,255,255,0.10); margin-right:8px; margin-bottom:4px;
}
.chip{ display:inline-block; padding:6px 10px; border-radius:999px; font-weight:600;
  background: var(--chip); border:1px solid rgba(255,255,255,0.08); margin:4px 6px 0 0; }
.ok   { color: var(--good);  border-color: rgba(16,185,129,0.35); }
.warn { color: var(--mid);   border-color: rgba(245,158,11,0.35); }
.crit { color: var(--bad);   border-color: rgba(239,68,68,0.35); }

.donut-wrap{ display:flex; align-items:center; justify-content:center; }
.donut{
  --size: 170px; width: var(--size); height: var(--size); border-radius:50%;
  background:
    conic-gradient(var(--arc) var(--val), #2b2f3a 0deg);
  display:grid; place-items:center;
  box-shadow: 0 0 0 10px #0f172a inset, 0 10px 22px rgba(0,0,0,0.35);
}
.donut > div{ text-align:center; }
.donut .big{ font-size: 30px; font-weight: 800; }
.donut .label{ font-size: 14px; opacity:0.85; }
.rule{ height:10px; border-radius:6px; background:#212633; overflow:hidden; }
.rule > div{ height:100%; border-radius:6px; }

.quest{
  display:flex; align-items:center; gap:12px;
  background: var(--card); padding:10px 12px; border-radius:14px;
  border:1px solid rgba(255,255,255,0.08);
}
.quest .title{ font-weight:700; }
.small{ font-size: 12px; opacity: 0.8; }
</style>
""", unsafe_allow_html=True)

# =========================================
# Header
# =========================================
st.markdown(f"""
<div class="header">
  <h1>🎮 Sleep → Recovery: <span style="color:#a78bfa">Game Mode</span></h1>
  <div class="small">Science-backed CRI & MRI with levels, XP, quests, and juicy visuals. {datetime.now().strftime("%b %d, %Y")}</div>
  <div style="margin-top:10px;">
    <span class="badge">⚗️ Science framework locked</span>
    <span class="badge">🧠 CRI</span>
    <span class="badge">💪 MRI</span>
    <span class="badge">🏆 Badges</span>
    <span class="badge">🔥 Streaks</span>
  </div>
</div>
""", unsafe_allow_html=True)

# =========================================
# Sidebar Game Toggles
# =========================================
with st.sidebar:
    st.subheader("🎛️ Game Settings")
    st.write("Tweak visuals & gamification. Formulas remain science-backed.")
    confetti_on = st.toggle("Confetti for milestones", value=True)
    streak_days = st.number_input("🔥 Streak (days)", min_value=0, max_value=365, value=0, step=1)
    show_debug = st.checkbox("Show math internals", value=False)

    st.markdown("—")
    continuity_mode = st.radio("Continuity input", ["Wake count", "WASO minutes"], index=0)

# =========================================
# Inputs
# =========================================
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

# =========================================
# Science-backed math (exactly as agreed)
# =========================================
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

fq = f_qty(TST)
fsws = f_sws(SWS)
frem = f_rem(REM)
fcont = f_cont(WASO_min, wake_count)
freg = f_reg(BT_SD, WU_SD)

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
Overall = round((CRI*0.45 + MRI*0.55), 1)  # slight bias to MRI for training adaptation

# =========================================
# Gamified classification
# =========================================
def tier(score):
    if score >= 92: return "Diamond", "💎", "#67e8f9"
    if score >= 85: return "Platinum", "🥇", "#60a5fa"
    if score >= 78: return "Gold", "🏆", "#facc15"
    if score >= 68: return "Silver", "🥈", "#a3a3a3"
    return "Bronze", "🥉", "#f97316"

tierCRI, iconCRI, colCRI = tier(CRI)
tierMRI, iconMRI, colMRI = tier(MRI)
tierOVR, iconOVR, colOVR = tier(Overall)

# =========================================
# Headline Gauges (CSS donut + color)
# =========================================
def donut(label, value, color, subtitle):
    val = max(0.0, min(100.0, value))
    st.markdown(f"""
    <div class="neon-card">
      <div class="donut-wrap">
        <div class="donut" style="--val:{val*3.6}deg; --arc:{color};">
          <div>
            <div class="big" style="color:{color}">{val:.1f}%</div>
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

st.markdown("### 🧪 Your Weekly Recovery (Game HUD)")
g1, g2, g3 = st.columns(3)
with g1: donut("🧠 CRI", CRI, colCRI, f"{iconCRI} {tierCRI}")
with g2: donut("💪 MRI", MRI, colMRI, f"{iconMRI} {tierMRI}")
with g3: donut("⚡ Overall", Overall, colOVR, f"{iconOVR} {tierOVR}")

# Celebrate milestones
if confetti_on and (CRI >= 90 or MRI >= 90 or Overall >= 90):
    st.balloons()

# =========================================
# Chips: What helped / What hurt
# =========================================
helped, hurt = [], []
def chipify(lbl, val, good=True):
    cls = "ok" if good else "crit" if val=="crit" else "warn"
    return f'<span class="chip {cls}">{lbl}</span>'

# Heuristics for chips
if 7.5 <= TST <= 8.5: helped.append("8h-ish total sleep")
else: hurt.append("Total sleep off target")
if SWS >= 1.5: helped.append("SWS ≥ 1.5h")
else: hurt.append("Low deep sleep")
if REM >= 1.6: helped.append("Good REM")
else: hurt.append("REM could improve")
if (WASO_min is not None and WASO_min <= 45) or (wake_count is not None and wake_count <= 2):
    helped.append("Low fragmentation")
else:
    hurt.append("Fragmented sleep")
if BT_SD <= 0.8 and WU_SD <= 0.8: helped.append("Regular schedule")
else: hurt.append("Irregular schedule")
if 20 <= Temp <= 25: helped.append("Comfortable temp")
else: hurt.append("Room temp suboptimal")
if 40 <= RH <= 60: helped.append("Humidity on point")
else: hurt.append("Humidity off-range")
if Screens <= 1.0: helped.append("Low late screens")
else: hurt.append("Late screens high")
if LastMeal_h >= 2: helped.append("Sensible meal timing")
else: hurt.append("Late/heavy meal?")

st.markdown("### 🎯 What boosted you")
st.markdown('<div class="neon-card">' + " ".join([chipify(h, "", True) for h in helped]) + "</div>", unsafe_allow_html=True)

st.markdown("### 🧨 What dragged you")
drag_chips = []
for h in hurt:
    severity = "crit" if any(k in h.lower() for k in ["off-range","fragmented","irregular","high"]) else "warn"
    drag_chips.append(chipify(h, severity, False))
st.markdown('<div class="neon-card">' + " ".join(drag_chips) + "</div>", unsafe_allow_html=True)

# =========================================
# Quests (mini-objectives for XP)
# =========================================
st.markdown("### 🗺️ Quests (earn XP)")
qcol1, qcol2 = st.columns(2)
with qcol1:
    st.markdown(f"""
    <div class="quest">
      <div>🌙</div>
      <div><div class="title">Bed/Wake within ±60 min</div>
      <div class="small">Keep BT_SD & WU_SD ≤ 1.0 h this week</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="quest" style="margin-top:10px;">
      <div>📵</div>
      <div><div class="title">Screens ≤ 45 min after 9 PM</div>
      <div class="small">Helps REM & continuity</div></div>
    </div>
    """, unsafe_allow_html=True)
with qcol2:
    st.markdown(f"""
    <div class="quest">
      <div>❄️</div>
      <div><div class="title">Cool, comfy nights</div>
      <div class="small">Keep 20–25°C and 40–60% RH</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="quest" style="margin-top:10px;">
      <div>🍽️</div>
      <div><div class="title">Last meal ≥ 2h before bed</div>
      <div class="small">Small, consistent bonus</div></div>
    </div>
    """, unsafe_allow_html=True)

# =========================================
# XP, Level, Streaks
# =========================================
def xp_from_scores(CRI, MRI, streak_days):
    base = (max(0, CRI-60) + max(0, MRI-60)) * 0.8     # scores above 60 give XP
    streak_bonus = min(streak_days, 30) * 2.5            # soft-cap at 30 days
    quest_bonus = 0
    # Passive quest detections:
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
with p1:
    st.markdown(f'<div class="neon-card"><div style="font-weight:700;">{lvl_icon} {lvl_label}</div><div class="small">XP this week: <b>{XP}</b></div></div>', unsafe_allow_html=True)
with p2:
    st.markdown(f'<div class="neon-card"><div style="font-weight:700;">🔥 Streak</div><div class="small">{streak_days} day(s)</div></div>', unsafe_allow_html=True)
with p3:
    # Show quick next-tier hint
    nxt = "Hit Overall ≥ 90% to push a tier!" if Overall < 90 else "You’re at the top. Maintain!"
    st.markdown(f'<div class="neon-card"><div style="font-weight:700;">🏆 Tier Hint</div><div class="small">{nxt}</div></div>', unsafe_allow_html=True)

# =========================================
# Debug / internals (optional)
# =========================================
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

st.caption("Visuals are playful; the math is the same research-based model we agreed on. Calibrated so ‘good’ weeks land ~78–92. Irregularity & fragmentation will drag scores into the 60s or below.")
