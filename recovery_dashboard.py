# recovery_dashboard.py
import streamlit as st
import numpy as np
import math

# --- PAGE CONFIG ---
st.set_page_config(page_title="Sleep & Recovery Dashboard", layout="wide")
st.title("🛌 Sleep & Recovery Estimator")
st.caption("An interactive tool to estimate your weekly cognitive and muscular recovery based on sleep & lifestyle inputs.")

# --- LAYOUT ---
sleep_col, env_col = st.columns(2)

# ----------------------------
# SLEEP METRICS
# ----------------------------
with sleep_col:
    st.header("😴 Sleep Metrics")
    total_sleep = st.slider("Average Total Sleep (hrs)", 4.0, 10.0, 7.5, 0.1)
    deep_sleep = st.slider("Average Deep Sleep (hrs)", 0.5, 3.0, 1.6, 0.1)
    rem_sleep = st.slider("Average REM Sleep (hrs)", 0.5, 3.0, 1.8, 0.1)
    wake_count = st.slider("Average Night Wake-Ups", 0, 6, 1)
    sleep_score = st.slider("Average Sleep Score (Noise Watch)", 0, 100, 82)
    bedtime_var = st.slider("Bedtime Variability (hrs STDEV)", 0.0, 3.0, 0.5, 0.1)
    wake_var = st.slider("Wake Time Variability (hrs STDEV)", 0.0, 3.0, 0.6, 0.1)

# ----------------------------
# ENVIRONMENT & HABITS
# ----------------------------
with env_col:
    st.header("🏠 Environment & Habits")
    bed_temp = st.slider("Nighttime Bedroom Temp (°C)", 15, 30, 22)
    humidity = st.slider("Bedroom Humidity (%)", 20, 80, 50)
    avg_bedtime = st.slider("Average Bedtime (24h)", 18.0, 26.0, 23.0, 0.25, format="%0.2f")
    last_meal = st.slider("Last Meal Time (hrs before bed)", 0.0, 5.0, 2.0, 0.25)
    earplugs = st.selectbox("Earplugs Worn", options=[0, 1, 2], format_func=lambda x: f"{x} earplug(s)")
    screen_time = st.slider("Screen Time after 9 PM (hrs)", 0.0, 4.0, 1.0, 0.1)

# ----------------------------
# RECOVERY FORMULAS
# ----------------------------
def calc_cognitive():
    base = (
        (total_sleep / 8.0)**0.9 *
        (deep_sleep / 1.5)**0.8 *
        (rem_sleep / 1.8)**0.9 *
        (sleep_score / 85)**1.0 *
        (1 - (bedtime_var / 3.0))**0.8 *
        (1 - (wake_var / 3.0))**0.8
    )
    # penalties
    penalty = 1 - (screen_time / 6) - (wake_count * 0.02)
    return np.clip(base * penalty * 100, 0, 100)

def calc_muscular():
    base = (
        (total_sleep / 8.0)**0.9 *
        (deep_sleep / 1.5)**0.85 *
        (sleep_score / 85)**1.0 *
        (1 - (bedtime_var / 3.0))**0.85 *
        (1 - (wake_var / 3.0))**0.85
    )
    score = base * 100

    # bonuses
    if 18 <= bed_temp <= 22:
        score += 3
    if 40 <= humidity <= 60:
        score += 3
    if screen_time < 1:
        score += 2
    if last_meal >= 2:
        score += 1

    # small penalty for many wake-ups
    score -= wake_count * 1.5

    return np.clip(score, 0, 100)

cognitive_score = calc_cognitive()
muscular_score = calc_muscular()

# ----------------------------
# DISPLAY RESULTS
# ----------------------------
st.markdown("---")
st.header("📊 Recovery Estimates")

def gauge_html(label, value, color):
    return f"""
    <div style="text-align:center; margin: 10px;">
        <h3 style="margin-bottom: -10px;">{label}</h3>
        <div style="font-size: 40px; font-weight: bold; color: {color};">{value:.1f}%</div>
        <div style="height: 10px; background-color: #ddd; border-radius: 5px;">
            <div style="width: {value}%; background-color: {color}; height: 10px; border-radius: 5px;"></div>
        </div>
    </div>
    """

col1, col2 = st.columns(2)
with col1:
    col_color = "#2ecc71" if cognitive_score > 80 else "#f39c12" if cognitive_score > 60 else "#e74c3c"
    st.markdown(gauge_html("🧠 Cognitive Recovery", cognitive_score, col_color), unsafe_allow_html=True)
with col2:
    col_color = "#2ecc71" if muscular_score > 80 else "#f39c12" if muscular_score > 60 else "#e74c3c"
    st.markdown(gauge_html("💪 Muscular Recovery", muscular_score, col_color), unsafe_allow_html=True)

# ----------------------------
# TIPS
# ----------------------------
st.markdown("---")
st.header("💡 Recovery Tips")
if muscular_score < 75:
    st.write("💪 Increase **deep sleep** above 1.5h and keep **bed temp** in 18–22°C range.")
if cognitive_score < 75:
    st.write("🧠 Reduce **screen time after 9 PM** and improve **bed/wake consistency**.")
if bedtime_var > 1:
    st.write("📅 Try to keep bedtime variation under 1h for optimal circadian alignment.")
if wake_count > 2:
    st.write("🌙 Work on reducing night-time wake-ups — consider optimizing room darkness and noise.")

st.caption("Note: These scores are estimates based on known sleep & recovery research. Adjust the formula weights if you have personal data.")
