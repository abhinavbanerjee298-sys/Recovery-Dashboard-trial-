# recovery_dashboard.py
import math, streamlit as st
from datetime import datetime

# =========================
# Page config
# =========================
st.set_page_config(page_title="Hypertrophy Quest — Avatar Builder", layout="wide", page_icon="💪")

# =========================
# Session state
# =========================
def init_state():
    s = st.session_state
    if "step" not in s: s.step = 0
    # inputs
    defaults = dict(
        TST=7.8, SWS=1.6, REM=1.8, # REM is kept for biology but not shown in UI
        mode="Wake count", WASO=35, wakes=1,
        BT_SD=0.6, WU_SD=0.7,
        Temp=23, RH=50, Screens=0.8, LastMeal=2.0,
        Ear=0, SleepScore=82
    )
    for k,v in defaults.items():
        if k not in s: s[k] = v
    # cosmetic
    if "confetti" not in s: s.confetti = True
    if "name" not in s: s.name = "You"
init_state()

# =========================
# Math — science-backed MRI (no cognitive)
# =========================
def clamp(x, lo, hi): return max(lo, min(hi, x))

def f_qty(TST):
    # U-shape around 8h, σ≈1h; clamp so 6–10h isn't nuked
    from math import exp
    val = exp(-0.5 * ((TST - 8.0)/1.0)**2)
    return clamp(val, 0.4, 1.0)

def f_sws(SWS): return clamp(SWS/1.6, 0.2, 1.15)     # cap bonus +15%
def f_rem(REM): return clamp(REM/1.8, 0.2, 1.10)     # cap bonus +10% (small for MRI)

def f_cont(WASO, wakes, mode):
    if mode == "WASO minutes":
        return 1.0 - min(WASO, 90)/300.0  # 0–90 → 1.0→0.7
    else:
        return 1.0 - min(wakes, 5)*0.06   # 0–5 → 1.0→0.70

def f_reg(BT_SD, WU_SD):
    from math import exp
    base = exp(-((BT_SD/1.0)**2 + (WU_SD/1.0)**2)/2.0)
    return max(0.5, base)

def pen_screens(x): return 1.0 - min(x, 3.0)*0.04
def bonus_temp(t):  return 1.05 if 20 <= t <= 25 else 1.00
def bonus_rh(rh):  return 1.03 if 40 <= rh <= 60 else 1.00
def bonus_ear(n):  return 1.02 if n >= 1 else 1.00
def bonus_meal(h): return 1.02 if h >= 2 else 0.99
def scaled_watch(score): return 0.5 + 0.5*(score/100.0)

def soft_cap(raw, watch_scaled):
    raw = clamp(raw, 0, 1.5)
    watch_scaled = clamp(watch_scaled, 0.5, 1.0)
    # harmonic mean keeps lower side influential
    return 2.0 / (1.0/max(raw,1e-9) + 1.0/max(watch_scaled,1e-9))

def MRI_calc(s):
    fq = f_qty(s.TST)
    fsws = f_sws(s.SWS)
    frem = f_rem(s.REM)
    fcont_ = f_cont(s.WASO, s.wakes, s.mode)
    freg = f_reg(s.BT_SD, s.WU_SD)
    gm_musc = (fq**0.35) * (fsws**0.25) * (frem**0.10) * (fcont_**0.15) * (freg**0.15)
    MRI_raw = gm_musc * pen_screens(s.Screens) * bonus_temp(s.Temp) * bonus_rh(s.RH) * bonus_ear(s.Ear) * bonus_meal(s.LastMeal)
    MRI = clamp(soft_cap(MRI_raw, scaled_watch(s.SleepScore)), 0, 1.0) * 100
    return round(MRI, 1), dict(fq=fq, fsws=fsws, frem=frem, fcont=fcont_, freg=freg)

# =========================
# Avatar builder (SVG)
# =========================
def color_by_score(score):
    # red→amber→green spectrum
    if score < 65: return "#ef4444"
    if score < 78: return "#f59e0b"
    if score < 85: return "#22c55e"
    return "#10b981"

def gear_badges(s):
    gear = []
    if s.Ear >= 1: gear.append("🦻 Earplugs")
    if s.Screens <= 0.75: gear.append("🕶️ Blue-block")
    if 20 <= s.Temp <= 25 and 40 <= s.RH <= 60: gear.append("❄️ Comfy room")
    if s.LastMeal >= 2: gear.append("🍽️ Early meal")
    return " · ".join(gear) if gear else "—"

