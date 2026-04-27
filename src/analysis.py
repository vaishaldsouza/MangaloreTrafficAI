"""
src/analysis.py — Statistical & ML analysis tools.

Features:
  • A/B testing with bootstrap confidence intervals
  • Welch's t-test for statistical significance
  • SHAP feature importance for the Random Forest model
  • Confusion matrix + classification report
  • Learning curve data parsing from SB3 training logs
"""
import numpy as np
import pandas as pd
import os
from typing import Optional, Dict, List
from sklearn.metrics import precision_recall_fscore_support, accuracy_score, confusion_matrix


# ── A/B Testing ───────────────────────────────────────────────────────────────

def bootstrap_ci(data: list[float], n_boot: int = 10_000,
                 ci: float = 0.95) -> tuple[float, float, float]:
    """
    Bootstrap confidence interval for the mean.

    Returns:
        (mean, lower_bound, upper_bound)
    """
    arr = np.array(data, dtype=float)
    means = [np.mean(np.random.choice(arr, size=len(arr), replace=True))
             for _ in range(n_boot)]
    alpha = (1 - ci) / 2
    lower = np.percentile(means, alpha * 100)
    upper = np.percentile(means, (1 - alpha) * 100)
    return float(arr.mean()), float(lower), float(upper)


def run_ab_test(
    df_episodes_a: list[pd.DataFrame],
    df_episodes_b: list[pd.DataFrame],
    metric: str = "total_queue",
) -> dict:
    """
    Compare two sets of simulation episodes using bootstrap CI + t-test.

    Args:
        df_episodes_a : list of per-episode DataFrames for method A
        df_episodes_b : list of per-episode DataFrames for method B
        metric        : column name to compare (default: total_queue)

    Returns dict with:
        means_a, ci_a, means_b, ci_b,
        t_stat, p_value, significant,
        improvement_pct
    """
    from scipy import stats

    avgs_a = [df[metric].mean() for df in df_episodes_a]
    avgs_b = [df[metric].mean() for df in df_episodes_b]

    mean_a, lo_a, hi_a = bootstrap_ci(avgs_a)
    mean_b, lo_b, hi_b = bootstrap_ci(avgs_b)

    t_stat, p_value = stats.ttest_ind(avgs_a, avgs_b, equal_var=False)
    significant = bool(p_value < 0.05)

    improvement_pct = (mean_a - mean_b) / max(abs(mean_a), 1e-6) * 100

    return {
        "mean_a": mean_a, "ci_a": (lo_a, hi_a), "avgs_a": avgs_a,
        "mean_b": mean_b, "ci_b": (lo_b, hi_b), "avgs_b": avgs_b,
        "t_stat": t_stat, "p_value": p_value,
        "significant": significant,
        "improvement_pct": improvement_pct,
    }


# ── T-test only ───────────────────────────────────────────────────────────────

def ttest_rewards(rewards_a: list[float], rewards_b: list[float]) -> dict:
    """
    Welch's t-test on per-step reward arrays from two methods.

    Returns dict: t_stat, p_value, significant, effect_size (Cohen's d)
    """
    from scipy import stats
    a, b = np.array(rewards_a), np.array(rewards_b)
    t_stat, p_value = stats.ttest_ind(a, b, equal_var=False)

    # Cohen's d effect size
    pooled_std = np.sqrt((a.std() ** 2 + b.std() ** 2) / 2)
    d = (a.mean() - b.mean()) / max(pooled_std, 1e-9)

    return {
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "significant": bool(p_value < 0.05),
        "effect_size_d": float(d),
        "mean_a": float(a.mean()),
        "mean_b": float(b.mean()),
        "std_a": float(a.std()),
        "std_b": float(b.std()),
        "n_a": len(a),
        "n_b": len(b),
    }


# ── SHAP ──────────────────────────────────────────────────────────────────────

def compute_shap(rf_clf, X: pd.DataFrame):
    """
    Compute SHAP values for a fitted RandomForestClassifier.

    Returns:
        shap_values  : np.ndarray shape (n_classes, n_samples, n_features)  OR
                       np.ndarray shape (n_samples, n_features) for binary
        explainer    : shap.TreeExplainer  (use .expected_value for base rate)
        X_used       : the DataFrame actually passed (same as X, exposed for plotting)
    """
    try:
        import shap
    except ImportError:
        raise ImportError("pip install shap")

    explainer = shap.TreeExplainer(rf_clf)
    raw = explainer.shap_values(X)
    return raw, explainer, X


def shap_mean_abs(shap_values, feature_names: list[str],
                  class_idx: int = -1) -> pd.DataFrame:
    """
    Summarise SHAP values into mean |SHAP| per feature.

    Args:
        shap_values  : output from compute_shap()
        feature_names: column names
        class_idx    : which class to summarise (-1 = average over all)

    Returns:
        DataFrame with columns [feature, importance] sorted descending.
    """
    if isinstance(shap_values, list):          # multi-class → list of arrays
        if class_idx == -1:
            arr = np.mean([np.abs(sv) for sv in shap_values], axis=0)
        else:
            arr = np.abs(shap_values[class_idx])
    else:
        arr = np.abs(shap_values)

    importances = arr.mean(axis=0)
    return pd.DataFrame({"feature": feature_names, "importance": importances})\
             .sort_values("importance", ascending=False).reset_index(drop=True)


# ── Confusion matrix ──────────────────────────────────────────────────────────

