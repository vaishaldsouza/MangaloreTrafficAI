"""
src/ensemble.py — Ensemble controller combining RF, LSTM, and Greedy votes.
"""
import numpy as np
import pandas as pd


def rf_vote(obs, step, rf_clf=None, rf_le=None, n_actions=4):
    if rf_clf is None or rf_le is None:
        return None
    try:
        from models.random_forest_model import build_features, FEATURE_COLS
        hour = (step * 5 // 3600) % 24
        row = build_features(pd.DataFrame([{
            "hour": hour,
            "vehicle_count": float(np.sum(obs[: len(obs) // 2]) * 20),
            "is_weekend": 0,
        }]))
        label = rf_le.inverse_transform(rf_clf.predict(row[FEATURE_COLS].fillna(0)))[0]
        if label == "congested":
            return int(np.argmax(obs[:n_actions]))
        return int((step // 30) % n_actions)
    except Exception:
        return None


def lstm_vote(lstm_model=None, lstm_hist=None, n_actions=4):
    if lstm_model is None or lstm_hist is None or len(lstm_hist) < 12:
        return None
    try:
        import torch
        seq = torch.tensor(np.array(lstm_hist[-12:], dtype=np.float32)).unsqueeze(0)
        with torch.no_grad():
            pred = lstm_model(seq).numpy()[0]
        return int(np.argmax(pred[:n_actions]))
    except Exception:
        return None


def greedy_vote(obs, n_actions=4):
    return int(np.argmax(obs[:n_actions]))


def choose_ensemble_action(obs, step, n_actions, rf_clf=None, rf_le=None, lstm_model=None, lstm_hist=None):
    """Majority vote across RF, LSTM, and Greedy with Greedy fallback."""
    votes = [
        rf_vote(obs, step, rf_clf=rf_clf, rf_le=rf_le, n_actions=n_actions),
        lstm_vote(lstm_model=lstm_model, lstm_hist=lstm_hist, n_actions=n_actions),
        greedy_vote(obs, n_actions=n_actions),
    ]
    valid_votes = [v for v in votes if v is not None]
    if not valid_votes:
        return 0, {"votes": votes}

    counts = {}
    for vote in valid_votes:
        counts[vote] = counts.get(vote, 0) + 1
    best_vote = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[0][0]
    return int(best_vote), {"votes": votes, "counts": counts}
