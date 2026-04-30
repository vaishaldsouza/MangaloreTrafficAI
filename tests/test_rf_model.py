import numpy as np
import pandas as pd
from models.random_forest_model import (
    generate_synthetic_data, build_features,
    label_congestion, train_random_forest, FEATURE_COLS
)

def test_label_congestion():
    assert label_congestion(2)  == "free"
    assert label_congestion(8)  == "moderate"
    assert label_congestion(20) == "congested"

def test_build_features():
    df = pd.DataFrame({"hour": [8, 17, 2], "vehicle_count": [10, 20, 3], "is_weekend": [0, 0, 1]})
    result = build_features(df)
    assert "hour_sin" in result.columns
    assert "is_peak" in result.columns
    assert result.loc[result["hour"] == 8, "is_peak"].values[0] == 1
    assert result.loc[result["hour"] == 2, "is_peak"].values[0] == 0

def test_synthetic_data_shape():
    df = generate_synthetic_data(n_hours=100)
    assert len(df) == 100
    assert "vehicle_count" in df.columns

def test_train_rf_accuracy():
    df = generate_synthetic_data(n_hours=500)
    clf, le = train_random_forest(df)
    X = build_features(df)[FEATURE_COLS].fillna(0)
    preds = clf.predict(X)
    acc = (preds == le.transform(df["vehicle_count"].apply(label_congestion))).mean()
    assert acc > 0.75, f"RF accuracy too low: {acc:.2f}"