def svg_avatar(score, s, mini=False):
    # scale muscles with score
    # base sizes
    chest = 60 + (score-50)*0.5     # 35–85
    arm   = 16 + (score-50)*0.20    # 6–26
    thigh = 24 + (score-50)*0.25    # 11–36
    neck  = 12 + (score-50)*0.08
    color = color_by_score(score)
    outline = "#0f172a"
    skin = "#eab308" if score >= 85 else "#f59e0b" if score >= 75 else "#f97316"

    # accessories
    earplug_left = ' <circle cx="168" cy="95" r="2.5" fill="#ffffff" />' if s.Ear>=1 else ""
    glasses = ' <rect x="143" y="85" width="18" height="6" rx="2" fill="#111827"/><rect x="162" y="85" width="18" height="6" rx="2" fill="#111827"/><rect x="161" y="87" width="2" height="2" fill="#111827"/>' if s.Screens<=0.75 else ""
    # room aura
    aura = "#06b6d4" if (20 <= s.Temp <= 25 and 40 <= s.RH <= 60) else "#64748b"

    W = 360 if not mini else 200
    H = 420 if not mini else 230
    scale = 1.0 if not mini else 0.6

    svg = f'''
<svg width="{W}" height="{H}" viewBox="0 0 360 420" xmlns="http://www.w3.org/2000/svg">
  <!-- background aura -->
  <defs>
    <radialGradient id="aura" cx="50%" cy="20%" r="70%">
      <stop offset="0%" stop-color="{aura}" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="#0b0f1a" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#aura)"/>
  <!-- torso -->
  <g transform="translate(0,0) scale({scale})">
    <ellipse cx="180" cy="140" rx="{neck}" ry="{neck/1.2}" fill="{skin}" stroke="{outline}" stroke-width="2"/>
    <ellipse cx="180" cy="190" rx="{chest}" ry="60" fill="{color}" stroke="{outline}" stroke-width="3"/>
    <!-- arms -->
    <ellipse cx="{180-chest}" cy="200" rx="{arm}" ry="40" fill="{color}" stroke="{outline}" stroke-width="3"/>
    <ellipse cx="{180+chest}" cy="200" rx="{arm}" ry="40" fill="{color}" stroke="{outline}" stroke-width="3"/>
    <!-- waist & hips -->
    <ellipse cx="180" cy="260" rx="{chest*0.7}" ry="40" fill="{color}" stroke="{outline}" stroke-width="3"/>
    <!-- legs -->
    <ellipse cx="{160}" cy="330" rx="{thigh}" ry="55" fill="{color}" stroke="{outline}" stroke-width="3"/>
    <ellipse cx="{200}" cy="330" rx="{thigh}" ry="55" fill="{color}" stroke="{outline}" stroke-width="3"/>
    <!-- head -->
    <circle cx="180" cy="100" r="28" fill="{skin}" stroke="{outline}" stroke-width="3"/>
    {glasses}
    {earplug_left}
    <!-- medal if elite -->
    {"<circle cx='180' cy='220' r='10' fill=\"#facc15\" stroke=\"#7c3aed\" stroke-width=\"2\"/>" if score>=90 else ""}
  </g>
</svg>
'''
    return svg

