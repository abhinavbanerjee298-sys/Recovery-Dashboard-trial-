# recovery_dashboard.py
import math
import numpy as np
import streamlit as st

# -------------------------------
# Page & layout
# -------------------------------
st.set_page_config(page_title="Sleep → Recovery (Science-backed)", layout="wide")
st.title("🛌→📈 Recovery Indices (Science-backed)")
st.caption("Cognitive Recovery Index (CRI) and Muscular Recovery Index (MRI), based on sleep science & circadian evidence.")

with st.sidebar:
    st.header("⚙️ Options")
    use_waso = st.radio("Continuity input:", ["Wake count", "WASO minutes"], index=0)
    st.write("• Scores are **estimates**, not medical advice.\n• Ranges are calibrated so ‘good’ weeks land ~78–92.")

# -------------------------------
# Inputs
# -------------------------------
sleep_col, env_col = st.columns(2)

with sleep_col:
    st.subheader("😴 Sleep")
    TST = st.slider("Average total sleep (hours)", 4.0, 10.0, 7.8, 0.1)
    SWS = st.slider("Average deep sleep (SWS, hours)", 0.3, 3.0, 1.6, 0.1)
    REM = st.slider("Average REM sleep (hours)", 0.3, 3.0, 1.8, 0.1)

    if use_waso == "WASO minutes":
        WASO_min = st.slider("Wake After Sleep Onset (minutes/night)", 0, 180, 35, 5)
        wake_count = None
    else:
        wake_count = st.slider("Average number of awakenings/night", 0, 6, 1, 1)
        WASO_min = None

    BT_SD = st.slider("Bedtime variability (SD, hours)", 0.0, 3.0, 0.6, 0.05)
    WU_SD = st.slider("Wake-time variability (SD, hours)", 0.0, 3.0, 0.7, 0.05)
    SleepScore = st.slider("Noise Sleep Score (/100)", 0, 100, 82, 1)

with env_col:
    st.subheader("🏠 Environment & habits")
    Temp = st.slider("Bedroom temperature (°C)", 15, 30, 23)
    RH = st.slider("Bedroom humidity (%)", 20, 80, 50)
    Screens = st.slider("Screen time after 9 PM (hours)", 0.0, 4.0, 0.8, 0.1)
    LastMeal_h = st.slider("Last meal time (hours before bed)", 0.0, 5.0, 2.0, 0.25)
    earplugs = st.selectbox("Earplugs worn", [0, 1, 2], index=0, format_func=lambda x: f"{x} earplug(s)")

# -------------------------------
# Helper: clamp
# -------------------------------
def clamp(x, lo, hi):
    return max(lo, min(hi, x))

# -------------------------------
# Normalizations (0–1 or small >1 bonus caps)
# -------------------------------
# Quantity (U-shape around 8h, σ≈1h), clamped so 6–10h isn’t crushed
def f_qty(TST):
    val = math.exp(-0.5 * ((TST - 8.0)/1.0)**2)
    return clamp(val, 0.4, 1.0)

# Architecture midpoints with small capped bonuses
def f_sws(SWS):
    return clamp(SWS / 1.6, 0.2, 1.15)  # up to +15% bonus when >1.6h

def f_rem(REM):
    return clamp(REM / 1.8, 0.2, 1.10)  # up to +10% bonus when >1.8h

# Continuity (prefer WASO; else wake count)
def f_cont(WASO_min, wake_count):
    if WASO_min is not None:
        return 1.0 - min(WASO_min, 90)/300.0  # 0–90→1.0→0.7
    else:
        return 1.0 - min(wake_count, 5)*0.06  # 0–5→1.0→0.70

# Regularity (bed + wake), guard rail at 0.5
def f_reg(BT_SD, WU_SD):
    base = math.exp(-((BT_SD/1.0)**2 + (WU_SD/1.0)**2)/2.0)
    return max(0.5, base)

# Modifiers
def pen_screens(Screens):
    return 1.0 - min(Screens, 3.0)*0.04  # up to −12%

def bonus_temp(Temp):
    return 1.05 if 20 <= Temp <= 25 else 1.00

def bonus_rh(RH):
    return 1.03 if 40 <= RH <= 60 else 1.00

def bonus_ear(earplugs):
    return 1.02 if earplugs >= 1 else 1.00

def bonus_meal(LastMeal_h):
    return 1.02 if LastMeal_h >= 2 else 0.99

def scaled_watch(SleepScore):
    return 0.5 + 0.5*(SleepScore/100.0)  # 0.5–1.0

# -------------------------------
# Geometric means → raw indices
# -------------------------------
fq = f_qty(TST)
fsws = f_sws(SWS)
frem = f_rem(REM)
fcont = f_cont(WASO_min, wake_count)
freg = f_reg(BT_SD, WU_SD)

# CRI weights: quantity 0.30, REM 0.25, SWS 0.15, continuity 0.15, regularity 0.15
gm_cog = (fq**0.30) * (frem**0.25) * (fsws**0.15) * (fcont**0.15) * (freg**0.15)
CRI_raw = gm_cog * pen_screens(Screens) * bonus_temp(Temp) * bonus_rh(RH) * bonus_meal(LastMeal_h)

