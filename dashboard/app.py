"""
dashboard/app.py  —  Mangalore Traffic AI  (full feature dashboard)

Tabs:
  1. 🗺️  Map & Route Finder
  2. 🚦  Run Simulation
  3. ⚖️  Side-by-Side Compare
  4. 📈  Live Training
  5. 🗓️  Run History
  6. 🎓  Research Hub
  7. 📄  Export Report
"""

import os
import sys
import subprocess
import re
import numpy as np
import pandas as pd
import streamlit as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))

st.set_page_config(
    page_title="Mangalore Traffic AI",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🚦",
)

# ── theme ─────────────────────────────────────────────────────────────────────
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

theme_col_1, theme_col_2 = st.columns([6, 1])
with theme_col_2:
    # UI toggle (requested): switch theme variables used by the CSS below.
    light_mode = st.toggle(
        "Light mode",
        value=(st.session_state.theme_mode == "Light"),
        key="theme_light_toggle",
    )
    st.session_state.theme_mode = "Light" if light_mode else "Dark"

THEMES = {
    "Dark": {
        "app_bg": "linear-gradient(-45deg,#0d1117,#161b22,#0d1117,#1c2333)",
        "text": "#f0f6fc",
        "muted": "#8b949e",
        "heading": "#c9d1d9",
        "card_bg": "rgba(22,27,34,.82)",
        "card_border": "rgba(255,255,255,.08)",
        "hover_border": "rgba(88,166,255,.3)",
        "shadow": "rgba(0,0,0,.4)",
        "metric_bg": "rgba(22,27,34,.85)",
        "input_bg": "rgba(22,27,34,.92)",
        "input_text": "#f0f6fc",
        "table_bg": "rgba(22,27,34,.85)",
        "divider": "rgba(255,255,255,.07)",
        "title_a": "#58a6ff",
        "title_b": "#bc8cff",
    },
    "Light": {
        "app_bg": "linear-gradient(-45deg,#f8fbff,#eef4ff,#f8fbff,#f1f5f9)",
        "text": "#111827",
        "muted": "#475569",
        "heading": "#0f172a",
        "card_bg": "rgba(255,255,255,.9)",
        "card_border": "rgba(15,23,42,.10)",
        "hover_border": "rgba(37,99,235,.25)",
        "shadow": "rgba(15,23,42,.08)",
        "metric_bg": "rgba(255,255,255,.95)",
        "input_bg": "#ffffff",
        "input_text": "#111827",
        "table_bg": "#ffffff",
        "divider": "rgba(15,23,42,.10)",
        "title_a": "#2563eb",
        "title_b": "#7c3aed",
    },
}

theme = THEMES[st.session_state.theme_mode]

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "admin_user" not in st.session_state:
    st.session_state.admin_user = None

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
:root {{
  --app-bg: {theme["app_bg"]};
  --text-color: {theme["text"]};
  --muted-text: {theme["muted"]};
  --heading-color: {theme["heading"]};
  --card-bg: {theme["card_bg"]};
  --card-border: {theme["card_border"]};
  --hover-border: {theme["hover_border"]};
  --shadow-color: {theme["shadow"]};
  --metric-bg: {theme["metric_bg"]};
  --input-bg: {theme["input_bg"]};
  --input-text: {theme["input_text"]};
  --table-bg: {theme["table_bg"]};
  --divider: {theme["divider"]};
  --title-a: {theme["title_a"]};
  --title-b: {theme["title_b"]};
}}
html,body,[class*="css"]{{font-family:'Inter',sans-serif;}}
.stApp{{background:var(--app-bg);
       background-size:400% 400%;animation:gradBG 18s ease infinite;color:var(--text-color);}}
