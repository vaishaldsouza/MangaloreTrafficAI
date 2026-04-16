"""
dashboard/app.py  —  Mangalore Traffic AI  (full rewrite)

Features:
  • Tab 1 — 🗺️  Mangalore map, traffic heatmap (post-sim), route finder
  • Tab 2 — 🚦  Simulation: 5 controllers, live vehicle positions on map
  • Tab 3 — 📊  Results: charts, lane heatmap, CSV download
"""

import os
import sys
import numpy as np
import pandas as pd
import streamlit as st

# ── path setup ────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Mangalore Traffic AI",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🚦",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(-45deg, #0d1117, #161b22, #0d1117, #1c2333);
    background-size: 400% 400%;
    animation: gradBG 18s ease infinite;
    color: #f0f6fc;
}
@keyframes gradBG {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
h1 {
    font-weight: 700 !important;
    font-size: 2.4rem !important;
    background: linear-gradient(90deg, #58a6ff, #bc8cff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
h2, h3 { font-weight: 600 !important; color: #c9d1d9 !important; }

div[data-testid="metric-container"] {
    background: rgba(22,27,34,.85);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: .8rem;
    padding: 1rem !important;
    box-shadow: 0 4px 18px rgba(0,0,0,.4);
    backdrop-filter: blur(8px);
    transition: transform .2s, box-shadow .2s;
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 28px rgba(88,166,255,.2);
    border-color: rgba(88,166,255,.3);
}
div[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: #58a6ff !important;
}
div.stButton > button {
    background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
    color: #fff; border: none;
    padding: .65rem 1.3rem; border-radius: .55rem;
    font-weight: 600; font-size: .95rem; width: 100%;
    box-shadow: 0 3px 12px rgba(35,134,54,.4);
    transition: all .2s;
}
div.stButton > button:hover {
    transform: scale(1.02);
    box-shadow: 0 5px 18px rgba(35,134,54,.6);
}
.info-card {
    background: rgba(22,27,34,.7);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: .8rem;
    padding: 1.1rem 1.3rem;
    color: #8b949e;
    line-height: 1.6;
}
.badge {
    display: inline-block; padding: .15rem .6rem;
    border-radius: 99px; font-size: .72rem; font-weight: 600;
}
.badge-green  { background: rgba(35,134,54,.25);  color: #3fb950; }
.badge-blue   { background: rgba(56,139,253,.25); color: #58a6ff; }
.badge-purple { background: rgba(188,140,255,.25);color: #bc8cff; }
.badge-orange { background: rgba(210,153,34,.25); color: #d29922; }
.badge-red    { background: rgba(248,81,73,.25);  color: #f85149; }
hr.div { border: none; border-top: 1px solid rgba(255,255,255,.07); margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ── constants ─────────────────────────────────────────────────────────────────
MANGALORE_CENTER = (12.8700, 74.8436)

LANDMARKS = {
    "📍 Select a location…": None,
    "Mangalore Central Station": (12.8710, 74.8418),
    "Hampankatta Circle": (12.8696, 74.8437),
    "KSRTC Bus Stand": (12.8695, 74.8456),
    "Lalbagh Junction": (12.8617, 74.8314),
    "Bunts Hostel Junction": (12.8755, 74.8356),
    "Bejai Cross Roads": (12.8763, 74.8456),
    "Kankanady Junction": (12.8765, 74.8523),
    "Attavar Junction": (12.8739, 74.8346),
    "State Bank Circle": (12.8635, 74.8432),
    "Falnir Road Junction": (12.8849, 74.8428),
    "Kadri Manjunath Temple": (12.8897, 74.8484),
    "Urwa Market": (12.9105, 74.8454),
    "Kavoor Junction": (12.9032, 74.8210),
    "Deralakatte Junction": (12.8366, 74.8183),
    "Mangalore Airport (Bajpe)": (12.9613, 74.8898),
    "Ullal Circle": (12.7968, 74.8632),
    "Surathkal NITK": (13.0125, 74.7965),
}

METHOD_INFO = {
    "Fixed-cycle baseline": {
        "badge": "badge-red", "icon": "🔴",
        "type_label": "Rule-based",
        "short": "Rotates phases every 30 s regardless of traffic.",
        "long": "Represents the real-world Mangalore signal. Blindly alternates every 30 steps — the baseline to beat.",
    },
    "Greedy adaptive": {
        "badge": "badge-orange", "icon": "🟠",
        "type_label": "Rule-based",
        "short": "Always greens the most congested lane.",
        "long": "A simple rule: observe vehicle counts, pick the busiest lane, give it green. No training needed.",
    },
    "Random Forest": {
        "badge": "badge-blue", "icon": "🌲",
        "type_label": "ML",
        "short": "Classifies congestion and maps to a phase.",
        "long": "Trained on synthetic hourly data. Classifies steps as free/moderate/congested and selects a phase accordingly.",
    },
    "LSTM predictor": {
        "badge": "badge-purple", "icon": "🔮",
        "type_label": "Deep ML",
        "short": "Uses last 12 steps of history to forecast demand.",
        "long": "A 2-layer LSTM predicts which lane will be most loaded next and activates the corresponding phase.",
    },
    "PPO (Reinforcement Learning)": {
        "badge": "badge-green", "icon": "🤖",
        "type_label": "RL",
        "short": "Neural network trained end-to-end in SUMO.",
        "long": "PPO agent trained for 200k simulation steps. Expected ~38% reduction in queue length vs fixed-cycle.",
    },
}

PHASE_LABELS = {0: "N-S Green", 1: "N-S Yellow", 2: "E-W Green", 3: "E-W Yellow"}

# ── session state initialisation ──────────────────────────────────────────────
for key, default in {
    "sim_df": None,
    "sim_positions": [],   # list of lists: [[lat,lon,speed], …] per step
    "sim_method": "",
    "sim_done": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── cached loaders ────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="Loading Mangalore road graph (first run only)…")
def load_road_graph():
    import osmnx as ox
    import networkx as nx
    try:
        G = ox.graph_from_point(MANGALORE_CENTER, dist=2500, network_type="drive")
        return G
    except Exception as e:
        st.warning(f"Could not load road graph: {e}")
        return None

def load_rf():
    try:
        import joblib
        return joblib.load("models/random_forest.pkl"), joblib.load("models/rf_label_encoder.pkl")
    except Exception:
        return None, None

def load_lstm():
    try:
        import torch
        from models.lstm_model import TrafficLSTM
        m = TrafficLSTM(input_size=6, hidden_size=128, num_layers=2, n_lanes=4)
        m.load_state_dict(torch.load("models/lstm_traffic.pt", map_location="cpu"))
        m.eval()
        return m
    except Exception:
        return None

def load_ppo():
    try:
        from stable_baselines3 import PPO
        for path in ["models/ppo_mangalore_sumo", "models/ppo_mangalore"]:
            try:
                return PPO.load(path), path
            except Exception:
                pass
    except Exception:
        pass
    return None, None

# ── helper: build folium base map ─────────────────────────────────────────────

def make_base_map(zoom=13, tiles="CartoDB dark_matter"):
    import folium
    m = folium.Map(
        location=list(MANGALORE_CENTER),
        zoom_start=zoom,
        tiles=tiles,
        attr="CartoDB",
    )
    return m

def add_landmarks_to_map(m, exclude=None):
    import folium
    for name, coords in LANDMARKS.items():
        if coords is None or name == exclude:
            continue
        folium.CircleMarker(
            location=coords,
            radius=5,
            color="#58a6ff",
            fill=True,
            fill_color="#58a6ff",
            fill_opacity=0.7,
            tooltip=name,
        ).add_to(m)
    return m

def add_heatmap_to_map(m, positions):
    """Add vehicle density heatmap from list of [lat, lon, weight]."""
    from folium.plugins import HeatMap
    if positions:
        HeatMap(
            positions,
            radius=18,
            blur=12,
            max_zoom=15,
            gradient={"0.4": "#3fb950", "0.65": "#d29922", "1.0": "#f85149"},
        ).add_to(m)
    return m

def add_route_to_map(m, route_coords, orig_name, dest_name):
    import folium
    if not route_coords:
        return m
    folium.PolyLine(
        route_coords,
        color="#58a6ff",
        weight=5,
        opacity=0.9,
        tooltip="Best route",
    ).add_to(m)
    folium.Marker(
        route_coords[0],
        tooltip=f"🏁 Start: {orig_name}",
        icon=folium.Icon(color="green", icon="play", prefix="fa"),
    ).add_to(m)
    folium.Marker(
        route_coords[-1],
        tooltip=f"🏆 End: {dest_name}",
        icon=folium.Icon(color="red", icon="flag", prefix="fa"),
    ).add_to(m)
    return m

def add_vehicles_to_map(m, positions, max_markers=300):
    """Add vehicle dots to map. positions = list of [lat, lon, speed]."""
    import folium
    for lat, lon, speed in positions[:max_markers]:
        color = "#3fb950" if speed > 8 else ("#d29922" if speed > 2 else "#f85149")
        folium.CircleMarker(
            location=[lat, lon],
            radius=3,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
        ).add_to(m)
    return m

# ── helper: action selector ───────────────────────────────────────────────────

def get_action(method, obs, env, step, rf_clf=None, rf_le=None,
               lstm_model=None, lstm_history=None, ppo_model=None):
    n = env.action_space.n
    if method == "Fixed-cycle baseline":
        return (step // 30) % n
    if method == "Greedy adaptive":
        return int(np.argmax(obs[:n]))
    if method == "Random Forest":
        if rf_clf is None:
            return (step // 30) % n
        try:
            import pandas as pd
            from models.random_forest_model import build_features, FEATURE_COLS
            hour = (step * 5 // 3600) % 24
            total_v = float(np.sum(obs[:len(obs) // 2]) * 20)
            df_row = build_features(pd.DataFrame([{"hour": hour, "vehicle_count": total_v, "is_weekend": 0}]))
            label = rf_le.inverse_transform(rf_clf.predict(df_row[FEATURE_COLS].fillna(0)))[0]
            return int(np.argmax(obs[:n])) if label == "congested" else (step // 30) % n
        except Exception:
            return (step // 30) % n
    if method == "LSTM predictor":
        if lstm_model is None or lstm_history is None or len(lstm_history) < 12:
            return (step // 30) % n
        try:
            import torch
            seq = torch.tensor(np.array(lstm_history[-12:], dtype=np.float32)).unsqueeze(0)
            with torch.no_grad():
                pred = lstm_model(seq).numpy()[0]
            return int(np.argmin(pred))
        except Exception:
            return (step // 30) % n
    if method == "PPO (Reinforcement Learning)":
        if ppo_model is None:
            return (step // 30) % n
        action, _ = ppo_model.predict(obs, deterministic=True)
        return int(action)
    return 0

def congestion_label(q):
    return "free" if q < 5 else ("moderate" if q < 12 else "high")

# ── PAGE HEADER ───────────────────────────────────────────────────────────────
st.markdown("<h1>🚦 Mangalore Traffic AI</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#8b949e;font-size:1rem;margin-bottom:.5rem;'>"
    "Physics-based SUMO road simulation + AI traffic light control for Mangalore city.</p>",
    unsafe_allow_html=True,
)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab_map, tab_sim, tab_results = st.tabs([
    "🗺️  Map & Route Finder",
    "🚦  Run Simulation",
    "📊  Results & Analysis",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MAP & ROUTE FINDER
# ══════════════════════════════════════════════════════════════════════════════
with tab_map:
    from streamlit_folium import st_folium

    left, right = st.columns([3, 1], gap="large")

    with right:
        st.markdown("### 🛣️ Route Finder")
        origin_name = st.selectbox("📍 Origin", list(LANDMARKS.keys()), key="origin")
        dest_name   = st.selectbox("🏁 Destination", list(LANDMARKS.keys()), key="dest")
        find_btn    = st.button("Find Best Route", key="route_btn")

        show_heatmap = st.checkbox(
            "Show traffic heatmap",
            value=bool(st.session_state.sim_positions),
            help="Overlay heatmap from the last simulation run.",
        )
        show_vehicles = st.checkbox(
            "Show vehicle snapshot",
            value=False,
            help="Show final-step vehicle positions from last simulation.",
        )

        st.markdown("<hr class='div'>", unsafe_allow_html=True)

        # legend
        st.markdown("""
        **Map legend**
        <div style='font-size:.85rem;color:#8b949e;'>
        🔵 Landmark markers<br>
        🟢 Moving vehicles (speed > 8 m/s)<br>
        🟡 Slow vehicles (2–8 m/s)<br>
        🔴 Stopped vehicles (&lt; 2 m/s)<br>
        🌡️ Heatmap = vehicle density
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.sim_done:
            st.success(f"✅ Last sim: **{st.session_state.sim_method}**")

    with left:
        route_coords   = []
        route_distance = 0
        route_time     = 0

        if find_btn and LANDMARKS.get(origin_name) and LANDMARKS.get(dest_name):
            if origin_name == dest_name:
                st.warning("Origin and destination must be different.")
            else:
                with st.spinner("Computing route…"):
                    G = load_road_graph()
                    if G is not None:
                        import networkx as nx
                        import osmnx as ox
                        orig_lat, orig_lon = LANDMARKS[origin_name]
                        dest_lat, dest_lon = LANDMARKS[dest_name]
                        o_node = ox.nearest_nodes(G, orig_lon, orig_lat)
                        d_node = ox.nearest_nodes(G, dest_lon, dest_lat)
                        try:
                            route_nodes = nx.shortest_path(G, o_node, d_node, weight="length")
                            route_coords = [
                                (G.nodes[n]["y"], G.nodes[n]["x"]) for n in route_nodes
                            ]
                            # distance in metres
                            route_distance = sum(
                                G[u][v][0].get("length", 0)
                                for u, v in zip(route_nodes[:-1], route_nodes[1:])
                            )
                            route_time = (route_distance / 1000) / 30 * 60   # 30 km/h avg
                        except nx.NetworkXNoPath:
                            st.error("No route found between these locations.")
                    else:
                        st.error("Road graph unavailable. Check internet connection.")

                if route_coords:
                    st.success(
                        f"Route found! "
                        f"**{route_distance/1000:.2f} km** — "
                        f"≈ **{route_time:.0f} min** at 30 km/h"
                    )

        # Build and render map
        m = make_base_map(zoom=13)
        m = add_landmarks_to_map(m)

        if show_heatmap and st.session_state.sim_positions:
            all_pos = [p for frame in st.session_state.sim_positions for p in frame]
            heat_pts = [[lat, lon] for lat, lon, *_ in all_pos]
            m = add_heatmap_to_map(m, heat_pts)

        if show_vehicles and st.session_state.sim_positions:
            last_frame = st.session_state.sim_positions[-1]
            m = add_vehicles_to_map(m, last_frame)

        if route_coords:
            m = add_route_to_map(m, route_coords, origin_name, dest_name)
            # Centre on origin
            m.location = list(LANDMARKS[origin_name])

        # Landmark pin highlights
        for name in [origin_name, dest_name]:
            if LANDMARKS.get(name):
                import folium
                lat, lon = LANDMARKS[name]
                folium.Marker(
                    [lat, lon],
                    tooltip=name,
                    icon=folium.Icon(color="blue", icon="map-marker", prefix="fa"),
                ).add_to(m)

        st_folium(m, height=520, use_container_width=True, returned_objects=[])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SIMULATION
# ══════════════════════════════════════════════════════════════════════════════
with tab_sim:
    from streamlit_folium import st_folium as sf2

    # ── controller selection ──────────────────────────────────────────────────
    method_cols = st.columns(len(METHOD_INFO))
    for i, (mname, minfo) in enumerate(METHOD_INFO.items()):
        with method_cols[i]:
            st.markdown(
                f"<div class='info-card' style='text-align:center;padding:.8rem;'>"
                f"<div style='font-size:1.6rem'>{minfo['icon']}</div>"
                f"<b style='color:#c9d1d9;font-size:.82rem;'>{mname}</b><br>"
                f"<span class='badge {minfo['badge']}' style='margin:.3rem 0;display:inline-block;'>"
                f"{minfo['type_label']}</span>"
                f"<p style='font-size:.75rem;margin-top:.3rem;'>{minfo['short']}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    sc1, sc2, sc3 = st.columns([2, 2, 1])
    with sc1:
        method = st.selectbox("🧠 Choose controller", list(METHOD_INFO.keys()))
    with sc2:
        max_steps = st.slider("⏱️ Simulation steps (1 step = 5 s)", 50, 720, 200, step=10)
        use_gui   = st.checkbox("📺 Open SUMO-GUI window")
    with sc3:
        st.markdown("<br>", unsafe_allow_html=True)
        run_btn = st.button("▶  Run Simulation", key="run_sim")

    # method info card
    mi = METHOD_INFO[method]
    st.markdown(
        f"<div class='info-card'>{mi['icon']} <b>{method}</b>"
        f"<span class='badge {mi['badge']}' style='margin-left:.5rem;'>{mi['type_label']}</span>"
        f"<br><span style='font-size:.9rem;'>{mi['long']}</span></div>",
        unsafe_allow_html=True,
    )
    st.markdown("<hr class='div'>", unsafe_allow_html=True)

    if run_btn:
        from controller import SumoTrafficEnv

        # load models
        rf_clf, rf_le, lstm_m, ppo_m = None, None, None, None
        status_ph = st.empty()
        if method == "Random Forest":
            rf_clf, rf_le = load_rf()
            status_ph.info("🌲 Random Forest loaded" if rf_clf else "⚠️ RF not found — using fallback")
        elif method == "LSTM predictor":
            lstm_m = load_lstm()
            status_ph.info("🔮 LSTM loaded" if lstm_m else "⚠️ LSTM not found — using fallback")
        elif method == "PPO (Reinforcement Learning)":
            ppo_m, ppo_path = load_ppo()
            status_ph.info(f"🤖 PPO loaded: {ppo_path}" if ppo_m else "⚠️ PPO not found — using fallback")

        # layout
        map_col, metrics_col = st.columns([3, 1])

        with metrics_col:
            st.markdown("#### 📡 Live Metrics")
            ph_veh  = st.empty()
            ph_phase= st.empty()
            ph_rew  = st.empty()
            ph_cong = st.empty()
            ph_step = st.empty()

        with map_col:
            st.markdown("#### 🗺️ Live Vehicle Map")
            st.caption("🟢 Moving  🟡 Slow  🔴 Stopped")
            map_ph = st.empty()

        prog = st.progress(0, text="Starting SUMO…")

        # ── run env ───────────────────────────────────────────────────────────
        import traci
        env = SumoTrafficEnv(
            config_path="simulation/config.sumocfg",
            use_gui=use_gui,
            max_steps=max_steps * 5,
        )
        obs, _ = env.reset()

        history      = []
        lstm_history = []
        all_pos_frames = []    # list of frames; each frame = [[lat,lon,speed],…]
        MAP_UPDATE_FREQ = max(1, max_steps // 30)   # update map ~30 times total

        done, step = False, 0
        while not done and step < max_steps:
            action = get_action(
                method, obs, env, step,
                rf_clf=rf_clf, rf_le=rf_le,
                lstm_model=lstm_m, lstm_history=lstm_history,
                ppo_model=ppo_m,
            )
            obs, reward, terminated, truncated, info_d = env.step(action)
            done = terminated or truncated

            lc      = info_d["lane_counts"]
            total_q = sum(lc.values())
            phase_n = PHASE_LABELS.get(info_d["current_phase"], f"Phase {info_d['current_phase']}")
            cong    = congestion_label(total_q)

            row = {"step": step, "reward": reward,
                   "phase": info_d["current_phase"], "phase_name": phase_n,
                   "total_vehicles": info_d["total_vehicles"],
                   "total_queue": total_q, "congestion": cong}
            for lane, cnt in lc.items():
                row[f"lane_{lane.split('_')[-1][:8]}"] = cnt
            history.append(row)

            # LSTM feature row
            hour = (step * 5 // 3600) % 24
            lv = list(lc.values())[:4]
            while len(lv) < 4: lv.append(0)
            lstm_history.append([v / 20.0 for v in lv] +
                                  [np.sin(hour*2*np.pi/24), np.cos(hour*2*np.pi/24)])

            # collect vehicle positions from SUMO
            frame_positions = []
            if step % MAP_UPDATE_FREQ == 0:
                try:
                    vids = traci.vehicle.getIDList()
                    for vid in vids[:400]:
                        try:
                            x, y = traci.vehicle.getPosition(vid)
                            lon2, lat2 = traci.simulation.convertGeo(x, y)
                            spd = traci.vehicle.getSpeed(vid)
                            frame_positions.append([lat2, lon2, spd])
                        except Exception:
                            pass
                except Exception:
                    pass
                all_pos_frames.append(frame_positions)

                # update live metrics
                cong_icon = {"free": "🟢", "moderate": "🟡", "high": "🔴"}[cong]
                ph_veh.metric("🚗 Total vehicles", info_d["total_vehicles"])
                ph_phase.metric("🚦 Phase", phase_n)
                ph_rew.metric("🏆 Reward", f"{reward:.4f}")
                ph_cong.metric("📊 Congestion", f"{cong_icon} {cong.title()}")
                ph_step.metric("⏱️ Step", f"{step}/{max_steps}")

                # update live map
                if frame_positions:
                    m2 = make_base_map(zoom=14)
                    m2 = add_vehicles_to_map(m2, frame_positions)
                    with map_ph.container():
                        sf2(m2, height=380, use_container_width=True,
                            returned_objects=[], key=f"lm_{step}")

            step += 1
            prog.progress(step / max_steps, text=f"Step {step}/{max_steps} — {phase_n}")

        env.close()
        prog.empty()
        status_ph.success(f"✅ Simulation complete! {step} steps with **{method}**")

        # save to session state
        st.session_state.sim_df        = pd.DataFrame(history)
        st.session_state.sim_positions = all_pos_frames
        st.session_state.sim_method    = method
        st.session_state.sim_done      = True

        # final heatmap on map
        all_pts = [p for fr in all_pos_frames for p in fr]
        if all_pts:
            m_final = make_base_map(zoom=14)
            m_final = add_heatmap_to_map(m_final, [[p[0], p[1]] for p in all_pts])
            m_final = add_vehicles_to_map(m_final, all_pos_frames[-1] if all_pos_frames else [])
            st.markdown("#### 🌡️ Simulation Traffic Heatmap")
            st.caption("Red = high vehicle density. Go to the 🗺️ Map tab to see it with route finding.")
            with map_ph.container():
                sf2(m_final, height=400, use_container_width=True, returned_objects=[], key="final_map")

        st.info("👉 Check the **📊 Results & Analysis** tab for charts, lane data, and CSV export.")

    elif not run_btn and not st.session_state.sim_done:
        st.markdown("""
        <div class='info-card' style='text-align:center;padding:2.5rem;'>
            <div style='font-size:3rem;'>🚗</div>
            <h3 style='color:#c9d1d9;'>Select a controller above and click ▶ Run Simulation</h3>
            <p>The map will update live with vehicle positions and colour-coded congestion as the simulation runs.</p>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — RESULTS & ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab_results:
    df = st.session_state.sim_df

    if df is None:
        st.markdown("""
        <div class='info-card' style='text-align:center;padding:2rem;'>
            <div style='font-size:2.5rem;'>📊</div>
            <h3 style='color:#c9d1d9;'>No simulation data yet</h3>
            <p>Run a simulation in the 🚦 tab first.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"### Results — {st.session_state.sim_method}")

        # ── summary metrics ───────────────────────────────────────────────────
        mc = st.columns(5)
        mc[0].metric("Steps",           len(df))
        mc[1].metric("Avg reward/step", f"{df['reward'].mean():.4f}")
        mc[2].metric("Avg queue",       f"{df['total_queue'].mean():.1f} cars")
        mc[3].metric("Peak queue",      f"{df['total_queue'].max():.0f} cars")
        mc[4].metric("High-cong steps", f"{(df['congestion']=='high').sum()} / {len(df)}")

        st.markdown("<hr class='div'>", unsafe_allow_html=True)

        # ── Animated step viewer ──────────────────────────────────────────────
        if st.session_state.sim_positions:
            from streamlit_folium import st_folium as sf3
            st.markdown("### 🎬 Vehicle Position Replay")
            st.caption("Scrub through the simulation to see vehicle positions at each captured frame.")
            n_frames = len(st.session_state.sim_positions)
            frame_idx = st.slider("Frame", 0, n_frames - 1, 0, key="frame_slider")
            frame = st.session_state.sim_positions[frame_idx]
            if frame:
                mr = make_base_map(zoom=14)
                mr = add_vehicles_to_map(mr, frame)
                mt_approx = frame_idx * (st.session_state.sim_df["step"].max() / max(n_frames-1, 1))
                st.caption(f"Frame {frame_idx+1}/{n_frames} — approx step {int(mt_approx)}")
                sf3(mr, height=370, use_container_width=True, returned_objects=[], key=f"replay_{frame_idx}")
            else:
                st.info("No vehicle data for this frame (SUMO may not have had vehicles yet).")

            st.markdown("<hr class='div'>", unsafe_allow_html=True)

        # ── charts ────────────────────────────────────────────────────────────
        st.markdown("### 📈 Performance Charts")
        lc1, lc2 = st.columns(2)
        with lc1:
            st.markdown("#### 🏆 Reward over time")
            st.caption("Closer to 0 = fewer waiting cars.")
            st.line_chart(df.set_index("step")[["reward"]], color=["#3fb950"])

            st.markdown("#### 🚗 Total vehicles in simulation")
            st.line_chart(df.set_index("step")[["total_vehicles"]], color=["#58a6ff"])

        lane_cols = [c for c in df.columns if c.startswith("lane_")]
        with lc2:
            if lane_cols:
                st.markdown("#### 🛣️ Queue per lane")
                st.caption("Each line = one road lane entering the junction.")
                st.line_chart(df.set_index("step")[lane_cols])

            st.markdown("#### 🚦 Traffic light phase")
            st.line_chart(df.set_index("step")[["phase"]], color=["#bc8cff"])

        st.markdown("<hr class='div'>", unsafe_allow_html=True)

        # ── congestion timeline ───────────────────────────────────────────────
        st.markdown("### 🔴 Congestion Timeline")
        cong_map = {"free": 0, "moderate": 1, "high": 2}
        df2 = df.copy()
        df2["cong_num"] = df2["congestion"].map(cong_map)
        st.area_chart(df2.set_index("step")[["cong_num"]], color=["#f85149"])
        free_pct = (df["congestion"] == "free").mean() * 100
        hi_pct   = (df["congestion"] == "high").mean() * 100
        st.caption(
            f"🟢 Free: **{free_pct:.1f}%** of steps  |  "
            f"🔴 High congestion: **{hi_pct:.1f}%** of steps"
        )

        st.markdown("<hr class='div'>", unsafe_allow_html=True)

        # ── lane heatmap table ────────────────────────────────────────────────
        if lane_cols:
            st.markdown("### 🌡️ Lane Queue Heatmap (last 100 steps)")
            st.caption("Red = congested lane. Green = free.")
            hm = df[lane_cols].tail(100).T
            st.dataframe(
                hm.style.background_gradient(cmap="RdYlGn_r", axis=1),
                use_container_width=True,
                height=min(42 * len(lane_cols) + 60, 420),
            )

        st.markdown("<hr class='div'>", unsafe_allow_html=True)

        # ── raw data + export ─────────────────────────────────────────────────
        with st.expander("🔍 Raw data (all steps)"):
            st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False)
        st.download_button(
            "⬇️ Download CSV",
            csv,
            f"{st.session_state.sim_method.replace(' ','_')}_results.csv",
            "text/csv",
        )
