# src/api/sim_utils.py
import os
import sys
import numpy as np
import pandas as pd
import joblib
import torch
from stable_baselines3 import PPO, DQN

# Ensure root is in path
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

def load_rf():
    try:
        clf = joblib.load(os.path.join(ROOT, "models/random_forest.pkl"))
        le = joblib.load(os.path.join(ROOT, "models/rf_label_encoder.pkl"))
        return clf, le
    except:
        return None, None

def load_lstm():
    try:
        from src.models.lstm_model import TrafficLSTM
        m = TrafficLSTM(input_size=6, hidden_size=128, num_layers=2, n_lanes=4)
        m.load_state_dict(torch.load(os.path.join(ROOT, "models/lstm_traffic.pt"), map_location="cpu"))
        m.eval()
        return m
    except:
        return None

def load_rl_model(algo="PPO"):
    try:
        if algo == "DQN":
            for p in ["models/dqn_mangalore", "models/dqn_model", "models/dqn_mangalore_sumo"]:
                full_p = os.path.join(ROOT, p)
                if os.path.exists(full_p) or os.path.exists(full_p + ".zip"):
                    return DQN.load(full_p)
        else:
            for p in ["models/ppo_mangalore_sumo", "models/ppo_mangalore"]:
                full_p = os.path.join(ROOT, p)
                if os.path.exists(full_p) or os.path.exists(full_p + ".zip"):
                    return PPO.load(full_p)
    except:
        pass
    return None

def predict_rf_label(obs, step, rf_clf, rf_le):
    if rf_clf is None or rf_le is None:
        return None
    try:
        from src.models.random_forest_model import build_features, FEATURE_COLS
        hour = (step * 5 // 3600) % 24
        vehicle_count = float(np.sum(obs[: len(obs) // 2]) * 20)
        row = build_features(pd.DataFrame([{
            "hour": hour,
            "vehicle_count": vehicle_count,
            "is_weekend": 0,
        }]))
        return rf_le.inverse_transform(rf_clf.predict(row[FEATURE_COLS].fillna(0)))[0]
    except:
        return None

def get_action(method, obs, action_space_n, step, rf_clf=None, rf_le=None,
               lstm_model=None, lstm_hist=None, rl_model=None):
    n = action_space_n
    if method == "Fixed-cycle baseline":   return (step // 30) % n
    if method == "Greedy adaptive":        return int(np.argmax(obs[:n]))
    if method == "Random Forest":
        if rf_clf is None: return (step // 30) % n
        lbl = predict_rf_label(obs, step, rf_clf, rf_le)
        return int(np.argmax(obs[:n])) if lbl == "congested" else (step // 30) % n
    if method == "LSTM predictor":
        if lstm_model is None or lstm_hist is None or len(lstm_hist) < 12: return (step // 30) % n
        seq = torch.tensor(np.array(lstm_hist[-12:], dtype=np.float32)).unsqueeze(0)
        with torch.no_grad(): pred = lstm_model(seq).numpy()[0]
        return int(np.argmin(pred))
    if method == "Ensemble controller":
        try:
            from src.ensemble import choose_ensemble_action
            action, _ = choose_ensemble_action(
                obs, step, n_actions=n,
                rf_clf=rf_clf, rf_le=rf_le,
                lstm_model=lstm_model, lstm_hist=lstm_hist,
            )
            return action
        except:
            return int(np.argmax(obs[:n]))
    if method in ["PPO RL Model", "DQN RL Model", "PPO (Reinforcement Learning)", "DQN (Reinforcement Learning)"]:
        if rl_model is None: return (step // 30) % n
        # Pad observation if model expects 12 but env gives 8
        if len(obs) < 12:
            obs = np.pad(obs, (0, 12 - len(obs)), 'constant')
        action, _ = rl_model.predict(obs, deterministic=True)
        return int(action)
    if method == "Actuated signals":
        return -1
    return 0

def congestion_label(q):
    return "free" if q < 5 else ("moderate" if q < 12 else "high")
