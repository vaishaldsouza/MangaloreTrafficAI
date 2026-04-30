import pytest
import numpy as np
import pandas as pd

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=50, freq="h"),
        "vehicle_count": np.random.randint(0, 30, 50),
        "hour": list(range(24)) * 2 + list(range(2)),
        "is_weekend": [0] * 50,
    })

@pytest.fixture
def sample_obs():
    # 8 values: 4 lane counts + 4 wait times (normalized 0-1)
    return np.array([0.5, 0.8, 0.2, 0.6, 0.3, 0.1, 0.4, 0.7], dtype=np.float32)
