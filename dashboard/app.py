import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from controller import SumoTrafficEnv
from model import TrafficRLModel

st.set_page_config(page_title="Mangalore Traffic AI", layout="wide", initial_sidebar_state="expanded")

# Inject Premium Glassmorphism and Dark Theme CSS
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Dynamic Background Gradient */
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1e293b, #0f172a, #334155);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #f8fafc;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Refined Typography */
    h1 {
        font-weight: 700 !important;
        font-size: 3rem !important;
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem !important;
        text-shadow: 0px 4px 20px rgba(56, 189, 248, 0.2);
    }
    h2, h3 {
        font-weight: 600 !important;
        color: #e2e8f0 !important;
    }

    /* Glassmorphism Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #38bdf8 !important;
    }
    div[data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem !important;
        border-radius: 1rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(56, 189, 248, 0.2);
        border: 1px solid rgba(56, 189, 248, 0.4);
    }

    /* Custom Button Styling */
    div.stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.75rem;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
    }

    /* Styled Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Charts container */
    [data-testid="stArrowVegaLiteChart"] {
        background: rgba(30, 41, 59, 0.4);
        padding: 1rem;
        border-radius: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>Mangalore AI Traffic Control</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #94a3b8; font-size: 1.1rem; margin-bottom: 2rem;'>Intelligent, real-time reinforcement learning controlling SUMO micro-simulated junctions.</p>", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("Controls")
use_gui = st.sidebar.checkbox("Open SUMO-GUI", value=False)
algo = st.sidebar.selectbox("Controller", ["PPO (trained)", "Fixed cycle baseline"])
max_steps = st.sidebar.slider("Max steps", 100, 720, 360)
run_btn = st.sidebar.button("Run episode")

if run_btn:
    env = SumoTrafficEnv(
        config_path="simulation/config.sumocfg",
        use_gui=use_gui,
        max_steps=max_steps * 5,
    )

    use_rl = algo.startswith("PPO")
    rl_model = None
    if use_rl:
        try:
            rl_model = TrafficRLModel(model_path="models/ppo_mangalore_sumo")
            rl_model.load()
            st.sidebar.success("Loaded trained PPO model.")
        except Exception as e:
            st.sidebar.warning(f"Model not found ({e}). Run train.py first.")
            use_rl = False

    obs, info = env.reset()
    history = []
    progress = st.progress(0, "Running SUMO episode...")

    done = False
    step = 0
    while not done and step < max_steps:
        if use_rl and rl_model:
            action, _ = rl_model.predict(obs)
        else:
            action = step % env.action_space.n   # fixed round-robin

        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated

        row = {
            "step": step,
            "reward": reward,
            "phase": info["current_phase"],
            "total_vehicles": info["total_vehicles"],
        }
        row.update({f"lane_{k.split('_')[-1]}": v
                    for k, v in info["lane_counts"].items()})
        history.append(row)
        step += 1
        progress.progress(step / max_steps)

    env.close()
    progress.empty()
    df = pd.DataFrame(history)

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total steps", len(df))
    c2.metric("Avg reward / step", f"{df['reward'].mean():.4f}")
    c3.metric("Controller", algo)

    # Charts
    st.subheader("Reward over time")
    st.line_chart(df.set_index("step")["reward"])

    st.subheader("Vehicle counts per lane")
    lane_cols = [c for c in df.columns if c.startswith("lane_")]
    if lane_cols:
        st.line_chart(df.set_index("step")[lane_cols])

    st.subheader("Traffic light phase")
    st.line_chart(df.set_index("step")["phase"])

else:
    # ------------------------------------------------------------------
    # WELCOME / EMPTY STATE
    # ------------------------------------------------------------------
    st.markdown("""
        <div style='background: rgba(30, 41, 59, 0.4); padding: 2rem; border-radius: 1rem; border: 1px solid rgba(255, 255, 255, 0.05); margin-top: 1rem;'>
            <h2 style='color: #e2e8f0; margin-bottom: 1rem;'>Welcome to the Simulation Dashboard 👋</h2>
            <p style='color: #cbd5e1; font-size: 1.1rem; line-height: 1.6;'>
                You are about to run a <strong style='color: #38bdf8;'>physics-based traffic simulation</strong> for the city of Mangalore. 
                Instead of using arbitrary numbers, this dashboard controls a live instance of <b>SUMO</b> (Simulation of Urban MObility) 
                which mathematically renders microscopic car behaviors, lane assignments, and traffic lights on a real mapped junction.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
            <div style='background: rgba(56, 189, 248, 0.1); padding: 1.5rem; border-radius: 1rem; border: 1px solid rgba(56, 189, 248, 0.2); height: 100%;'>
                <h3 style='color: #38bdf8;'>🧠 The Controllers</h3>
                <ul style='color: #cbd5e1; font-size: 1.05rem; line-height: 1.6;'>
                    <li><b>Fixed cycle baseline:</b> A dumb, traditional traffic light that swaps green phases every 30 seconds blindly, regardless of how many cars are waiting.</li>
                    <li><b>PPO (trained):</b> A state-of-the-art Reinforcement Learning brain. It dynamically observes the <i>exact vehicle count</i> at the junction in real-time and swaps lights on the fly to aggressively clear traffic jams.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    with c2:
         st.markdown("""
            <div style='background: rgba(129, 140, 248, 0.1); padding: 1.5rem; border-radius: 1rem; border: 1px solid rgba(129, 140, 248, 0.2); height: 100%;'>
                <h3 style='color: #818cf8;'>🚀 How to Start</h3>
                <ol style='color: #cbd5e1; font-size: 1.05rem; line-height: 1.6;'>
                    <li>Select a <b>Controller</b> from the sidebar on the left.</li>
                    <li>Adjust the <b>Max steps</b> if you want a longer or shorter simulation (1 step = 5 real-world seconds).</li>
                    <li>Tick <b>Open SUMO-GUI</b> if you want to visually watch the little 3D cars driving around the junction!</li>
                    <li>Click the blue <b>Run episode</b> button to start the engine.</li>
                </ol>
            </div>
        """, unsafe_allow_html=True)
