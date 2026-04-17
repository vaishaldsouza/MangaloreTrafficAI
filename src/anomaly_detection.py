"""
src/anomaly_detection.py — Traffic anomaly detection tools.
"""
import pandas as pd
from sklearn.ensemble import IsolationForest


FEATURE_CANDIDATES = [
    "reward",
    "total_queue",
    "total_vehicles",
    "co2_mg",
]


def fit_isolation_forest(df: pd.DataFrame, contamination: float = 0.05):
    feat_cols = [c for c in FEATURE_CANDIDATES if c in df.columns]
    lane_cols = [c for c in df.columns if c.startswith("lane_")]
    feat_cols.extend(lane_cols[:8])
    if not feat_cols:
        raise ValueError("No usable numeric features were found for anomaly detection.")

    X = df[feat_cols].fillna(0)
    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42,
    )
    preds = model.fit_predict(X)
    scores = model.decision_function(X)

    result = df.copy()
    result["anomaly_score"] = -scores
    result["is_anomaly"] = preds == -1
    return model, result.sort_values("anomaly_score", ascending=False)