def confusion_matrix_report(rf_clf, rf_le, n_samples: int = 500):
    """
    Generate synthetic test data, run RF predictions, return CM + report.

    Returns:
        cm        : np.ndarray (n_classes x n_classes)
        labels    : class name list
        df_report : per-class precision/recall/F1 as DataFrame
        metrics   : dict of macro-avg precision, recall, f1, accuracy
    """
    from sklearn.metrics import confusion_matrix, classification_report
    from models.random_forest_model import (
        generate_synthetic_data, build_features,
        label_congestion, FEATURE_COLS,
    )

    df = generate_synthetic_data(n_hours=n_samples)
    df = build_features(df)
    df["label"] = df["vehicle_count"].apply(label_congestion)
    X = df[FEATURE_COLS].fillna(0)
    y_true_str  = df["label"]
    y_true_enc  = rf_le.transform(y_true_str)
    y_pred_enc  = rf_clf.predict(X)

    cm = confusion_matrix(y_true_enc, y_pred_enc)
    report_dict = classification_report(
        y_true_enc, y_pred_enc,
        target_names=rf_le.classes_,
        output_dict=True,
    )
    df_report = pd.DataFrame(report_dict).T.round(3)

    # Global metrics
    p, r, f, _ = precision_recall_fscore_support(y_true_enc, y_pred_enc, average='macro')
    acc = accuracy_score(y_true_enc, y_pred_enc)

    metrics = {
        "precision": float(p),
        "recall": float(r),
        "f1": float(f),
        "accuracy": float(acc)
    }

    return cm, list(rf_le.classes_), df_report, metrics


def evaluate_rf_realtime_predictions(df: pd.DataFrame) -> tuple[np.ndarray, list[str], pd.DataFrame, dict]:
    """
    Evaluate Random Forest predictions collected during a live simulation run.

    Expected columns:
        rf_pred_label : model prediction per step ("free"/"moderate"/"congested")
        congestion    : observed simulation congestion ("free"/"moderate"/"high")
    """
    if "rf_pred_label" not in df.columns:
        raise ValueError("Simulation data does not contain 'rf_pred_label'.")
    if "congestion" not in df.columns:
        raise ValueError("Simulation data does not contain 'congestion'.")

    eval_df = df[["rf_pred_label", "congestion"]].dropna().copy()
    if eval_df.empty:
        raise ValueError("No valid RF realtime prediction rows were found.")

    eval_df["actual_label"] = eval_df["congestion"].replace({"high": "congested"})
    labels = ["free", "moderate", "congested"]

    y_true = eval_df["actual_label"]
    y_pred = eval_df["rf_pred_label"]
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    p, r, f, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )
    accuracy = accuracy_score(y_true, y_pred)
    df_report = pd.DataFrame({
        "precision": p,
        "recall": r,
        "f1-score": f,
        "support": support,
    }, index=labels).round(3)

    metrics = {
        "precision": float(np.mean(p)),
        "recall": float(np.mean(r)),
        "f1": float(np.mean(f)),
        "accuracy": float(accuracy),
        "n_samples": int(len(eval_df)),
    }
    return cm, labels, df_report, metrics


# ── Learning curve ────────────────────────────────────────────────────────────

def parse_sb3_training_log(log_lines: list[str]) -> pd.DataFrame:
    """
    Parse SB3 stdout log lines to extract (timestep, ep_rew_mean, ep_len_mean).

    Returns DataFrame with columns: timestep, ep_rew_mean, ep_len_mean
    """
    import re
    records = []
    ts_pattern  = re.compile(r"total_timesteps\s*\|\s*([\d.e+]+)")
    rew_pattern = re.compile(r"ep_rew_mean\s*\|\s*([-\d.e+]+)")
    len_pattern = re.compile(r"ep_len_mean\s*\|\s*([\d.e+]+)")

    ts = rew = ep_len = None
    for line in log_lines:
        m = ts_pattern.search(line)
        if m: ts = float(m.group(1))
        m = rew_pattern.search(line)
        if m: rew = float(m.group(1))
        m = len_pattern.search(line)
        if m: ep_len = float(m.group(1))
        if ts is not None and rew is not None:
            records.append({"timestep": ts, "ep_rew_mean": rew,
                            "ep_len_mean": ep_len or np.nan})
            ts = rew = ep_len = None

    return pd.DataFrame(records)


def get_los_grade(avg_delay_seconds: float) -> str:
    """Highway Capacity Manual Level of Service grades."""
    if avg_delay_seconds <= 10:  return "A"
    if avg_delay_seconds <= 20:  return "B"
    if avg_delay_seconds <= 35:  return "C"
    if avg_delay_seconds <= 55:  return "D"
    if avg_delay_seconds <= 80:  return "E"
    return "F"


def cv_vs_traci_ablation(config_path="simulation/config.sumocfg", n_steps=200):
    """Compare queue length readings: CV pipeline vs TraCI ground truth."""
    from src.controller import SumoTrafficEnv
    import pandas as pd

    results = []
    for use_cv in [False, True]:
        env = SumoTrafficEnv(config_path=config_path, use_cv=use_cv, max_steps=n_steps*5)
        obs, _ = env.reset()
        queues = []
        for _ in range(n_steps):
            obs, _, term, trunc, info = env.step(env.action_space.sample())
            queues.append(info["total_queue"])
            if term or trunc:
                break
        env.close()
        results.append({"source": "CV" if use_cv else "TraCI", 
                         "mean_queue": float(np.mean(queues)),
                         "std_queue": float(np.std(queues))})
    return pd.DataFrame(results)