# =========================
# UI bits
# =========================
def header():
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
                background:linear-gradient(135deg,#0b0f1a,#0a0e17);
                border:1px solid rgba(255,255,255,.12); padding:10px 14px;border-radius:14px;">
      <div>
        <div style="font-weight:900;font-size:22px;">💪 Hypertrophy Quest — Avatar Builder</div>
        <div style="opacity:.8;font-size:12px;">{datetime.now().strftime("%b %d, %Y")} — Build your physique by nailing weekly recovery.</div>
      </div>
      <div style="opacity:.9;">Player: <b>{st.session_state.name}</b></div>
    </div>
    """, unsafe_allow_html=True)

def nav(prev=True, next=True, next_label="Next"):
    c1, c2, c3 = st.columns([1,6,1])
    with c1:
        if prev and st.button("← Back"):
            st.session_state.step = max(0, st.session_state.step - 1)
            st.rerun()
    with c3:
        if next and st.button(f"{next_label} →"):
            st.session_state.step = min(7, st.session_state.step + 1)
            st.rerun()

# =========================
# Screens
# =========================
def screen_intro():
    header()
    st.markdown("### Welcome, athlete.")
    st.write("This is a **mini-game** where each screen records one weekly metric. "
             "As you progress, your **avatar grows** based on your **Muscular Recovery Index (MRI)**.")
    st.text_input("Choose your avatar name", key="name")
    # live mini avatar preview
    mri,_ = MRI_calc(st.session_state)
    st.markdown("#### Current physique preview")
    st.markdown(svg_avatar(mri, st.session_state, mini=True), unsafe_allow_html=True)
    nav(prev=False, next=True, next_label="Start")

def screen_sleep_qty():
    header()
    st.markdown("### Stage 1: Sleep Quantity")
    st.write("Target **~8 hours** on average. Very low or very high drags recovery.")
    st.session_state.TST = st.slider("Average total sleep (hours)", 4.0, 10.0, st.session_state.TST, 0.1)
    mri,_ = MRI_calc(st.session_state)
    st.markdown(svg_avatar(mri, st.session_state, mini=True), unsafe_allow_html=True)
    nav()

def screen_deep():
    header()
    st.markdown("### Stage 2: Deep Sleep (SWS)")
    st.write("Deep sleep supports **anabolism**; aim **≥ 1.5 h**.")
    st.session_state.SWS = st.slider("Average deep sleep (hours)", 0.3, 3.0, st.session_state.SWS, 0.1)
    mri,_ = MRI_calc(st.session_state)
    st.markdown(svg_avatar(mri, st.session_state, mini=True), unsafe_allow_html=True)
    nav()

def screen_continuity():
    header()
    st.markdown("### Stage 3: Continuity")
    st.write("Fewer, shorter awakenings → better recovery.")
    st.session_state.mode = st.radio("Continuity input", ["Wake count", "WASO minutes"], index=0 if st.session_state.mode=="Wake count" else 1)
    if st.session_state.mode == "WASO minutes":
        st.session_state.WASO = st.slider("WASO (minutes per night)", 0, 180, st.session_state.WASO, 5)
    else:
        st.session_state.wakes = st.slider("Awakenings per night", 0, 6, st.session_state.wakes, 1)
    mri,_ = MRI_calc(st.session_state)
    st.markdown(svg_avatar(mri, st.session_state, mini=True), unsafe_allow_html=True)
    nav()

def screen_regular():
    header()
    st.markdown("### Stage 4: Regularity")
    st.write("Keep **bed/wake within ~1 h** to support circadian alignment.")
    st.session_state.BT_SD = st.slider("Bedtime variability (SD, hours)", 0.0, 3.0, st.session_state.BT_SD, 0.05)
    st.session_state.WU_SD = st.slider("Wake-time variability (SD, hours)", 0.0, 3.0, st.session_state.WU_SD, 0.05)
    mri,_ = MRI_calc(st.session_state)
    st.markdown(svg_avatar(mri, st.session_state, mini=True), unsafe_allow_html=True)
    nav()

def screen_env():
    header()
    st.markdown("### Stage 5: Environment")
    st.write("Best zone: **20–25°C** & **40–60% RH**.")
    st.session_state.Temp = st.slider("Bedroom temperature (°C)", 15, 30, st.session_state.Temp, 1)
    st.session_state.RH = st.slider("Bedroom humidity (%)", 20, 80, st.session_state.RH, 1)
    st.session_state.Ear = st.selectbox("Earplugs worn", [0,1,2], index=st.session_state.Ear)
    mri,_ = MRI_calc(st.session_state)
    st.markdown(svg_avatar(mri, st.session_state, mini=True), unsafe_allow_html=True)
    nav()

def screen_habits():
    header()
    st.markdown("### Stage 6: Late Habits")
    st.write("Less **screen time after 9 PM** and **last meal ≥ 2 h** before bed helps.")
    st.session_state.Screens = st.slider("Screen time after 9 PM (hours)", 0.0, 4.0, st.session_state.Screens, 0.1)
    st.session_state.LastMeal = st.slider("Last meal (hours before bed)", 0.0, 5.0, st.session_state.LastMeal, 0.25)
    st.session_state.SleepScore = st.slider("Noise Sleep Score (/100)", 0, 100, st.session_state.SleepScore, 1)
    mri,_ = MRI_calc(st.session_state)
    st.markdown(svg_avatar(mri, st.session_state, mini=True), unsafe_allow_html=True)
    nav(next_label="Forge Avatar")

def screen_final():
    header()
    st.markdown("### Final Form Revealed")
    mri,_ = MRI_calc(st.session_state)
    col = color_by_score(mri)
    tier = "Bronze" if mri<68 else "Silver" if mri<78 else "Gold" if mri<85 else "Platinum" if mri<92 else "Diamond"
    st.markdown(f"**{st.session_state.name}** — **MRI: {mri:.1f}%** · Tier: **{tier}**")
    st.markdown(svg_avatar(mri, st.session_state, mini=False), unsafe_allow_html=True)

    # Gear badges
    st.markdown("**Gear & perks unlocked:** " + gear_badges(st.session_state))

    # Buttons
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("← Edit previous"):
            st.session_state.step = 5
            st.rerun()
    with c2:
        if st.button("🔁 Start over"):
            for k in list(st.session_state.keys()):
                if k not in ("step","confetti","name"):
                    del st.session_state[k]
            init_state()
            st.session_state.step = 0
            st.rerun()
    with c3:
        if st.button("📤 Save as this week's result"):
            st.success("Saved locally in session (persisting to file/DB would be the next upgrade).")

    if st.session_state.confetti and mri>=90:
        st.balloons()

# =========================
# Router
# =========================
screens = [
    screen_intro,       # 0
    screen_sleep_qty,   # 1
    screen_deep,        # 2
    screen_continuity,  # 3
    screen_regular,     # 4
    screen_env,         # 5
    screen_habits,      # 6
    screen_final        # 7
]
screens[st.session_state.step]()
