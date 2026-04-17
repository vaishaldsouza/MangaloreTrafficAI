"""
src/real_data.py — Real data ingestion and normalization pipeline.
"""
import pandas as pd

from models.random_forest_model import build_features, train_random_forest


REQUIRED_COLS = {"hour", "vehicle_count", "is_weekend"}


def normalize_real_traffic_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and normalizes uploaded traffic data.
    Handles missing columns by using aliases or assigning defaults.
    """
    data = df.copy()

    # 1. Handle vehicle_count aliases
    count_aliases = ["vehicle_count", "count", "volume", "vehicles", "qty"]
    for alias in count_aliases:
        found = [col for col in data.columns if col.lower() == alias]
        if found and "vehicle_count" not in data.columns:
            data["vehicle_count"] = data[found[0]]
            break

    # 2. Derive time features from timestamp if present
    ts_cols = [col for col in data.columns if col.lower() in ["timestamp", "time", "date"]]
    if ts_cols and ("hour" not in data.columns or "is_weekend" not in data.columns):
        try:
            ts_series = pd.to_datetime(data[ts_cols[0]])
            if "hour" not in data.columns:
                data["hour"] = ts_series.dt.hour
            if "is_weekend" not in data.columns:
                data["is_weekend"] = (ts_series.dt.dayofweek >= 5).astype(int)
        except Exception:
            pass

    # 3. Fill missing required columns with safe defaults
    if "vehicle_count" not in data.columns:
        data["vehicle_count"] = 0
    if "hour" not in data.columns:
        data["hour"] = 12
    if "is_weekend" not in data.columns:
        data["is_weekend"] = 0

    # 4. Handle null values (NAs)
    data["vehicle_count"] = data["vehicle_count"].fillna(0)
    data["hour"] = data["hour"].fillna(12)
    data["is_weekend"] = data["is_weekend"].fillna(0)

    if "weather" not in data.columns:
        data["weather"] = "clear"

    return build_features(data)


def train_rf_from_real_data(df: pd.DataFrame):
    normalized = normalize_real_traffic_data(df)
    return train_random_forest(normalized)
