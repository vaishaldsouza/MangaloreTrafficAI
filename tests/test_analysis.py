import numpy as np
import pandas as pd
from analysis import bootstrap_ci, run_ab_test

def test_bootstrap_ci_mean():
    data = [10.0] * 100
    mean, lo, hi = bootstrap_ci(data)
    assert mean == 10.0
    assert lo <= mean <= hi

def test_bootstrap_ci_width():
    # High variance data → wider CI
    data_hi = list(np.random.normal(0, 10, 200))
    data_lo = list(np.random.normal(0, 1,  200))
    _, lo_hi, hi_hi = bootstrap_ci(data_hi)
    _, lo_lo, hi_lo = bootstrap_ci(data_lo)
    assert (hi_hi - lo_hi) > (hi_lo - lo_lo)

def test_ab_test_significant():
    # Need at least 2 episodes to calculate variance for t-test
    df_a = [pd.DataFrame({"total_queue": np.ones(50) * 10}), pd.DataFrame({"total_queue": np.ones(50) * 10.1})]
    df_b = [pd.DataFrame({"total_queue": np.ones(50) * 5}), pd.DataFrame({"total_queue": np.ones(50) * 5.1})]
    result = run_ab_test(df_a, df_b)
    assert result["p_value"] < 0.05

def test_los_grade():
    from analysis import get_los_grade
    assert get_los_grade(5)  == "A"
    assert get_los_grade(15) == "B"
    assert get_los_grade(90) == "F"
