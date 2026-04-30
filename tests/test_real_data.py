import pandas as pd
from real_data import normalize_real_traffic_data, train_rf_from_real_data

def test_normalize_basic(sample_df):
    result = normalize_real_traffic_data(sample_df)
    assert "vehicle_count" in result.columns
    assert "hour_sin" in result.columns
    assert "is_peak" in result.columns
    assert result["vehicle_count"].isna().sum() == 0

def test_normalize_aliases():
    df = pd.DataFrame({"count": [5, 10], "timestamp": ["2024-01-01 08:00", "2024-01-01 17:00"]})
    result = normalize_real_traffic_data(df)
    assert "vehicle_count" in result.columns

def test_normalize_missing_all_cols():
    df = pd.DataFrame({"random_col": [1, 2, 3]})
    result = normalize_real_traffic_data(df)
    # Should fill defaults, not crash
    assert "vehicle_count" in result.columns

def test_train_rf_from_real_data(sample_df):
    clf, le = train_rf_from_real_data(sample_df)
    assert clf is not None
    assert set(le.classes_) == {"free", "moderate", "congested"}
