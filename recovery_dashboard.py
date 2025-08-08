# recovery_dashboard.py
import streamlit as st
import numpy as np

st.set_page_config(page_title="Recovery Dashboard", layout="wide")

st.title("🛌 Sleep & Recovery Estimator")
st.write("Adjust the sliders to input your weekly averages. The model will estimate your cognitive and muscular recovery.")

# --- INPUT SLIDERS ---
st.subheader("Sleep Metrics")
total_sleep = st.slider("Average Total Sleep (hrs)", 4.0, 10.0, 7.5, 0.1)
deep_sleep = st.slider("Average Deep Sleep (hrs)", 0.5, 3.0, 1.5, 0.1)
rem_sleep = st.slider("Average REM Sleep (hrs)", 0.5, 3.0, 1.8, 0.1)
wake_count = st.slider("Average Night Wake-Ups", 0, 6, 2)
sleep_score = st.slider("Average Sleep Score (Noise Watch)", 0, 100, 80)
bedtime_var = st.slider("Bedtime Variability (hrs STDEV)", 0.0, 3.0, 0.5, 0.1)
wake_var = st.slider("Wake Time Variability (hrs STDEV)", 0.0, 3.0, 0.6, 0.1)

# --- ENVIRONMENT ---
st.subheader("Environment Metrics")
bed_temp = st.slider("Nighttime Bedroom Temp (°C)", 15, 30, 23)
humidity = st.slider("Bedroom Humidity (%)", 20, 80, 50)
avg_bedtime = st.slider("Average Bedtime (24h)", 18.0, 2.0+24, 23.0, 0.25, format="%0.2f")
last_meal = st.slider("Average Last Meal Time (hrs before bed)", 0.0, 5.0, 2.0, 0.25)
earplugs = st.selectbox("Earplugs Worn", options=[0, 1, 2], format_func=lambda x: f"{x} earplugs")
screen_time = st.slider("Screen Time after 9 PM (hrs)", 0.0, 4.0, 1.0, 0.1)

# --- SIMPLE CALCULATIONS ---
# Weighting factors for cognitive vs muscular recovery
cognitive_score = (
    (total_sleep/8.0)*30 +
    (deep_sleep/2.0)*20 +
    (rem_sleep/2.0)*20 +
    (100 - sleep_score)/-3 +
    (-(wake_count*2)) +
    (max(0, 1-bedtime_var))*10 +
    (max(0, 1-wake_var))*10 -
    (screen_time*3) +
    (last_meal*1)
)

muscular_score = (
    (total_sleep/8.0)*25 +
    (deep_sleep/2.0)*25 +
    (humidity >= 40 and humidity <= 60)*5 +
    (bed_temp >= 18 and bed_temp <= 22)*5 +
    (100 - sleep_score)/-4 +
    (max(0, 1-bedtime_var))*10 +
    (wake_var < 1)*5 -
    (screen_time*2) +
    (last_meal*2)
)

# Normalize
cognitive_score = np.clip(cognitive_score, 0, 100)
muscular_score = np.clip(muscular_score, 0, 100)

# --- OUTPUT ---
st.subheader("📊 Recovery Estimates")
col1, col2 = st.columns(2)
with col1:
    st.metric("Cognitive Recovery (%)", f"{cognitive_score:.1f}")
with col2:
    st.metric("Muscular Recovery (%)", f"{muscular_score:.1f}")

# Interpretation
st.write("### Interpretation")
if cognitive_score > 80:
    st.success("Cognitive recovery is excellent — your brain is well-rested for focus, memory, and decision-making.")
elif cognitive_score > 60:
    st.info("Cognitive recovery is moderate — consider improving deep/REM sleep or reducing nighttime screen use.")
else:
    st.warning("Cognitive recovery is poor — your sleep habits or environment may be holding back mental performance.")

if muscular_score > 80:
    st.success("Muscular recovery is excellent — you're set for good training adaptation and hypertrophy.")
elif muscular_score > 60:
    st.info("Muscular recovery is moderate — fine-tune sleep length, deep sleep, and hydration.")
else:
    st.warning("Muscular recovery is poor — training performance and muscle gains may suffer.")

st.caption("This is an estimation tool and not a medical diagnostic. Adjust the weights for your own data and observations.")