# MRI weights: quantity 0.35, SWS 0.25, REM 0.10, continuity 0.15, regularity 0.15
gm_musc = (fq**0.35) * (fsws**0.25) * (frem**0.10) * (fcont**0.15) * (freg**0.15)
MRI_raw = gm_musc * pen_screens(Screens) * bonus_temp(Temp) * bonus_rh(RH) * bonus_ear(earplugs) * bonus_meal(LastMeal_h)

# Soft cap / nudge via harmonic mean with device score
def soft_cap(raw, watch_scaled):
    raw = clamp(raw, 0, 1.5)  # protect against accidental >1 from bonuses
    watch_scaled = clamp(watch_scaled, 0.5, 1.0)
    # Harmonic mean of raw and watch to keep the lower influential
    return 2.0 / (1.0/max(raw, 1e-9) + 1.0/max(watch_scaled, 1e-9))

CRI = round(clamp(soft_cap(CRI_raw, scaled_watch(SleepScore)), 0, 1.0) * 100, 1)
MRI = round(clamp(soft_cap(MRI_raw, scaled_watch(SleepScore)), 0, 1.0) * 100, 1)

# -------------------------------
# UI: headline gauges
# -------------------------------
def gauge(label, value):
    color = "#2ecc71" if value >= 80 else "#f39c12" if value >= 65 else "#e74c3c"
    st.markdown(f"""
    <div style="text-align:center; margin: 4px 0 16px 0;">
      <div style="font-weight:600; font-size: 18px; margin-bottom: 4px;">{label}</div>
      <div style="font-size: 42px; font-weight: 800; color:{color}; line-height:1;">{value:.1f}%</div>
      <div style="height: 10px; background:#e6e6e6; border-radius:6px; margin-top:8px;">
        <div style="width:{value}%; height:10px; background:{color}; border-radius:6px;"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.subheader("📊 Recovery this week")
g1, g2 = st.columns(2)
with g1: gauge("🧠 Cognitive Recovery Index (CRI)", CRI)
with g2: gauge("💪 Muscular Recovery Index (MRI)", MRI)

# -------------------------------
# Factor breakdown
# -------------------------------
st.markdown("### 🔎 Factor breakdown (normalized 0–1, bonuses may exceed 1 slightly)")
fb1, fb2, fb3 = st.columns(3)
with fb1:
    st.write(f"- **Quantity (f_qty)**: `{fq:.3f}`  (target ~1.0 around 8h)")
    st.write(f"- **SWS / Deep (f_sws)**: `{fsws:.3f}`  (cap 1.15)")
with fb2:
    st.write(f"- **REM (f_rem)**: `{frem:.3f}`  (cap 1.10)")
    st.write(f"- **Continuity (f_cont)**: `{fcont:.3f}`")
with fb3:
    st.write(f"- **Regularity (f_reg)**: `{freg:.3f}`")
    st.write(f"- **Watch scaled**: `{scaled_watch(SleepScore):.3f}`")

st.markdown("### ⚖️ Modifiers applied")
m1, m2, m3 = st.columns(3)
with m1:
    st.write(f"- Screens penalty: `{pen_screens(Screens):.3f}`")
    st.write(f"- Temp bonus: `{bonus_temp(Temp):.3f}`")
with m2:
    st.write(f"- RH bonus: `{bonus_rh(RH):.3f}`")
    st.write(f"- Earplugs bonus: `{bonus_ear(earplugs):.3f}`")
with m3:
    st.write(f"- Meal timing: `{bonus_meal(LastMeal_h):.3f}`")
    if WASO_min is not None:
        st.write(f"- Using **WASO** continuity")
    else:
        st.write(f"- Using **wake count** continuity")

# -------------------------------
# Contextual tips
# -------------------------------
st.markdown("---")
st.subheader("💡 Targeted suggestions")
tips = []
if TST < 7.0 or TST > 9.5:
    tips.append("Keep weekly average sleep close to **8h**; big deviations reduce CRI/MRI.")
if SWS < 1.3:
    tips.append("Aim for **≥1.5h deep sleep**; cool, dark, quiet bedroom helps.")
if REM < 1.5:
    tips.append("Push **REM** up by improving sleep continuity and reducing late screens.")
if (WASO_min and WASO_min > 45) or (wake_count is not None and wake_count > 2):
    tips.append("Reduce **fragmentation** (noise/light control, wind-down routine).")
if BT_SD > 1.0 or WU_SD > 1.0:
    tips.append("Tighten **regularity**: keep bed/wake within ~1h day-to-day.")
if not (20 <= Temp <= 25):
    tips.append("Keep room **20–25°C** to support sleep efficiency.")
if not (40 <= RH <= 60):
    tips.append("Keep humidity around **40–60%** if possible.")
if Screens > 1.0:
    tips.append("Limit **screens after 9 PM** or use stronger blue-light blocking.")

if tips:
    for t in tips:
        st.write("• " + t)
else:
    st.success("Nice! Your inputs align well with strong weekly recovery.")

st.caption("Calibration: Good but realistic weeks typically yield ~78–92. Irregular schedules or fragmented sleep will pull scores into the 60s or below.")