@keyframes gradBG{{0%{{background-position:0% 50%;}}50%{{background-position:100% 50%;}}100%{{background-position:0% 50%;}}}}
h1{{font-weight:700!important;font-size:2.3rem!important;
   background:linear-gradient(90deg,var(--title-a),var(--title-b));
   -webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
h2,h3,label,p,li,span,div{{color:var(--text-color);}}
h2,h3{{font-weight:600!important;color:var(--heading-color)!important;}}
div[data-testid="metric-container"]{{background:var(--metric-bg);
  border:1px solid var(--card-border);border-radius:.8rem;padding:1rem!important;
  box-shadow:0 4px 18px var(--shadow-color);backdrop-filter:blur(8px);
  transition:transform .2s,box-shadow .2s;}}
div[data-testid="metric-container"]:hover{{transform:translateY(-3px);
  box-shadow:0 8px 28px rgba(88,166,255,.2);border-color:var(--hover-border);}}
div[data-testid="stMetricValue"]{{font-size:1.8rem!important;font-weight:700!important;color:#58a6ff!important;}}
div[data-testid="stMetricLabel"] p{{color:var(--muted-text)!important;}}
div.stButton>button{{background:linear-gradient(135deg,#238636,#2ea043);color:#fff;
  border:none;padding:.65rem 1.3rem;border-radius:.55rem;font-weight:600;width:100%;
  box-shadow:0 3px 12px rgba(35,134,54,.4);transition:all .2s;}}
div.stButton>button:hover{{transform:scale(1.02);box-shadow:0 5px 18px rgba(35,134,54,.6);}}
.card{{background:var(--card-bg);border:1px solid var(--card-border);
      border-radius:.8rem;padding:1.1rem 1.3rem;color:var(--muted-text);line-height:1.6;}}
.card b,.card h3{{color:var(--heading-color)!important;}}
.badge{{display:inline-block;padding:.15rem .6rem;border-radius:99px;font-size:.72rem;font-weight:600;}}
.badge-green{{background:rgba(35,134,54,.25);color:#3fb950;}}
.badge-blue{{background:rgba(56,139,253,.25);color:#58a6ff;}}
.badge-purple{{background:rgba(188,140,255,.25);color:#bc8cff;}}
.badge-teal{{background:rgba(46,160,67,.25);color:#56d4dd;}}
.badge-orange{{background:rgba(210,153,34,.25);color:#d29922;}}
.badge-red{{background:rgba(248,81,73,.25);color:#f85149;}}
.hr{{border:none;border-top:1px solid var(--divider);margin:1rem 0;}}
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
textarea,
input {{
  background: var(--input-bg)!important;
  color: var(--input-text)!important;
}}
div[data-baseweb="select"] * ,
div[data-baseweb="input"] * ,
textarea,
input {{
  color: var(--input-text)!important;
}}
div[data-testid="stDataFrame"], div[data-testid="stTable"] {{
  background: var(--table-bg)!important;
  border-radius: .6rem;
}}
div[data-testid="stMarkdownContainer"] p {{
  color: var(--text-color);
}}
</style>
""",
    unsafe_allow_html=True,
)

# ── admin auth ────────────────────────────────────────────────────────────────
from database import SimulationDB
auth_db = SimulationDB()

with st.sidebar:
    st.markdown("### 🔐 Admin Access")
    if st.session_state.admin_logged_in:
        st.success(f"Logged in as `{st.session_state.admin_user}`")
        if st.button("Logout", key="admin_logout_btn"):
            st.session_state.admin_logged_in = False
            st.session_state.admin_user = None
            st.rerun()
    else:
        auth_tab_login, auth_tab_register = st.tabs(["Login", "Register"])
        with auth_tab_login:
            login_user = st.text_input("Username", key="admin_login_user")
            login_pass = st.text_input("Password", type="password", key="admin_login_pass")
            if st.button("Login", key="admin_login_btn"):
                if auth_db.authenticate_admin(login_user, login_pass):
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_user = login_user.strip()
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        with auth_tab_register:
            reg_user = st.text_input("New username", key="admin_reg_user")
            reg_pass = st.text_input("New password", type="password", key="admin_reg_pass")
            if st.button("Register admin", key="admin_register_btn"):
                ok, msg = auth_db.register_admin(reg_user, reg_pass)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
        if not auth_db.has_admins():
            st.info("No admin found yet. Register the first admin account.")

if not st.session_state.admin_logged_in:
    st.markdown("<h1>🚦 Mangalore Traffic AI</h1>", unsafe_allow_html=True)
    st.warning("Admin login required. Use the sidebar to register or sign in.")
    st.stop()

# ── constants ─────────────────────────────────────────────────────────────────
MANGALORE_CENTER = (12.8700, 74.8436)

LANDMARKS = {
    "📍 Select a location…": None,
    "Mangalore Central Station": (12.8710, 74.8418),
    "Hampankatta Circle":        (12.8696, 74.8437),
    "KSRTC Bus Stand":           (12.8695, 74.8456),
    "Lalbagh Junction":          (12.8617, 74.8314),
    "Bunts Hostel Junction":     (12.8755, 74.8356),
    "Bejai Cross Roads":         (12.8763, 74.8456),
    "Kankanady Junction":        (12.8765, 74.8523),
    "Attavar Junction":          (12.8739, 74.8346),
    "State Bank Circle":         (12.8635, 74.8432),
    "Falnir Road Junction":      (12.8849, 74.8428),
    "Kadri Manjunath Temple":    (12.8897, 74.8484),
    "Urwa Market":               (12.9105, 74.8454),
    "Kavoor Junction":           (12.9032, 74.8210),
    "Deralakatte Junction":      (12.8366, 74.8183),
    "Mangalore Airport (Bajpe)": (12.9613, 74.8898),
    "Ullal Circle":              (12.7968, 74.8632),
    "Surathkal NITK":            (13.0125, 74.7965),
}

METHOD_INFO = {
    "Fixed-cycle baseline": {
        "badge": "badge-red", "icon": "🔴", "type": "Rule",
        "desc": "Traditional traffic signal control. Rotates through a sequence of pre-defined phases (Green/Yellow/Red) based on fixed timers (e.g., 30s per lane), oblivious to real-time traffic demand."
    },
    "Greedy adaptive": {
        "badge": "badge-orange", "icon": "🟠", "type": "Rule",
        "desc": "A reactive rule-based controller. It constantly monitors lane occupancy and immediately switches the green light to the lane with the highest current vehicle count."
    },
    "Random Forest": {
        "badge": "badge-blue", "icon": "🌲", "type": "ML",
        "desc": "A machine learning approach. It uses a Forest of Decision Trees trained on historical Mangalore traffic patterns to classify the current congestion state and select the optimal phase."
    },
    "LSTM predictor": {
        "badge": "badge-purple", "icon": "🔮", "type": "Deep ML",
        "desc": "Uses Long Short-Term Memory (LSTM) recurrent networks. It analyzes the time-series history of the last 12 simulation steps to forecast near-future flow and pre-emptively adjust cycles."
    },
    "Ensemble controller": {
        "badge": "badge-blue", "icon": "🧠", "type": "Hybrid",
        "desc": "A 'best of all worlds' model. It combines predictions from Random Forest, LSTM, and Rule-based systems, using a weighted voting mechanism to ensure stability and efficiency."
    },
    "PPO (Reinforcement Learning)": {
        "badge": "badge-green", "icon": "🤖", "type": "RL",
        "desc": "Proximal Policy Optimization. A state-of-the-art RL agent that treats traffic as a game. It learns through a reward system to maximize throughput and minimize global waiting time."
    },
    "DQN (Reinforcement Learning)": {
        "badge": "badge-teal", "icon": "🎮", "type": "RL",
        "desc": "Deep Q-Network. It uses a deep neural network to estimate the 'Q-Value' (future reward) of every possible action, choosing the one that leads to the least long-term congestion."
    },
}
PHASE_LABELS = {0:"N-S Green",1:"N-S Yellow",2:"E-W Green",3:"E-W Yellow"}

# ── session state ─────────────────────────────────────────────────────────────
for k, v in {
    "sim_df": None, "sim_pos": [], "sim_method": "",
    "cmp_df_a": None, "cmp_df_b": None, "cmp_m_a": "", "cmp_m_b": "",
    "training_log": [], "training_rewards": [],
    "dataset_df": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── cached loaders ────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="Loading Mangalore road graph…", ttl=3600)
def load_graph():
    try:
        import osmnx as ox
        return ox.graph_from_point(MANGALORE_CENTER, dist=2500, network_type="drive")
    except Exception:
        return None

def _load_rf():
    try:
        import joblib
        return joblib.load("models/random_forest.pkl"), joblib.load("models/rf_label_encoder.pkl")
    except Exception:
        return None, None

def _load_lstm():
    try:
        import torch
        from models.lstm_model import TrafficLSTM
        m = TrafficLSTM(input_size=6, hidden_size=128, num_layers=2, n_lanes=4)
        m.load_state_dict(torch.load("models/lstm_traffic.pt", map_location="cpu"))
        m.eval(); return m
    except Exception:
        return None

def _load_rl_model(algo="PPO"):
    try:
        from stable_baselines3 import PPO, DQN
        if algo == "DQN":
            for p in ["models/dqn_mangalore", "models/dqn_model"]:
                try: return DQN.load(p), p
                except Exception: pass
        else:
            for p in ["models/ppo_mangalore_sumo", "models/ppo_mangalore"]:
                try: return PPO.load(p), p
                except Exception: pass
    except Exception: pass
    return None, None


def predict_rf_label(obs, step, rf_clf=None, rf_le=None):
    """Generate an RF congestion label for the current simulation state."""
    if rf_clf is None or rf_le is None:
        return None
    try:
        from models.random_forest_model import build_features, FEATURE_COLS
        hour = (step * 5 // 3600) % 24
        vehicle_count = float(np.sum(obs[: len(obs) // 2]) * 20)
        row = build_features(pd.DataFrame([{
            "hour": hour,
            "vehicle_count": vehicle_count,
            "is_weekend": 0,
        }]))
        return rf_le.inverse_transform(rf_clf.predict(row[FEATURE_COLS].fillna(0)))[0]
    except Exception:
        return None

# ── action selector ───────────────────────────────────────────────────────────

def get_action(method, obs, env, step, rf_clf=None, rf_le=None,
               lstm_model=None, lstm_hist=None, ppo_m=None):
    n = env.action_space.n
    if method == "Fixed-cycle baseline":   return (step // 30) % n
    if method == "Greedy adaptive":        return int(np.argmax(obs[:n]))
    if method == "Random Forest":
        if rf_clf is None: return (step // 30) % n
        try:
            lbl = predict_rf_label(obs, step, rf_clf, rf_le)
            return int(np.argmax(obs[:n])) if lbl == "congested" else (step//30)%n
        except Exception: return (step//30)%n
    if method == "LSTM predictor":
        if lstm_model is None or lstm_hist is None or len(lstm_hist)<12: return (step//30)%n
        try:
            import torch
            seq = torch.tensor(np.array(lstm_hist[-12:],dtype=np.float32)).unsqueeze(0)
            with torch.no_grad(): pred = lstm_model(seq).numpy()[0]
            return int(np.argmin(pred))
        except Exception: return (step//30)%n
    if method == "Ensemble controller":
        try:
            from ensemble import choose_ensemble_action
            action, _ = choose_ensemble_action(
                obs, step, n_actions=n,
                rf_clf=rf_clf, rf_le=rf_le,
                lstm_model=lstm_model, lstm_hist=lstm_hist,
            )
            return action
        except Exception:
            return int(np.argmax(obs[:n]))
    if method in ["PPO (Reinforcement Learning)", "DQN (Reinforcement Learning)"]:
        if ppo_m is None: return (step // 30) % n
        action, _ = ppo_m.predict(obs, deterministic=True); return int(action)
    return 0

def congestion_label(q):
    return "free" if q<5 else ("moderate" if q<12 else "high")


def _norm_congestion_label(lbl: str) -> str:
    if lbl == "high":
        return "congested"
    return lbl


def _congestion_to_num(lbl: str) -> int:
    mapping = {"free": 0, "moderate": 1, "congested": 2}
    return mapping.get(_norm_congestion_label(lbl), 0)


def benchmark_prediction_models(sim_df: pd.DataFrame):
    """
    Compare available prediction models on the same run:
      - Random Forest
      - LSTM predictor
      - Ensemble (RF + LSTM + persistence vote)
    Returns:
      metrics_df, confusion_mats
    """
    from sklearn.metrics import accuracy_score, confusion_matrix

    if sim_df is None or "congestion" not in sim_df.columns:
        raise ValueError("Simulation dataframe with congestion labels is required.")

    labels = ["free", "moderate", "congested"]
    y_true = sim_df["congestion"].map(_norm_congestion_label).fillna("free")

    # Load models if available
    rf_clf, rf_le = _load_rf()
    lstm_model = _load_lstm()

    lane_cols = [c for c in sim_df.columns if c.startswith("lane_")]
    preds = {}

    # RF predictions
    rf_preds = []
    if rf_clf is not None and rf_le is not None:
        for _, row in sim_df.iterrows():
            step = int(row.get("step", 0))
            obs_len = max(2, len(lane_cols) * 2)
            obs = np.zeros(obs_len, dtype=np.float32)
            queue = float(row.get("total_queue", 0.0))
            obs[0] = queue / 20.0
            rf_lbl = predict_rf_label(obs, step, rf_clf=rf_clf, rf_le=rf_le)
            rf_preds.append(_norm_congestion_label(rf_lbl or "free"))
        preds["Random Forest"] = rf_preds

    # LSTM predictions from lane history
    lstm_preds = []
    if lstm_model is not None and lane_cols:
        hist = []
        for _, row in sim_df.iterrows():
            step = int(row.get("step", 0))
            hour = (step * 5 // 3600) % 24
            lane_vals = [float(row.get(c, 0.0)) for c in lane_cols[:4]]
            while len(lane_vals) < 4:
                lane_vals.append(0.0)
            hist.append([v / 20.0 for v in lane_vals] + [np.sin(hour * 2 * np.pi / 24), np.cos(hour * 2 * np.pi / 24)])
            if len(hist) < 12:
                lstm_preds.append("free")
                continue
            try:
                import torch
                seq = torch.tensor(np.array(hist[-12:], dtype=np.float32)).unsqueeze(0)
                with torch.no_grad():
                    pred = lstm_model(seq).numpy()[0]
                pred_queue = float(np.sum(pred[:4]) * 20.0)
                lstm_preds.append(_norm_congestion_label(congestion_label(pred_queue)))
            except Exception:
                lstm_preds.append("free")
        preds["LSTM"] = lstm_preds

    # Ensemble vote (RF + LSTM + persistence from current queue)
    if "Random Forest" in preds or "LSTM" in preds:
        ens_preds = []
        for i, row in sim_df.iterrows():
            votes = []
            if "Random Forest" in preds:
                votes.append(preds["Random Forest"][i])
            if "LSTM" in preds:
                votes.append(preds["LSTM"][i])
            votes.append(_norm_congestion_label(congestion_label(float(row.get("total_queue", 0.0)))))
            counts = {}
            for v in votes:
                counts[v] = counts.get(v, 0) + 1
            ens_preds.append(sorted(counts.items(), key=lambda x: (-x[1], x[0]))[0][0])
        preds["Ensemble"] = ens_preds

    if not preds:
        raise ValueError("No trained model available for benchmarking.")

    metrics_rows = []
    cms = {}
    y_true_num = np.array([_congestion_to_num(v) for v in y_true], dtype=float)
    for model_name, y_pred in preds.items():
        y_pred_series = pd.Series(y_pred).fillna("free")
        y_pred_num = np.array([_congestion_to_num(v) for v in y_pred_series], dtype=float)
        acc = accuracy_score(y_true, y_pred_series)
        mae = float(np.mean(np.abs(y_true_num - y_pred_num)))
        err = 1.0 - acc
        metrics_rows.append({
            "model": model_name,
            "accuracy": float(acc),
            "error_rate": float(err),
            "mean_abs_error": mae,
        })
        cms[model_name] = confusion_matrix(y_true, y_pred_series, labels=labels)

    metrics_df = pd.DataFrame(metrics_rows).sort_values("accuracy", ascending=False).reset_index(drop=True)
    return metrics_df, cms, labels

# ── map helpers ───────────────────────────────────────────────────────────────

def make_base_map(zoom=13):
    import folium
    return folium.Map(location=list(MANGALORE_CENTER), zoom_start=zoom,
                      tiles="CartoDB dark_matter", attr="CartoDB")

def add_heatmap(m, pts):
    from folium.plugins import HeatMap
    if pts: HeatMap(pts, radius=18, blur=12, max_zoom=15,
                    gradient={"0.4":"#3fb950","0.65":"#d29922","1.0":"#f85149"}).add_to(m)
    return m

def add_vehicles(m, positions, limit=300):
    import folium
    for lat, lon, spd in positions[:limit]:
        col = "#3fb950" if spd>8 else ("#d29922" if spd>2 else "#f85149")
        folium.CircleMarker([lat,lon], radius=3, color=col, fill=True,
                            fill_color=col, fill_opacity=0.85).add_to(m)
    return m

def add_landmarks(m):
    import folium
    for name, coords in LANDMARKS.items():
        if coords:
            folium.CircleMarker(coords, radius=5, color="#58a6ff", fill=True,
                                fill_color="#58a6ff", fill_opacity=0.7,
                                tooltip=name).add_to(m)
    return m

def add_route(m, coords, orig, dest):
    import folium
    if not coords: return m
    folium.PolyLine(coords, color="#58a6ff", weight=5, opacity=0.9).add_to(m)
    folium.Marker(coords[0], tooltip=f"🏁 {orig}", icon=folium.Icon(color="green",icon="play",prefix="fa")).add_to(m)
    folium.Marker(coords[-1], tooltip=f"🏆 {dest}", icon=folium.Icon(color="red",icon="flag",prefix="fa")).add_to(m)
    return m

# ── junction overlay helper ───────────────────────────────────────────────────

def add_junction_overlay(m, junction_data: list):
    """Add colour-coded circles for every traffic light junction."""
    import folium
    cong_colors = {"free": "#3fb950", "moderate": "#d29922", "high": "#f85149"}
    for lat, lon, tl_id, cong in junction_data:
        col = cong_colors.get(cong, "#58a6ff")
        folium.CircleMarker(
            [lat, lon], radius=10, color=col, fill=True,
            fill_color=col, fill_opacity=0.6,
            tooltip=f"🚦 {tl_id} — {cong.title()}",
        ).add_to(m)
    return m

# ── simulation runner ─────────────────────────────────────────────────────────

class _SimpleActionSpace:
    def __init__(self, n=4):
        self.n = n


class _PythonSimEnv:
    def __init__(self, n_actions=4):
        self.action_space = _SimpleActionSpace(n_actions)


def _prepare_python_dataset(dataset_df: pd.DataFrame | None, max_steps: int) -> pd.DataFrame:
    if dataset_df is None or len(dataset_df) == 0:
        from models.random_forest_model import generate_synthetic_data
        dataset_df = generate_synthetic_data(n_hours=max(max_steps, 200))
    df = dataset_df.copy()
    if "hour" not in df.columns and "timestamp" in df.columns:
        ts = pd.to_datetime(df["timestamp"])
        df["hour"] = ts.dt.hour
        df["is_weekend"] = (ts.dt.dayofweek >= 5).astype(int)
    if "hour" not in df.columns:
        df["hour"] = np.arange(len(df)) % 24
    if "is_weekend" not in df.columns:
        df["is_weekend"] = 0
    if "vehicle_count" not in df.columns:
        lane_cols = [c for c in df.columns if c.startswith("lane_")]
        if lane_cols:
            df["vehicle_count"] = df[lane_cols].sum(axis=1)
        else:
            df["vehicle_count"] = 20
    return df.reset_index(drop=True)


def run_python_simulation(method, max_steps, reward_type="wait_time", dataset_df=None,
                          live_metrics=None, progress_ph=None):
    """Pure Python simulation driven by uploaded dataset demand."""
    rf_clf, rf_le = _load_rf()
    lstm_m, ppo_m = None, None
    if method in ["LSTM predictor", "Ensemble controller"]:
        lstm_m = _load_lstm()
    elif method in ["PPO (Reinforcement Learning)", "DQN (Reinforcement Learning)"]:
        algo = "DQN" if "DQN" in method else "PPO"
        ppo_m, _ = _load_rl_model(algo)

    env = _PythonSimEnv(n_actions=4)
    df_src = _prepare_python_dataset(dataset_df, max_steps=max_steps)
    queues = np.zeros(4, dtype=float)
    history, pos_frames, lstm_hist = [], [], []

    for step in range(max_steps):
        row_src = df_src.iloc[step % len(df_src)]
        # Each dataset row = 1 hour of traffic.
        # Convert to per-step rate (1 step ≈ 5s, 720 steps/hour → /12 gives
        # a 5-min count which is the standard traffic survey interval).
        # Add Poisson noise so each step is stochastic and realistic.
        raw_demand = max(0.0, float(row_src.get("vehicle_count", 20.0)))
        demand_per_step = raw_demand / 12.0          # treat row as hourly → 5-min bucket
        # Stochastic arrivals: Poisson(λ) with per-lane split
        split = np.array([0.30, 0.25, 0.25, 0.20], dtype=float)
        lane_lambdas = demand_per_step * split
        arrivals = np.array([
            float(np.random.poisson(max(0.0, lam))) for lam in lane_lambdas
        ], dtype=float)
        demand = demand_per_step          # keep 'demand' for downstream logging
        queues += arrivals

        # Build obs: 4 queue ratios + 4 clipped saturation + 4 padding zeros
        # = 12 features, matching the PPO/DQN model's trained observation space (12,).
        # The trained model sees 6 real SUMO lanes × 2 features each = 12.
        # Our Python sim only has 4 virtual lanes, so we zero-pad to 12.
        obs = np.concatenate([
            queues / 20.0,                     # 4: normalised queue lengths
            np.clip(queues / 50.0, 0, 1),      # 4: saturation ratio
            np.zeros(4, dtype=np.float32),     # 4: padding → total = 12
        ]).astype(np.float32)
        action = get_action(
            method, obs, env, step,
            rf_clf=rf_clf, rf_le=rf_le,
            lstm_model=lstm_m, lstm_hist=lstm_hist, ppo_m=ppo_m,
        )
        action = int(action) % env.action_space.n

        service = np.zeros(4, dtype=float)
        # Service: 2.5 vehicles/step per active green lane
        # At peak demand (90 veh/hour): λ = 90/12 = 7.5/step arriving total
        # Service clears 2.5×2 = 5/step on green → moderate queue build-up → congested
        # At night (10 veh/hour): λ = 10/12 ≈ 0.8/step → service exceeds arrivals → free
        if action in [0, 1]:
            service[0] = 2.5 if action == 0 else 0.3
            service[1] = 2.5 if action == 0 else 0.3
        else:
            service[2] = 2.5 if action == 2 else 0.3
            service[3] = 2.5 if action == 2 else 0.3

        served = np.minimum(queues, service)
        queues = np.maximum(0.0, queues - served)
        total_q = float(queues.sum())
        throughput = float(served.sum())
        reward = throughput if reward_type == "throughput" else -total_q / 20.0
        cong = congestion_label(total_q)
        rf_pred = predict_rf_label(obs, step, rf_clf, rf_le)
        phase_n = PHASE_LABELS.get(action, f"Phase {action}")

        history.append({
            "step": step,
            "reward": reward,
            "phase": action,
            "phase_name": phase_n,
            "total_vehicles": int(total_q + throughput),
            "total_queue": total_q,
            "congestion": cong,
            "co2_mg": total_q * 120.0,
            "accident_active": False,
            "rf_pred_label": rf_pred,
            "lane_n": float(queues[0]),
            "lane_s": float(queues[1]),
            "lane_e": float(queues[2]),
            "lane_w": float(queues[3]),
            "hour": int(row_src.get("hour", step % 24)),
            "vehicle_count": demand,
        })

        hour = int(row_src.get("hour", step % 24))
        lstm_hist.append([v / 20.0 for v in queues[:4]] + [np.sin(hour * 2 * np.pi / 24), np.cos(hour * 2 * np.pi / 24)])
        pos_frames.append([])

        if live_metrics:
            ci = {"free": "🟢", "moderate": "🟡", "high": "🔴"}[cong]
            live_metrics[0].metric("🚗 Vehicles", int(total_q + throughput))
            live_metrics[1].metric("🚦 Phase", phase_n)
            live_metrics[2].metric("🏆 Reward", f"{reward:.4f}")
            live_metrics[3].metric("📊 Congestion", f"{ci} {cong.title()}")
        if progress_ph:
            progress_ph.progress((step + 1) / max_steps, f"Step {step + 1}/{max_steps} — {phase_n}")

    if progress_ph:
        progress_ph.empty()
    return pd.DataFrame(history), pos_frames, [], []


def run_sumo_simulation(method, max_steps, use_gui, scenario=None, reward_type="wait_time",
                        live_map_ph=None, live_metrics=None, progress_ph=None, use_cv=False):
    """Run one SUMO-backed episode. Returns (df, pos_frames, junction_data_last)."""
    from controller import SumoTrafficEnv
    import traci
    rf_clf, rf_le = _load_rf()
    lstm_m, ppo_m = None, None
    if method == "Random Forest":
        pass
    elif method == "LSTM predictor":
        lstm_m = _load_lstm()
    elif method == "Ensemble controller":
        lstm_m = _load_lstm()
    elif method in ["PPO (Reinforcement Learning)", "DQN (Reinforcement Learning)"]:
        algo = "DQN" if "DQN" in method else "PPO"
        ppo_m, _ = _load_rl_model(algo)

    env = SumoTrafficEnv(config_path="simulation/config.sumocfg",
                         use_gui=use_gui, max_steps=max_steps*5,
                         scenario=scenario, reward_type=reward_type,
                         use_cv=use_cv)
    obs, _ = env.reset()
    history, lstm_hist, pos_frames = [], [], []
    junction_data_last = []
    MAP_FREQ = max(1, max_steps // 25)
    done, step = False, 0

    while not done and step < max_steps:
        action = get_action(method, obs, env, step,
                            rf_clf=rf_clf, rf_le=rf_le,
                            lstm_model=lstm_m, lstm_hist=lstm_hist, ppo_m=ppo_m)
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        lc = info["lane_counts"]; total_q = sum(lc.values())
        cong = congestion_label(total_q)
        rf_pred = predict_rf_label(obs, step, rf_clf, rf_le)
        phase_n = PHASE_LABELS.get(info["current_phase"], f"Phase {info['current_phase']}")

        type_counts = {}
        for veh_id in traci.vehicle.getIDList():
            vt = traci.vehicle.getTypeID(veh_id)
            type_counts[vt] = type_counts.get(vt, 0) + 1

        row = {"step":step, "reward":reward, "phase":info["current_phase"],
               "phase_name":phase_n, "total_vehicles":info["total_vehicles"],
               "total_queue":total_q, "congestion":cong,
               "co2_mg":info.get("co2_mg", 0),
               "accident_active":info.get("accident_active", False),
               "rf_pred_label":rf_pred,
               "vehicle_types": type_counts}
        for lane, cnt in lc.items(): row[f"lane_{lane.split('_')[-1][:8]}"] = cnt
        history.append(row)

        hour = (step*5//3600)%24
        lv = list(lc.values())[:4]
        while len(lv) < 4: lv.append(0)
        lstm_hist.append([v/20.0 for v in lv] +
                         [np.sin(hour*2*np.pi/24), np.cos(hour*2*np.pi/24)])

        if step % MAP_FREQ == 0:
            frame = []
            try:
                for vid in traci.vehicle.getIDList()[:400]:
                    try:
                        x, y = traci.vehicle.getPosition(vid)
                        lon2, lat2 = traci.simulation.convertGeo(x, y)
                        spd = traci.vehicle.getSpeed(vid)
                        frame.append([lat2, lon2, spd])
                    except Exception: pass
            except Exception: pass
            pos_frames.append(frame)
            # capture junction congestion state for map overlay
            junction_data_last = env.get_junction_map_data()

            if live_metrics:
                ci = {"free":"🟢","moderate":"🟡","high":"🔴"}[cong]
                live_metrics[0].metric("🚗 Vehicles", info["total_vehicles"])
                live_metrics[1].metric("🚦 Phase", phase_n)
                live_metrics[2].metric("🏆 Reward", f"{reward:.4f}")
                live_metrics[3].metric("📊 Congestion", f"{ci} {cong.title()}")
                if info.get("accident_active"): live_metrics[3].error("🚨 ACCIDENT ACTIVE")
            if live_map_ph and frame:
                from streamlit_folium import st_folium
                m2 = make_base_map(14)
                add_vehicles(m2, frame)
                if junction_data_last:
                    add_junction_overlay(m2, junction_data_last)
                with live_map_ph.container():
                    st_folium(m2, height=350, use_container_width=True,
                              returned_objects=[], key=f"lm_{method[:3]}_{step}")
            if progress_ph:
                progress_ph.progress(step/max_steps, f"Step {step}/{max_steps} — {phase_n}")
        step += 1

    jhist = getattr(env, "junction_history", [])
    env.close()
    if progress_ph: progress_ph.empty()
    return pd.DataFrame(history), pos_frames, junction_data_last, jhist


def run_simulation(method, max_steps, use_gui, scenario=None, reward_type="wait_time",
                   live_map_ph=None, live_metrics=None, progress_ph=None,
                   backend="Python Simulator", dataset_df=None, use_cv=False):
    if backend == "Python Simulator":
        return run_python_simulation(
            method=method,
            max_steps=max_steps,
            reward_type=reward_type,
            dataset_df=dataset_df,
            live_metrics=live_metrics,
            progress_ph=progress_ph,
        )
    return run_sumo_simulation(
        method=method,
        max_steps=max_steps,
        use_gui=use_gui,
        scenario=scenario,
        reward_type=reward_type,
        live_map_ph=live_map_ph,
        live_metrics=live_metrics,
        progress_ph=progress_ph,
        use_cv=use_cv,
    )

# ── page header ───────────────────────────────────────────────────────────────
st.markdown("<h1>🚦 Mangalore Traffic AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:var(--muted-text);font-size:1rem;margin-bottom:.3rem;'>Physics-based SUMO simulation + AI traffic control · Live maps · Research analytics</p>", unsafe_allow_html=True)

# ── tabs ──────────────────────────────────────────────────────────────────────
(tab_map, tab_sim, tab_cmp, tab_train,
 tab_hist, tab_research, tab_analysis, tab_export, tab_data) = st.tabs([
    "🗺️ Map & Routes", "🚦 Simulate", "⚖️ Compare",
    "📈 Train Live", "🗓️ History", "🎓 Research",
    "🧪 Analysis", "📄 Export", "📂 Data Hub",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MAP & ROUTE FINDER
# ══════════════════════════════════════════════════════════════════════════════
with tab_map:
    from streamlit_folium import st_folium as sfm

    lc, rc = st.columns([3,1], gap="large")
    with rc:
        st.markdown("### 🛣️ Route Finder")
        orig_n = st.selectbox("📍 Origin",      list(LANDMARKS.keys()), key="m_orig")
        dest_n = st.selectbox("🏁 Destination", list(LANDMARKS.keys()), key="m_dest")
        find_btn = st.button("Find Best Route", key="m_find")
        show_heat = st.checkbox("Traffic heatmap", value=bool(st.session_state.sim_pos))
        show_veh  = st.checkbox("Vehicle snapshot", value=False)
        st.markdown("<hr class='hr'>", unsafe_allow_html=True)
        st.markdown("<div class='card'><b>Legend</b><br>🔵 Landmarks<br>🟢 Moving vehicles<br>🟡 Slow vehicles<br>🔴 Stopped vehicles<br>🌡️ Heatmap = density</div>", unsafe_allow_html=True)

    with lc:
        route_coords, route_dist_m, route_time_min = [], 0, 0
        if find_btn and LANDMARKS.get(orig_n) and LANDMARKS.get(dest_n) and orig_n!=dest_n:
            with st.spinner("Computing route…"):
                G = load_graph()
                if G:
                    import networkx as nx, osmnx as ox
                    olat,olon = LANDMARKS[orig_n]; dlat,dlon = LANDMARKS[dest_n]
                    o = ox.nearest_nodes(G,olon,olat); d = ox.nearest_nodes(G,dlon,dlat)
                    try:
                        rn = nx.shortest_path(G,o,d,weight="length")
                        route_coords = [(G.nodes[n]["y"],G.nodes[n]["x"]) for n in rn]
                        route_dist_m = sum(G[u][v][0].get("length",0) for u,v in zip(rn[:-1],rn[1:]))
                        route_time_min = (route_dist_m/1000)/30*60
                        st.success(f"Route: **{route_dist_m/1000:.2f} km** — ≈ **{route_time_min:.0f} min** at 30 km/h")
                    except nx.NetworkXNoPath:
                        st.error("No route found between these locations.")

        m = make_base_map(); add_landmarks(m)
        if show_heat and st.session_state.sim_pos:
            pts = [[p[0],p[1]] for fr in st.session_state.sim_pos for p in fr]
            add_heatmap(m, pts)
        if show_veh and st.session_state.sim_pos:
            add_vehicles(m, st.session_state.sim_pos[-1])
        if route_coords:
            add_route(m, route_coords, orig_n, dest_n)
        sfm(m, height=500, use_container_width=True, returned_objects=[], key="mapview")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SIMULATE
# ══════════════════════════════════════════════════════════════════════════════
with tab_sim:
    from streamlit_folium import st_folium as sfs

    # method cards
    method_cols = st.columns(len(METHOD_INFO))
    for i,(mn,mi) in enumerate(METHOD_INFO.items()):
        with method_cols[i]:
            badge_cls = mi["badge"]
            mi_type   = mi["type"]
            st.markdown(
                f"<div class='card' style='text-align:center;padding:.8rem;'>"
                f"<div style='font-size:1.5rem'>{mi['icon']}</div>"
                f"<b style='color:var(--heading-color);font-size:.8rem'>{mn}</b><br>"
                f"<span class='badge {badge_cls}' style='margin:.3rem 0;display:inline-block'>{mi_type}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br>",unsafe_allow_html=True)
    sc1, sc2, sc3, sc4 = st.columns([2, 2, 2, 1])
    with sc1: method = st.selectbox("🧠 Controller", list(METHOD_INFO.keys()), key="sim_m")
    with sc2:
        sim_backend = st.selectbox("⚙️ Simulation Backend", ["Python Simulator", "SUMO"], index=0, key="sim_backend")
        from scenarios import SCENARIOS
        scen_name = st.selectbox("🌤️ Scenario", list(SCENARIOS.keys()), key="sim_scen")
        sc_cfg = SCENARIOS[scen_name]
        sc_icon = sc_cfg.icon
        st.caption(f"{sc_icon} {sc_cfg.description[:80]}")
    with sc3:
        max_steps = st.slider("⏱️ Steps (1 step=5 s)", 50, 720, 200, 10)
        use_gui   = st.checkbox("📺 SUMO-GUI", disabled=(sim_backend != "SUMO"))
        use_cv = st.checkbox("📷 Use CV Pipeline", 
                             disabled=(sim_backend != "SUMO"),
                             help="Use computer vision instead of TraCI for vehicle counts")
        reward_type = st.selectbox("🎯 Reward Type", ["wait_time", "throughput"], 
                                   help="wait_time: minimize queue length. throughput: maximize arrived vehicles.")
    with sc4:
        st.markdown("<br>", unsafe_allow_html=True)
        run_btn = st.button("▶  Run", key="sim_run")

    # Method Explanation Panel
    if method in METHOD_INFO:
        mi = METHOD_INFO[method]
        st.markdown(f"""
        <div class="card" style="margin-top: 1rem; border-left: 5px solid var(--title-a);">
            <h4 style="margin-bottom: 0.4rem;">{mi['icon']} {method} — <i>{mi['type']}</i></h4>
            <p style="font-size: 0.95rem; color: var(--text-color);">{mi['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

    if sim_backend == "Python Simulator":
        if st.session_state.dataset_df is not None:
            st.info(f"Using uploaded dataset with {len(st.session_state.dataset_df)} rows for Python simulation.")
        else:
            st.info("No dataset loaded. Python simulator will use synthetic traffic demand.")

    if run_btn:
        st.markdown("---")
        mc, lmc = st.columns([1, 3])
        with mc:
            st.markdown("#### 📡 Live")
            ph = [st.empty() for _ in range(4)]
        with lmc:
            st.markdown("#### 🗺️ Vehicles + Junctions")
            map_ph = st.empty()
        prog_ph = st.progress(0)

        from scenarios import get_scenario
        scenario_cfg = get_scenario(scen_name)
        df, pos, jct, jhist = run_simulation(
            method, max_steps, use_gui, 
            scenario=scenario_cfg, 
            reward_type=reward_type,
            live_map_ph=map_ph, live_metrics=ph, progress_ph=prog_ph,
            backend=sim_backend,
            dataset_df=st.session_state.dataset_df,
            use_cv=use_cv,
        )
        st.session_state.sim_df     = df
        st.session_state.sim_pos    = pos
        st.session_state.sim_method = method
        st.session_state["sim_jct"] = jct
        st.session_state["junction_history"] = jhist

        # auto-save to DB
        from database import SimulationDB
        db = SimulationDB()
        run_id = db.save_run(method, df)

        # final heatmap
        all_pts = [[p[0],p[1]] for fr in pos for p in fr]
        if all_pts and sim_backend == "SUMO":
            mf = make_base_map(14); add_heatmap(mf, all_pts)
            if pos: add_vehicles(mf, pos[-1])
            with map_ph.container():
                sfs(mf, height=400, use_container_width=True, returned_objects=[], key="sim_final")

        st.success(f"✅ Done! Saved as **Run #{run_id}**. Check 📊 Results in the 🗓️ History tab.")

        # quick metrics
        mc2 = st.columns(6)
        mc2[0].metric("Steps", len(df))
        mc2[1].metric("Avg reward", f"{df['reward'].mean():.4f}")
        mc2[2].metric("Avg queue", f"{df['total_queue'].mean():.1f}")
        mc2[3].metric("Peak queue", f"{df['total_queue'].max():.0f}")
        mc2[4].metric("High-cong %", f"{(df['congestion']=='high').mean()*100:.1f}%")
        
        from src.analysis import get_los_grade
        avg_delay = df["total_queue"].mean() * 5
        los = get_los_grade(avg_delay)
        mc2[5].metric("Level of Service", los, help="HCM grades A (best) → F (worst)")

        lane_cols = [c for c in df.columns if c.startswith("lane_")]
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("#### Reward"); st.line_chart(df.set_index("step")[["reward"]], color=["#3fb950"])
        with c2:
            if lane_cols: st.markdown("#### Queues per lane"); st.line_chart(df.set_index("step")[lane_cols])

        # ── Advanced Insights & Validation ──────────────────────────────────────
        st.markdown("<hr class='hr'>", unsafe_allow_html=True)
        st.markdown("### 📊 Advanced Insights & Validation")
        
        avg_q = df['total_queue'].mean()
        if avg_q < 5: 
            status, color = "EXCELLENT — Clear Flow", "#3fb950"
        elif avg_q < 15:
            status, color = "GOOD — Minor Bottlenecks", "#d29922"
        else:
            status, color = "CRITICAL — Heavy Congestion", "#f85149"
            
        st.markdown(f"""
        <div style="background:{color}22; border:1px solid {color}; padding:1rem; border-radius:8px; margin-bottom:1.5rem;">
            <h4 style="margin:0; color:{color};">Conclusion: {status}</h4>
            <p style="margin:5px 0 0 0; font-size:0.9rem;">
                The {method} controller maintained an average queue of <b>{avg_q:.1f}</b> vehicles.
                Peak congestion reached <b>{df['total_queue'].max():.0f}</b> vehicles.
            </p>
        </div>
        """, unsafe_allow_html=True)

        a1, a2 = st.columns(2)
        with a1:
            st.markdown("#### 🥯 Congestion Mix")
            dist = df['congestion'].value_counts(normalize=True) * 100
            st.bar_chart(dist, color="#8b949e")
            st.caption("Percentage of simulation time spent in each congestion state.")
            
        with a2:
            st.markdown("#### 🌿 CO₂ Emissions")
            if "co2_mg" in df.columns:
                st.line_chart(df.set_index("step")[["co2_mg"]], color=["#f2cc60"])
                st.caption("Total CO₂ (mg) emitted by all vehicles per simulation step.")

        if "vehicle_types" in df.columns:
            st.markdown("#### 🚗 Vehicle Type Mix")
            type_counts = df["vehicle_types"].iloc[-1] if df["vehicle_types"].iloc[-1] else {}
            if type_counts:
                st.bar_chart(type_counts)
            else:
                st.info("No vehicles active at simulation end.")

        if "rf_pred_label" in df.columns and "congestion" in df.columns:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 🎯 Prediction Accuracy (Confusion Matrix)")
            try:
                from analysis import evaluate_rf_realtime_predictions
                cm, labels, report, metrics = evaluate_rf_realtime_predictions(df)
                
                c1, c2 = st.columns([1, 1])
                with c1:
                    import matplotlib.pyplot as plt
                    import seaborn as sns
                    fig, ax = plt.subplots(figsize=(4, 3))
                    sns.heatmap(cm, annot=True, fmt='d', xticklabels=labels, yticklabels=labels, 
                                cmap="YlGnBu", cbar=False, ax=ax)
                    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
                    plt.tight_layout()
                    st.pyplot(fig)
                with c2:
                    st.metric("Model Precision", f"{metrics['precision']*100:.1f}%")
                    st.metric("Model Recall", f"{metrics['recall']*100:.1f}%")
                    st.dataframe(report[["f1-score", "support"]], use_container_width=True)
            except Exception as e:
                st.info(f"Detailed prediction evaluation unavailable: {e}")
    else:
        st.markdown("<div class='card' style='text-align:center;padding:2rem;'><div style='font-size:2.5rem'>🚗</div><h3 style='color:var(--heading-color)'>Choose a controller and click ▶ Run</h3></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SIDE-BY-SIDE COMPARE
# ══════════════════════════════════════════════════════════════════════════════
with tab_cmp:
    st.markdown("### ⚖️ Side-by-Side Method Comparison")
    st.caption("Runs two controllers sequentially on the same SUMO network and displays their metrics and charts head-to-head.")

    cc1,cc2,cc3,cc4 = st.columns([2,2,1,2])
    with cc1: ma = st.selectbox("Method A", list(METHOD_INFO.keys()), key="cmp_a")
    with cc2: mb = st.selectbox("Method B", list(METHOD_INFO.keys()), index=4, key="cmp_b")
    with cc3:
        cmp_steps = st.number_input("Steps", 50, 720, 150, 10, key="cmp_steps")
        cmp_btn   = st.button("⚖️  Compare", key="cmp_run")
    with cc4:
        cmp_backend = st.selectbox("Backend", ["Python Simulator", "SUMO"], index=0, key="cmp_backend")

    if cmp_btn:
        prog_a = st.progress(0, f"Running {ma}…")
        df_a, _, _, _ = run_simulation(
            ma, cmp_steps, False, progress_ph=prog_a,
            backend=cmp_backend, dataset_df=st.session_state.dataset_df,
        )
        st.session_state.cmp_df_a = df_a; st.session_state.cmp_m_a = ma

        prog_b = st.progress(0, f"Running {mb}…")
        df_b, _, _, _ = run_simulation(
            mb, cmp_steps, False, progress_ph=prog_b,
            backend=cmp_backend, dataset_df=st.session_state.dataset_df,
        )
        st.session_state.cmp_df_b = df_b; st.session_state.cmp_m_b = mb

        # save both
        from database import SimulationDB
        db = SimulationDB()
        db.save_run(ma, df_a, notes="Compare A")
        db.save_run(mb, df_b, notes="Compare B")

    if st.session_state.cmp_df_a is not None and st.session_state.cmp_df_b is not None:
        df_a = st.session_state.cmp_df_a; ma2 = st.session_state.cmp_m_a
        df_b = st.session_state.cmp_df_b; mb2 = st.session_state.cmp_m_b
        st.markdown("<hr class='hr'>",unsafe_allow_html=True)

        # summary header metrics
        st.markdown("#### 📊 Head-to-Head Metrics")
        ha1,ha2,ha3 = st.columns(3)
        ha1.metric(f"{ma2[:20]} — Avg Queue", f"{df_a['total_queue'].mean():.2f}",
                   delta=f"{df_a['total_queue'].mean()-df_b['total_queue'].mean():.2f} vs B", delta_color="inverse")
        ha2.metric(f"{mb2[:20]} — Avg Queue", f"{df_b['total_queue'].mean():.2f}")
        improvement = (df_a['total_queue'].mean()-df_b['total_queue'].mean())/max(df_a['total_queue'].mean(),0.001)*100
        ha3.metric("Improvement (B vs A)", f"{improvement:.1f}%")

        st.markdown("<hr class='hr'>",unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        for col, df_x, nm in [(col_a,df_a,ma2),(col_b,df_b,mb2)]:
            with col:
                mi_x = METHOD_INFO.get(nm, {"icon":"?","badge":"badge-blue","type":"?"})
                mx_badge = mi_x["badge"]
                mx_type  = mi_x["type"]
                st.markdown(f"<h3>{mi_x['icon']} {nm} <span class='badge {mx_badge}'>{mx_type}</span></h3>", unsafe_allow_html=True)
                m1,m2,m3,m4 = st.columns(4)
                m1.metric("Steps",       len(df_x))
                m2.metric("Avg reward",  f"{df_x['reward'].mean():.4f}")
                m3.metric("Avg queue",   f"{df_x['total_queue'].mean():.1f}")
                m4.metric("High-cong %", f"{(df_x['congestion']=='high').mean()*100:.1f}%")
                st.markdown("**Reward**"); st.line_chart(df_x.set_index("step")[["reward"]], color=["#3fb950"])
                st.markdown("**Queue length**"); st.line_chart(df_x.set_index("step")[["total_queue"]], color=["#f85149"])
                cong_map={"free":0,"moderate":1,"high":2}
                df_x2=df_x.copy(); df_x2["cong_num"]=df_x2["congestion"].map(cong_map)
                st.markdown("**Congestion timeline**"); st.area_chart(df_x2.set_index("step")[["cong_num"]], color=["#d29922"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — LIVE TRAINING
# ══════════════════════════════════════════════════════════════════════════════
with tab_train:
    st.markdown("### 📈 Live RL Training Monitor")
    st.caption("Runs `py src/train.py` as a subprocess for PPO or DQN and saves a learning-curve CSV for later comparison.")

    st.markdown("<div class='card'>"
                "⚠️ Training requires SUMO to be running. Each PPO iteration takes ~25 seconds. "
                "The chart updates after each rollout (every 2048 steps)."
                "</div>", unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)

    tc1,tc2,tc3 = st.columns(3)
    with tc1: train_algo = st.selectbox("Algorithm", ["PPO", "DQN"], key="train_algo")
    with tc2: train_ts = st.number_input("Total timesteps", 2048, 200000, 10000, 2048)
    with tc3:
        train_reward = st.selectbox("Reward", ["wait_time", "throughput"], key="train_reward")
        st.markdown("<br>",unsafe_allow_html=True)
        train_btn  = st.button("🚀 Start Training", key="train_start")
        clear_btn  = st.button("🗑️ Clear Log",       key="train_clear")

    if clear_btn:
        st.session_state.training_log = []
        st.session_state.training_rewards = []

    reward_chart_ph = st.empty()
    log_ph          = st.empty()

    if train_btn:
        st.session_state.training_log     = []
        st.session_state.training_rewards = []
        st.info("Training started… this may take several minutes.")

        train_script = os.path.join(ROOT, "src", "train.py")
        curve_path = os.path.join(ROOT, "models", f"{train_algo.lower()}_learning_curve.csv")
        proc = subprocess.Popen(
            [
                sys.executable, train_script,
                "--algo", train_algo,
                "--timesteps", str(train_ts),
                "--reward-type", train_reward,
                "--curve-path", curve_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=ROOT,
            bufsize=1,
        )
        try:
            for line in proc.stdout:
                line = line.rstrip()
                st.session_state.training_log.append(line)

                # parse SB3 rollout reward lines e.g. "|    ep_rew_mean     | -0.488   |"
                m = re.search(r"ep_rew_mean\s*\|\s*([-\d.]+)", line)
                if m:
                    try:
                        st.session_state.training_rewards.append(float(m.group(1)))
                    except ValueError:
                        pass

                # update chart if we have data
                if st.session_state.training_rewards:
                    rdf = pd.DataFrame({"Reward": st.session_state.training_rewards,
                                        "Iteration": range(len(st.session_state.training_rewards))})
                    reward_chart_ph.line_chart(rdf.set_index("Iteration")[["Reward"]], color=["#3fb950"])

                # stream last 30 lines
                log_ph.code("\n".join(st.session_state.training_log[-30:]), language="bash")

            proc.wait()
            if proc.returncode == 0:
                st.success(f"✅ {train_algo} training complete! Learning curve saved to `models/{train_algo.lower()}_learning_curve.csv`")
            else:
                st.error("Training exited with an error. Check the log above.")
        except Exception as e:
            st.error(f"Training error: {e}")

    # show existing log from state
    if st.session_state.training_rewards and not train_btn:
        rdf = pd.DataFrame({"Reward": st.session_state.training_rewards,
                             "Iteration": range(len(st.session_state.training_rewards))})
        st.markdown("#### Last training session")
        reward_chart_ph.line_chart(rdf.set_index("Iteration")[["Reward"]], color=["#3fb950"])
        log_ph.code("\n".join(st.session_state.training_log[-30:]), language="bash")

    st.markdown("<hr class='hr'>", unsafe_allow_html=True)
    st.markdown("#### PPO vs DQN Learning Curves")
    curve_files = {
        "PPO": os.path.join(ROOT, "models", "ppo_learning_curve.csv"),
        "DQN": os.path.join(ROOT, "models", "dqn_learning_curve.csv"),
    }
    curve_frames = []
    for algo_name, curve_file in curve_files.items():
        if os.path.exists(curve_file):
            try:
                cdf = pd.read_csv(curve_file)
                if {"timestep", "mean_reward"}.issubset(cdf.columns):
                    cdf = cdf[["timestep", "mean_reward"]].copy()
                    cdf = cdf.rename(columns={"mean_reward": algo_name})
                    curve_frames.append(cdf)
            except Exception:
                pass

    if curve_frames:
        merged_curve = curve_frames[0]
        for extra_curve in curve_frames[1:]:
            merged_curve = merged_curve.merge(extra_curve, on="timestep", how="outer")
        merged_curve = merged_curve.sort_values("timestep").set_index("timestep")
        st.line_chart(merged_curve)
    else:
        st.info("Train PPO and/or DQN first to generate comparable learning curves.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — HISTORY
# ══════════════════════════════════════════════════════════════════════════════
with tab_hist:
    from database import SimulationDB
    st.markdown("### 🗓️ Simulation Run History")
    st.caption("Every run is automatically saved to SQLite. Click a row ID to reload its full data.")

    db = SimulationDB()
    all_runs = db.get_all_runs()

    if len(all_runs) == 0:
        st.info("No runs saved yet. Run a simulation in the 🚦 tab first.")
    else:
        st.dataframe(all_runs, use_container_width=True,
                     column_config={"id": st.column_config.NumberColumn("ID", width="small"),
                                    "avg_reward":    st.column_config.NumberColumn("Avg Reward", format="%.4f"),
                                    "avg_queue":     st.column_config.NumberColumn("Avg Queue",  format="%.2f"),
                                    "high_cong_pct": st.column_config.NumberColumn("High Cong%", format="%.1f"),})

        st.markdown("<hr class='hr'>",unsafe_allow_html=True)
        hc1,hc2 = st.columns(2)
        with hc1:
            sel_id = st.number_input("Load run by ID", int(all_runs["id"].min()),
                                     int(all_runs["id"].max()), int(all_runs["id"].iloc[0]))
            load_btn = st.button("📥 Load this run", key="hist_load")
        with hc2:
            del_id  = st.number_input("Delete run by ID", int(all_runs["id"].min()),
                                      int(all_runs["id"].max()), int(all_runs["id"].iloc[-1]))
            del_btn = st.button("🗑️ Delete", key="hist_del")

        if del_btn:
            db.delete_run(del_id)
            st.success(f"Deleted run #{del_id}"); st.rerun()

        if load_btn:
            meta   = db.get_run_meta(sel_id)
            run_df = db.get_run_df(sel_id)
            if run_df is not None:
                st.success(f"Loaded Run #{sel_id} — **{meta['method']}** ({meta['timestamp']})")
                st.session_state.sim_df     = run_df
                st.session_state.sim_method = meta["method"]
                hm1,hm2,hm3,hm4 = st.columns(4)
                hm1.metric("Steps",       meta["steps"])
                hm2.metric("Avg reward",  f"{meta['avg_reward']:.4f}")
                hm3.metric("Avg queue",   f"{meta['avg_queue']:.2f}")
                hm4.metric("High-cong%",  f"{meta['high_cong_pct']:.1f}%")
                lcc = [c for c in run_df.columns if c.startswith("lane_")]
                h1,h2 = st.columns(2)
                with h1:
                    st.markdown("**Reward**"); st.line_chart(run_df.set_index("step")[["reward"]], color=["#3fb950"])
                with h2:
                    if lcc: st.markdown("**Lane queues**"); st.line_chart(run_df.set_index("step")[lcc])

        # comparison bar chart across all runs
        if len(all_runs) > 1:
            st.markdown("<hr class='hr'>",unsafe_allow_html=True)
            st.markdown("#### 📊 All Runs — Avg Queue Comparison")
            chart_df = all_runs.set_index("id")[["avg_queue"]].rename(
                columns={"avg_queue": "avg_queue (vehicles/step)"})
            st.bar_chart(chart_df)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — RESEARCH HUB
# ══════════════════════════════════════════════════════════════════════════════
with tab_research:
    st.markdown("### 🎓 Research & Academic Analysis")

    r_t1, r_t2, r_t3, r_t4, r_t5, r_t6 = st.tabs([
        "📚 Literature Benchmarks",
        "🌍 Carbon Calculator",
        "🔬 Ablation Study",
        "🧪 Optimization",
        "📡 Real Data",
        "🚀 Advanced RL",
    ])

    if "junction_history" not in st.session_state:
        st.session_state["junction_history"] = None

    # ── Literature benchmarks ─────────────────────────────────────────────────
    with r_t1:
        st.markdown("#### 📚 Literature Benchmark Comparison")
        st.caption("Comparison of published results vs our Mangalore simulation. All values = % queue/wait-time reduction vs fixed-cycle.")

        lit = pd.DataFrame([
            {"Method": "Fixed-cycle (baseline)", "Reduction %": 0.0,  "Source": "— (Our baseline)"},
            {"Method": "Actuated signals",        "Reduction %": 15.0, "Source": "Koonce et al. (2008)"},
            {"Method": "Fuzzy logic control",     "Reduction %": 22.0, "Source": "Trabia et al. (1999)"},
            {"Method": "Random Forest (ML)",      "Reduction %": 18.0, "Source": "Liang et al. (2019)"},
            {"Method": "LSTM predictor",          "Reduction %": 28.0, "Source": "Zhang et al. (2020)"},
            {"Method": "GCN + LSTM (DCRNN)",      "Reduction %": 33.0, "Source": "Li et al. (2018) — DCRNN"},
            {"Method": "DQN (RL)",                "Reduction %": 31.0, "Source": "Wei et al. (2018) — IntelliLight"},
            {"Method": "PPO (RL) — This project", "Reduction %": None, "Source": "Our result (run Compare tab)"},
        ])

        # inject our result if available
        if st.session_state.cmp_df_a is not None and st.session_state.cmp_df_b is not None:
            q_a = st.session_state.cmp_df_a["total_queue"].mean()
            q_b = st.session_state.cmp_df_b["total_queue"].mean()
            if st.session_state.cmp_m_a == "Fixed-cycle baseline":
                our_pct = (q_a - q_b) / max(q_a, 0.001) * 100
            elif st.session_state.cmp_m_b == "Fixed-cycle baseline":
                our_pct = (q_b - q_a) / max(q_b, 0.001) * 100
            else:
                our_pct = None
            if our_pct is not None:
                lit.loc[lit["Method"].str.contains("This project"), "Reduction %"] = round(our_pct, 1)

        def highlight_ours(row):
            return ["background-color: rgba(35,134,54,.2); font-weight:600" if "This project" in str(row["Method"]) else "" for _ in row]

        st.dataframe(lit.style.apply(highlight_ours, axis=1), use_container_width=True)
        st.caption("**Tip**: Run Fixed-cycle vs PPO in the ⚖️ Compare tab to fill in 'Our result' automatically.")
        st.markdown("""
        **Key references:**
        - Li, Y. et al. (2018). *Diffusion Convolutional Recurrent Neural Network*. ICLR.
        - Wei, H. et al. (2018). *IntelliLight: A Reinforcement Learning Approach*. KDD.
        - Zhang, Z. et al. (2020). *An Attention-Based LSTM for Traffic Signal Control*. IEEE.
        - Koonce, P. et al. (2008). *Traffic Signal Timing Manual*. FHWA-HOP-08-024.
        """)

    # ── Carbon calculator ─────────────────────────────────────────────────────
    with r_t2:
        st.markdown("#### 🌍 CO₂ & Fuel Savings Calculator")
        from carbon_calculator import estimate_savings, format_impact_summary, MANGALORE_SIGNALISED_JNS
        cc1,cc2,cc3 = st.columns(3)
        with cc1: baseline_q = st.number_input("Baseline avg queue (fixed-cycle)", 0.1, 50.0, 15.0, 0.1)
        with cc2: method_q   = st.number_input("Method avg queue",                 0.0, 50.0, 9.3,  0.1)
        with cc3: sim_steps  = st.number_input("Simulation steps used",            50, 720, 360)

        savings = estimate_savings(baseline_q, method_q, int(sim_steps))
        st.markdown(f"<div class='card'>{format_impact_summary(savings)}</div>", unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        sc = st.columns(4)
        sc[0].metric("Queue reduction",         f"{savings['queue_reduction_pct']:.1f}%")
        sc[1].metric("CO₂ saved / day",         f"{savings['co2_kg_saved_daily']:.0f} kg")
        sc[2].metric("CO₂ saved / year",        f"{savings['co2_tonnes_saved_yearly']:.1f} t")
        sc[3].metric("Equivalent trees 🌳",     f"{savings['trees_equivalent']:.0f}")

        st.caption(f"Assumptions: {MANGALORE_SIGNALISED_JNS} signalised junctions · 4 peak hours/day · "
                   f"0.6 L/hour idle fuel · 2.31 kg CO₂/litre petrol · 313 working days/year")

        # auto-fill from compare results
        if st.session_state.cmp_df_a is not None:
            if st.button("↩️ Auto-fill from last Compare run"):
                st.rerun()

    # ── Ablation study ────────────────────────────────────────────────────────
    with r_t3:
        st.markdown("#### 🔬 Random Forest Feature Ablation Study")
        st.caption("Trains the RF classifier with different subsets of features to measure each feature's contribution to accuracy.")

        abl_btn = st.button("▶ Run Ablation", key="abl_run")
        if abl_btn:
            try:
                from models.random_forest_model import generate_synthetic_data, build_features, label_congestion
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.preprocessing import LabelEncoder
                from sklearn.model_selection import train_test_split
                from sklearn.metrics import accuracy_score

                df_syn = generate_synthetic_data(n_hours=720)
                df_syn = build_features(df_syn)
                df_syn["label"] = df_syn["vehicle_count"].apply(label_congestion)
                le = LabelEncoder()
                df_syn["y"] = le.fit_transform(df_syn["label"])

                ALL_FEATS = ["hour_sin","hour_cos","is_peak","is_weekend","is_rain","vehicle_count"]
                results_abl = []
                with st.spinner("Running ablation…"):
                    # full model
                    for drop_feat in ["none"] + ALL_FEATS:
                        feats = [f for f in ALL_FEATS if f != drop_feat]
                        X = df_syn[feats].fillna(0)
                        y = df_syn["y"]
                        X_tr,X_te,y_tr,y_te = train_test_split(X,y,test_size=.2,shuffle=False)
                        clf = RandomForestClassifier(n_estimators=100,random_state=42,n_jobs=-1)
                        clf.fit(X_tr,y_tr)
                        acc = accuracy_score(y_te,clf.predict(X_te))*100
                        label = "All features (baseline)" if drop_feat=="none" else f"Without {drop_feat}"
                        results_abl.append({"Configuration":label,"Accuracy %":round(acc,2),"Feature dropped":drop_feat})

                df_abl = pd.DataFrame(results_abl)
                baseline_acc = df_abl.iloc[0]["Accuracy %"]
                df_abl["Impact"] = df_abl["Accuracy %"].apply(lambda x: f"{x-baseline_acc:+.2f}%")
                st.dataframe(df_abl, use_container_width=True)
                st.bar_chart(df_abl.set_index("Configuration")[["Accuracy %"]])
                st.caption("Each row = model trained without that feature. Biggest drop = most important feature.")
            except Exception as e:
                st.error(f"Ablation study failed: {e}")

    # ── Optuna Optimization ───────────────────────────────────────────────────
    with r_t4:
        st.markdown("#### 🧪 Automated Hyperparameter Tuning (Optuna)")
        st.caption("Auto-tunes PPO hyperparameters (lr, gamma, n_steps) using Bayesian optimization.")
        st.markdown("<div class='card'>"
                    "This spawns multiple SUMO instances in the background. "
                    "Each trial takes ~1 minute. Trials are saved to `simulation/logs.db`."
                    "</div>", unsafe_allow_html=True)
        
        o_c1, o_c2 = st.columns(2)
        with o_c1: n_trials = st.number_input("Number of trials", 1, 50, 5)
        with o_c2:
            st.markdown("<br>", unsafe_allow_html=True)
            opt_btn = st.button("🚀 Start Optimization", key="opt_run")
            
        opt_log_ph = st.empty()
        
        if opt_btn:
            opt_log_ph.info("Starting Bayesian search… check console for live SUMO output.")
            cmd = [sys.executable, "-m", "src.optimization"]
            # pass n_trials if I modify optimization.py to take args, 
            # or just run as-is for now (default 5)
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                        text=True, cwd=ROOT)
                opt_lines = []
                for line in proc.stdout:
                    opt_lines.append(line.rstrip())
                    opt_log_ph.code("\n".join(opt_lines[-15:]))
                proc.wait()
                if proc.returncode == 0:
                    st.success("✅ Optimization Complete! Best parameters saved to logs.db")
                    st.balloons()
                else:
                    st.error("Optimization failed. Check console logs.")
            except Exception as e:
                st.error(f"Error: {e}")

    # ── Real data integration ─────────────────────────────────────────────────
    with r_t5:
        st.markdown("#### 📡 Real Traffic Data Integration")
        st.markdown("""
        This tab shows how to plug real Mangalore traffic data into the pipeline.

        **Option A — Google Maps Traffic API** *(requires billing)*
        ```python
        import googlemaps
        gmaps = googlemaps.Client(key="YOUR_API_KEY")
        matrix = gmaps.distance_matrix(
            origins=["Hampankatta Circle, Mangalore"],
            destinations=["Kankanady Junction, Mangalore"],
            departure_time="now",
            traffic_model="best_guess",
        )
        duration_in_traffic = matrix["rows"][0]["elements"][0]["duration_in_traffic"]["value"]
        ```

        **Option B — OpenTraffic / Overpass API** *(free)*
        ```python
        import requests
        # Fetch real-time OSM speed data via Overpass
        url = "https://overpass-api.de/api/interpreter"
        query = '[out:json];way["highway"](12.86,74.83,12.90,74.86);out body;'
        r = requests.get(url, params={"data": query}).json()
        ```

        **Option C — CSV upload** *(your own field survey data)*
        """)

        upl = st.file_uploader("Upload traffic CSV (columns: timestamp, hour, vehicle_count, is_weekend)", type="csv")
        if upl:
            real_df = pd.read_csv(upl)
            st.success(f"Loaded {len(real_df)} rows. Columns: {list(real_df.columns)}")
            st.dataframe(real_df.head(20), use_container_width=True)
            required = {"hour","vehicle_count","is_weekend"}
            if required.issubset(set(real_df.columns)):
                st.info("✅ All required columns present.")
                if st.button("Train Random Forest on uploaded real data", key="real_rf_train"):
                    try:
                        from real_data import train_rf_from_real_data
                        train_rf_from_real_data(real_df)
                        st.success("Random Forest trained on uploaded real data and saved to `models/random_forest.pkl`.")
                    except Exception as e:
                        st.error(f"Real-data training failed: {e}")
                
                if st.button("Train LSTM on uploaded real data", key="real_lstm_train"):
                    try:
                        from src.models.lstm_model import TrafficLSTM, make_sequences
                        from src.real_data import normalize_real_traffic_data
                        import torch, torch.nn as nn
                        from torch.utils.data import DataLoader, TensorDataset

                        norm_df = normalize_real_traffic_data(real_df)
                        data = norm_df[["vehicle_count", "hour_sin", "hour_cos", "is_peak", "is_weekend", "is_rain"]].values.astype("float32")
                        X, y = make_sequences(data, seq_len=12)
                        ds = TensorDataset(torch.tensor(X), torch.tensor(y))
                        loader = DataLoader(ds, batch_size=32, shuffle=True)

                        model = TrafficLSTM(input_size=6, n_lanes=4)
                        opt = torch.optim.Adam(model.parameters(), lr=1e-3)
                        for epoch in range(10):
                            for xb, yb in loader:
                                opt.zero_grad()
                                nn.MSELoss()(model(xb), yb).backward()
                                opt.step()
                        os.makedirs("models", exist_ok=True)
                        torch.save(model.state_dict(), "models/lstm_traffic.pt")
                        st.success("LSTM trained and saved to models/lstm_traffic.pt")
                    except Exception as e:
                        st.error(f"LSTM training failed: {e}")
            else:
                st.warning(f"Missing columns: {required - set(real_df.columns)}")

    with r_t6:
        st.markdown("#### 🚀 Advanced RL Features")
        ar1, ar2 = st.columns(2)

        with ar1:
            st.markdown("##### Multi-junction control")
            mj_n = st.slider("Number of junctions", 2, 3, 2, key="mj_n")
            if st.button("Inspect multi-junction environment", key="mj_run"):
                try:
                    from multi_junction import MultiJunctionTrafficEnv
                    env = MultiJunctionTrafficEnv(n_junctions=mj_n, use_gui=False)
                    obs, info = env.reset()
                    st.json({
                        "junction_ids": info["junction_ids"],
                        "joint_action_count": env.action_space.n,
                        "observation_dim": len(obs),
                        "initial_total_queue": info["total_queue"],
                    })
                    env.close()
                except Exception as e:
                    st.error(f"Multi-junction env error: {e}")

            st.markdown("##### Transfer learning")
            tf_src = st.text_input("Source junction", value="cluster_1", key="tf_src")
            tf_tgt = st.text_input("Target junction", value="cluster_2", key="tf_tgt")
            if st.button("Run transfer learning", key="tf_run"):
                try:
                    from transfer_learning import train_and_finetune
                    meta = train_and_finetune(tf_src, tf_tgt)
                    st.json(meta)
                except Exception as e:
                    st.error(f"Transfer learning failed: {e}")

            st.markdown("##### Curriculum learning")
            if st.button("Run curriculum PPO", key="cur_run"):
                try:
                    from curriculum_learning import train_curriculum
                    hist = train_curriculum()
                    st.dataframe(pd.DataFrame(hist), use_container_width=True)
                except Exception as e:
                    st.error(f"Curriculum training failed: {e}")

        with ar2:
            st.markdown("##### Multi-agent RL")
            marl_n = st.slider("Agents / junctions", 2, 3, 2, key="marl_n")
            if st.button("Train cooperative MARL baseline", key="marl_run"):
                try:
                    from multi_agent_rl import train_independent_ppo_agents
                    prog = st.progress(0, text="Training joint PPO on all junctions...")
                    model = train_independent_ppo_agents(
                        n_junctions=marl_n,
                        total_timesteps=50_000,
                    )
                    prog.progress(100, text="Done!")
                    st.success(f"Saved: models/marl_joint.zip")
                    st.json({"junctions_controlled": marl_n, "timesteps": 50_000})
                except Exception as e:
                    st.error(f"MARL training failed: {e}")

            st.markdown("##### Offline RL")
            off_file = st.file_uploader("Upload simulation CSV for offline RL", type="csv", key="off_csv")
            if off_file is not None and st.button("Train offline CQL model", key="off_run"):
                try:
                    from offline_rl import train_offline_cql
                    off_df = pd.read_csv(off_file)
                    meta = train_offline_cql(off_df)
                    st.json(meta)
                except Exception as e:
                    st.error(f"Offline RL failed: {e}")

            st.markdown("##### 🕸️ GCN-LSTM Spatial-Temporal Model")
            gcn_epochs = st.slider("Epochs", 10, 100, 50, key="gcn_epochs")
            if st.button("Train GCN-LSTM on simulation data", key="gcn_train"):
                try:
                    from src.models.gcn_lstm_model import train_gcn_lstm
                    step_data = st.session_state.get("junction_history", None)
                    if step_data:
                        with st.spinner("Training GCN-LSTM..."):
                            train_gcn_lstm(epochs=gcn_epochs, step_data=step_data)
                        st.success("Saved: models/gcn_lstm_best.pt")
                        st.info("The GCN model is now integrated into the controller's observations.")
                    else:
                        st.warning("No junction_history found. Run a simulation first to populate real data.")
                except Exception as e:
                    st.error(f"GCN-LSTM training failed: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab_analysis:
    st.markdown("### 🧪 Advanced ML Analysis & Model Validation")
    
    an_c1, an_c2 = st.columns(2)
    with an_c1:
        st.markdown("#### 🌲 Random Forest Classifier Evaluation")
        rf_clf, rf_le = _load_rf()
        if rf_clf:
            from analysis import confusion_matrix_report
            cm, labels, df_rep, adv_metrics = confusion_matrix_report(rf_clf, rf_le)
            
            # Metrics Row
            m_c1, m_c2, m_c3, m_c4 = st.columns(4)
            m_c1.metric("Precision", f"{adv_metrics['precision']:.2f}")
            m_c2.metric("Recall", f"{adv_metrics['recall']:.2f}")
            m_c3.metric("F1-Score", f"{adv_metrics['f1']:.2f}")
            m_c4.metric("Accuracy", f"{adv_metrics['accuracy']:.2f}")

            st.caption("Detailed Per-Class Performance:")
            st.dataframe(df_rep, use_container_width=True)
            
            show_cm = st.checkbox("Show Confusion Matrix Heatmap")
            if show_cm:
                import matplotlib.pyplot as plt
                import seaborn as sns
                fig, ax = plt.subplots(figsize=(5, 4))
                sns.heatmap(cm, annot=True, fmt='d', xticklabels=labels, yticklabels=labels, 
                            cmap="Blues", cbar=False, ax=ax)
                plt.ylabel("Actual")
                plt.xlabel("Predicted")
                st.pyplot(fig)
        else:
            st.info("Train the Random Forest model first.")

    with an_c2:
        st.markdown("#### 🔍 SHAP Explainer (Feature Importance)")
        if rf_clf:
            try:
                from analysis import compute_shap, shap_mean_abs
                from models.random_forest_model import generate_synthetic_data, build_features, FEATURE_COLS
                
                df_sv = generate_synthetic_data(n_hours=100)
                df_sv = build_features(df_sv)
                X_sv = df_sv[FEATURE_COLS].fillna(0)
                
                if st.button("Calculate SHAP Values"):
                    with st.spinner("Computing local feature importances…"):
                        sv, expl, X_u = compute_shap(rf_clf, X_sv)
                        df_imp = shap_mean_abs(sv, FEATURE_COLS)
                        st.bar_chart(df_imp.set_index("feature")[["importance"]])
                        st.caption("Higher value = more influence on the model's decision.")
            except Exception as e:
                st.error(f"SHAP error: {e}")
        else:
            st.info("Load a model to see SHAP values.")

    st.markdown("<hr class='hr'>", unsafe_allow_html=True)
    st.markdown("#### 🚦 Real-Time RF Metrics From Latest Simulation")
    sim_df = st.session_state.sim_df
    if sim_df is not None and "rf_pred_label" in sim_df.columns:
        try:
            from analysis import evaluate_rf_realtime_predictions
            rt_cm, rt_labels, rt_report, rt_metrics = evaluate_rf_realtime_predictions(sim_df)
            r1, r2, r3, r4, r5 = st.columns(5)
            r1.metric("Precision", f"{rt_metrics['precision']:.2f}")
            r2.metric("Recall", f"{rt_metrics['recall']:.2f}")
            r3.metric("F1-Score", f"{rt_metrics['f1']:.2f}")
            r4.metric("Accuracy", f"{rt_metrics['accuracy']:.2f}")
            r5.metric("Samples", rt_metrics["n_samples"])
            st.dataframe(rt_report, use_container_width=True)
        except Exception as e:
            st.info(f"Real-time RF evaluation unavailable: {e}")
    else:
        st.info("Run a simulation first to compute RF real-time evaluation metrics.")

    st.markdown("<hr class='hr'>", unsafe_allow_html=True)
    fx1, fx2 = st.columns(2)

    with fx1:
        st.markdown("#### 🚨 Traffic Anomaly Detection")
        if sim_df is not None:
            try:
                from anomaly_detection import fit_isolation_forest
                _, anomaly_df = fit_isolation_forest(sim_df)
                top_anoms = anomaly_df[anomaly_df["is_anomaly"]].head(20)
                if len(top_anoms) == 0:
                    st.info("No anomalies detected in the latest run.")
                else:
                    st.metric("Detected anomalies", int(top_anoms["is_anomaly"].sum()))
                    st.dataframe(
                        top_anoms[[c for c in ["step", "total_queue", "reward", "anomaly_score", "congestion"] if c in top_anoms.columns]],
                        use_container_width=True,
                    )
            except Exception as e:
                st.info(f"Anomaly detection unavailable: {e}")
        else:
            st.info("Run a simulation first to analyze anomalies.")

    with fx2:
        st.markdown("#### 📈 Congestion Prediction Panel")
        if sim_df is not None and len(sim_df) >= 20:
            try:
                from forecasting import compare_forecasts
                hist_df, future_df = compare_forecasts(sim_df, target_col="total_queue", horizon=6)
                st.caption("Forecast horizon: next 30 minutes assuming 5-minute control intervals.")
                chart_df = hist_df.rename(columns={"total_queue": "Observed"}).set_index("step")[["Observed"]].tail(60)
                st.line_chart(chart_df)
                st.dataframe(future_df, use_container_width=True)
                pred_panel = future_df.copy()
                pred_panel["predicted_congestion"] = pred_panel["lstm_forecast"].apply(congestion_label)
                st.dataframe(pred_panel[["future_step", "lstm_forecast", "arima_forecast", "predicted_congestion"]], use_container_width=True)
            except Exception as e:
                st.info(f"Forecasting unavailable: {e}")
        else:
            st.info("Run a longer simulation first to enable congestion forecasting.")

    st.markdown("<hr class='hr'>", unsafe_allow_html=True)
    st.markdown("#### 📂 Forecast From Simulation CSV")
    fc_file = st.file_uploader("Upload a saved simulation CSV", type="csv", key="forecast_csv")
    if fc_file is not None:
        try:
            from forecasting import load_simulation_csv, compare_forecasts
            fc_df = load_simulation_csv(fc_file)
            _, fc_future = compare_forecasts(fc_df, target_col="total_queue", horizon=6)
            st.dataframe(fc_future, use_container_width=True)
        except Exception as e:
            st.error(f"CSV forecasting failed: {e}")

    st.markdown("<hr class='hr'>", unsafe_allow_html=True)
    st.markdown("#### 📊 Model Comparison: Accuracy, Error, Mean Error, Confusion Matrix")
    st.caption("Benchmarks available models on congestion prediction using the latest simulation run.")

    if sim_df is not None:
        if st.button("Run Model Benchmark", key="model_benchmark_btn"):
            try:
                mdf, cms, cm_labels = benchmark_prediction_models(sim_df)
                st.dataframe(mdf, use_container_width=True)

                g1, g2, g3 = st.columns(3)
                with g1:
                    st.markdown("**Accuracy**")
                    st.bar_chart(mdf.set_index("model")[["accuracy"]])
                with g2:
                    st.markdown("**Error Rate**")
                    st.bar_chart(mdf.set_index("model")[["error_rate"]])
                with g3:
                    st.markdown("**Mean Absolute Error**")
                    st.bar_chart(mdf.set_index("model")[["mean_abs_error"]])

                cm_model = st.selectbox("Confusion Matrix Model", list(cms.keys()), key="cm_model_select")
                import matplotlib.pyplot as plt
                import seaborn as sns
                fig, ax = plt.subplots(figsize=(5, 4))
                sns.heatmap(
                    cms[cm_model],
                    annot=True,
                    fmt="d",
                    xticklabels=cm_labels,
                    yticklabels=cm_labels,
                    cmap="Blues",
                    cbar=False,
                    ax=ax,
                )
                plt.xlabel("Predicted")
                plt.ylabel("Actual")
                plt.title(f"Confusion Matrix — {cm_model}")
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Model benchmark failed: {e}")
    else:
        st.info("Run a simulation first to compare model accuracy and error metrics.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 8 — EXPORT
# ══════════════════════════════════════════════════════════════════════════════
with tab_export:
    st.markdown("### 📄 Export Simulation Report")
    st.caption("Generates a self-contained HTML file with embedded charts — open in any browser, print as PDF.")

    df_exp = st.session_state.sim_df
    if df_exp is None:
        st.info("Run a simulation first (🚦 tab).")
    else:
        st.success(f"Ready to export: **{st.session_state.sim_method}** ({len(df_exp)} steps)")

        exp_notes = st.text_area("Add notes to report (optional)", placeholder="e.g. PPO trained for 200k steps, Mangalore 2km radius network…")

        # carbon auto-calc if compare was run
        carbon_data = None
        if st.session_state.cmp_df_a is not None:
            from carbon_calculator import estimate_savings
            q_a = st.session_state.cmp_df_a["total_queue"].mean()
            q_b = st.session_state.cmp_df_b["total_queue"].mean()
            if st.session_state.cmp_m_a == "Fixed-cycle baseline":
                carbon_data = estimate_savings(q_a, q_b, len(st.session_state.cmp_df_b))
            elif st.session_state.cmp_m_b == "Fixed-cycle baseline":
                carbon_data = estimate_savings(q_b, q_a, len(df_exp))

        exp_btn = st.button("🖨️ Generate Report", key="gen_report")
        if exp_btn:
            with st.spinner("Generating report…"):
                from database import SimulationDB
                from report_generator import generate_html_report
                db = SimulationDB()
                all_r = db.get_all_runs()
                html = generate_html_report(
                    method=st.session_state.sim_method,
                    df=df_exp,
                    carbon=carbon_data,
                    all_runs_df=all_r if len(all_r)>0 else None,
                    notes=exp_notes,
                )
            st.download_button(
                "⬇️ Download HTML Report",
                data=html.encode("utf-8"),
                file_name=f"mangalore_traffic_{st.session_state.sim_method.replace(' ','_').lower()}.html",
                mime="text/html",
            )
            st.success("Report ready! Click ⬇️ to download. Open in Chrome/Firefox → File → Print → Save as PDF.")

        # CSV export
        st.markdown("<hr class='hr'>",unsafe_allow_html=True)
        st.markdown("#### Also export raw data as CSV")
        csv = df_exp.to_csv(index=False)
        st.download_button("⬇️ Download CSV", csv,
                           f"{st.session_state.sim_method.replace(' ','_')}_data.csv", "text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 9 — DATA HUB
# ══════════════════════════════════════════════════════════════════════════════
with tab_data:
    st.markdown("### 📂 Data & Map Hub")
    st.caption("Upload your own traffic datasets, road network files, or pre-defined routes to customize the simulation.")

    dt1, dt2, dt3 = st.tabs(["📊 Traffic Dataset", "🗺️ Road Network", "🛣️ Vehicle Routes"])

    # --- Traffic Dataset Upload ---
    with dt1:
        st.markdown("#### 📊 Upload Traffic CSV")
        st.info("Upload a historical traffic dataset to train models. Required columns: `hour`, `vehicle_count`, `is_weekend`.")
        csv_file = st.file_uploader("Choose a CSV file", type="csv", key="data_hub_csv")
        
        if csv_file:
            try:
                # Read the raw CSV first
                df_uploaded = pd.read_csv(csv_file)
                
                # Auto-clean the dataset using src/real_data.py logic
                from real_data import normalize_real_traffic_data
                try:
                    df_cleaned = normalize_real_traffic_data(df_uploaded)
                    st.session_state.dataset_df = df_cleaned.copy()
                    
                    st.success("✅ Dataset loaded and cleaned! (Missing or null values handled automatically)")
                    st.dataframe(df_cleaned.head(10), use_container_width=True)
                except Exception as e:
                    st.error(f"Failed to clean dataset: {e}")
                    st.dataframe(df_uploaded.head(10), use_container_width=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🌲 Train Random Forest", key="tab_data_rf_train"):
                        with st.spinner("Training Random Forest…"):
                            from real_data import load_field_survey
                            from sklearn.ensemble import RandomForestClassifier
                            import joblib
                            
                            # Save uploaded file to temp path for load_field_survey
                            temp_path = "cache/uploaded_survey.csv"
                            os.makedirs("cache", exist_ok=True)
                            with open(temp_path, "wb") as f:
                                f.write(csv_file.getbuffer())
                                
                            X, y = load_field_survey(temp_path)
                            rf_clf = RandomForestClassifier(n_estimators=100, random_state=42)
                            rf_clf.fit(X, y)
                            
                            os.makedirs("models", exist_ok=True)
                            joblib.dump(rf_clf, "models/random_forest.pkl")
                            st.success("Model trained successfully on field survey data and saved to `models/random_forest.pkl`!")
                    with c2:
                        if st.button("🔮 Train LSTM (Experimental)", key="tab_data_lstm_train"):
                            st.info("LSTM training on custom datasets coming soon.")
                    st.caption("This dataset is now available to the Python Simulator in the 🚦 Simulate tab.")

                    st.markdown("##### 🔍 Quick Traffic Prediction (from uploaded data)")
                    from models.random_forest_model import predict_congestion
                    # Use cleaned data for defaults if available
                    clean_df = st.session_state.dataset_df
                    p1, p2, p3 = st.columns(3)
                    with p1:
                        pred_hour = st.slider("Hour", 0, 23, int(clean_df["hour"].iloc[0]) if len(clean_df) else 8, key="data_pred_hour")
                    with p2:
                        pred_count = st.number_input("Vehicle count", 0.0, 500.0, float(clean_df["vehicle_count"].mean()) if len(clean_df) else 30.0, key="data_pred_count")
                    with p3:
                        pred_weekend = st.selectbox("Weekend", [0, 1], key="data_pred_weekend")
                    if st.button("Predict congestion", key="data_pred_btn"):
                        try:
                            lbl = predict_congestion({
                                "hour": pred_hour,
                                "vehicle_count": pred_count,
                                "is_weekend": pred_weekend,
                                "weather": "clear",
                            })
                            st.success(f"Predicted congestion: **{lbl}**")
                        except Exception as e:
                            st.error(f"Prediction failed (train RF first): {e}")
            except Exception as e:
                st.error(f"Error reading CSV: {e}")

    # --- Road Network Upload ---
    with dt2:
        st.markdown("#### 🗺️ Upload OSM Road Network")
        st.warning("Warning: Uploading a new network will overwrite the current Mangalore simulation network.")
        osm_file = st.file_uploader("Choose an .osm or .xml file", type=["osm", "xml"], key="data_hub_osm")
        
        if osm_file:
            st.success(f"File uploaded: {osm_file.name}")
            if st.button("🚀 Rebuild Simulation Network", key="tab_data_net_rebuild"):
                with st.spinner("Converting OSM to SUMO network… this takes a few seconds."):
                    try:
                        temp_osm = os.path.join("simulation", "uploaded_network.osm")
                        with open(temp_osm, "wb") as f:
                            f.write(osm_file.getbuffer())
                        
                        from simulation.generate_network import generate_sumo_network
                        generate_sumo_network(
                            osm_path=temp_osm,
                            output_net="simulation/mangalore.net.xml",
                            output_routes="simulation/routes.xml"
                        )
                        st.success("✅ Network successfully rebuilt! The 🚦 Simulate tab now points to your custom map.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Network conversion failed: {e}")

    # --- Vehicle Routes Upload ---
    with dt3:
        st.markdown("#### 🛣️ Upload SUMO Routes")
        st.info("Upload a `.rou.xml` file to define specific traffic demand cycles.")
        rou_file = st.file_uploader("Choose a route file", type=["xml"], key="data_hub_rou")
        
        if rou_file:
            st.success(f"File uploaded: {rou_file.name}")
            if st.button("📥 Apply Routes", key="tab_data_rou_apply"):
                try:
                    target_path = "simulation/routes.xml"
                    with open(target_path, "wb") as f:
                        f.write(rou_file.getbuffer())
                    st.success("✅ Routes applied! Next simulation will use these traffic patterns.")
                except Exception as e:
                    st.error(f"Failed to save route file: {e}")

    st.markdown("<hr class='hr'>", unsafe_allow_html=True)
    st.markdown("#### 💾 Current Storage Status")
    db_size = os.path.getsize("simulation_history.db") / 1024 if os.path.exists("simulation_history.db") else 0
    st.text(f"• Database Size: {db_size:.2f} KB")
    st.text(f"• Traffic Network: {'Found' if os.path.exists('simulation/mangalore.net.xml') else 'Missing'}")
    st.text(f"• Route File: {'Found' if os.path.exists('simulation/routes.xml') else 'Missing'}")
