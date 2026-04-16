"""
src/models/random_forest_model.py

Method 2 — Random Forest congestion classifier.
Fastest "interpretable ML" baseline. Trains on synthetic Mangalore traffic
data (or real data if supplied) and classifies each timestep as:
    free / moderate / congested

Literature target: ≥ 85% accuracy with just time-of-day + vehicle count.

Run:
    python -m src.models.random_forest_model
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib
import os


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Feature engineering matching the literature:
    time of day, vehicle count, weather, day type.
    """
    df = df.copy()
    df["hour_sin"] = np.sin(df["hour"] * (2 * np.pi / 24))
    df["hour_cos"] = np.cos(df["hour"] * (2 * np.pi / 24))
    df["is_peak"]  = df["hour"].apply(
        lambda h: 1 if (8 <= h <= 10 or 17 <= h <= 19) else 0
    )
    # Weather column is optional; default to 0 (clear) if absent
    weather_col = df.get("weather", pd.Series(["clear"] * len(df), index=df.index))
    df["is_rain"] = weather_col.apply(
        lambda w: 1 if str(w).lower() in ["rain", "drizzle"] else 0
    )
    return df


def label_congestion(count: float) -> str:
    """Labels matching your survey thresholds."""
    if count < 5:
        return "free"
    if count < 12:
        return "moderate"
    return "congested"


# ---------------------------------------------------------------------------
# Synthetic data generator (used when no real CSV is provided)
# ---------------------------------------------------------------------------

def generate_synthetic_data(n_hours: int = 720, seed: int = 42) -> pd.DataFrame:
    """
    Generates synthetic hourly Mangalore traffic data.
    - Morning rush: 8–10 AM
    - Evening rush: 5–7 PM
    - Lighter on weekends
    """
    np.random.seed(seed)
    timestamps = pd.date_range("2024-01-01", periods=n_hours, freq="h")
    records = []
    for ts in timestamps:
        hour = ts.hour
        is_weekend = int(ts.dayofweek >= 6)
        if 8 <= hour <= 10:
            base = 80
        elif 17 <= hour <= 19:
            base = 90
        elif 0 <= hour <= 5:
            base = 10
        else:
            base = 40
        if is_weekend:
            base = int(base * 0.6)
        records.append({
            "timestamp":     ts,
            "hour":          hour,
            "day_of_week":   ts.dayofweek,
            "is_weekend":    is_weekend,
            "vehicle_count": int(np.random.poisson(base)),
        })
    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

FEATURE_COLS = ["hour_sin", "hour_cos", "is_peak", "is_weekend", "is_rain", "vehicle_count"]


def train_random_forest(df: pd.DataFrame):
    """
    df columns needed: hour, vehicle_count, is_weekend, weather (optional).

    Returns:
        clf (RandomForestClassifier): fitted classifier
        le  (LabelEncoder):          label encoder used during training
    """
    df = build_features(df)
    df["label"] = df["vehicle_count"].apply(label_congestion)

    X = df[FEATURE_COLS].fillna(0)
    y = df["label"]

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    # Temporal split — keep time order, no shuffle
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, shuffle=False
    )

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n[RandomForest] Test accuracy: {acc*100:.1f}%")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    importances = dict(zip(FEATURE_COLS, clf.feature_importances_))
    print("Feature importances:")
    for feat, imp in sorted(importances.items(), key=lambda x: -x[1]):
        print(f"  {feat:<20} {imp:.4f}")

    os.makedirs("models", exist_ok=True)
    joblib.dump(clf, "models/random_forest.pkl")
    joblib.dump(le,  "models/rf_label_encoder.pkl")
    print("\nSaved: models/random_forest.pkl, models/rf_label_encoder.pkl")
    return clf, le


def predict_congestion(obs_row: dict) -> str:
    """
    Predict congestion level from a single observation dict.
    Keys needed: hour, vehicle_count, is_weekend.
    """
    clf = joblib.load("models/random_forest.pkl")
    le  = joblib.load("models/rf_label_encoder.pkl")
    df  = pd.DataFrame([obs_row])
    df  = build_features(df)
    X   = df[FEATURE_COLS].fillna(0)
    return le.inverse_transform(clf.predict(X))[0]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Generating synthetic Mangalore data (720 hours)...")
    df = generate_synthetic_data(n_hours=720)
    train_random_forest(df)
