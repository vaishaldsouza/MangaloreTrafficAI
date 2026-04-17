"""
src/offline_rl.py — Offline RL from saved simulation CSV data using d3rlpy.
"""
import numpy as np
import pandas as pd


def dataframe_to_offline_dataset(df: pd.DataFrame):
    lane_cols = [c for c in df.columns if c.startswith("lane_")]
    if not lane_cols:
        raise ValueError("Offline RL needs lane-level features in the dataframe.")

    obs_cols = lane_cols + [c for c in ["total_queue", "reward", "co2_mg"] if c in df.columns]
    observations = df[obs_cols].fillna(0).astype(float).values
    actions = df["phase"].fillna(0).astype(int).values if "phase" in df.columns else np.zeros(len(df), dtype=int)
    rewards = df["reward"].fillna(0).astype(float).values
    terminals = np.zeros(len(df), dtype=bool)
    terminals[-1] = True
    return observations, actions, rewards, terminals


def train_offline_cql(df: pd.DataFrame, save_path: str = "models/offline_cql.d3"):
    try:
        import d3rlpy
        from d3rlpy.dataset import MDPDataset
    except ImportError as exc:
        raise ImportError("Install d3rlpy to use offline RL.") from exc

    observations, actions, rewards, terminals = dataframe_to_offline_dataset(df)
    dataset = MDPDataset(
        observations=observations,
        actions=actions,
        rewards=rewards,
        terminals=terminals,
    )
    algo = d3rlpy.algos.DiscreteCQLConfig().create(device=False)
    algo.fit(dataset, n_steps=1000, show_progress=False)
    algo.save(save_path)
    return {"save_path": save_path, "n_samples": len(df)}
