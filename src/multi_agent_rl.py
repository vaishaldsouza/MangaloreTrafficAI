"""
src/multi_agent_rl.py — Cooperative multi-agent RL over multiple junctions.

Implements a practical independent-PPO baseline for each controlled junction.
"""
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

from multi_junction import MultiJunctionTrafficEnv


def train_independent_ppo_agents(
    n_junctions: int = 2,
    total_timesteps: int = 5_000,
    config_path: str = "simulation/config.sumocfg",
):
    """
    Train one PPO agent per junction using a shared multi-junction environment.
    This is a lightweight cooperative MARL baseline suitable for project demos.
    """
    agents = []
    metadata = []
    for idx in range(n_junctions):
        env = Monitor(MultiJunctionTrafficEnv(
            config_path=config_path,
            n_junctions=n_junctions,
            use_gui=False,
        ))
        model = PPO("MlpPolicy", env, verbose=0)
        model.learn(total_timesteps=total_timesteps)
        save_path = f"models/marl_agent_{idx + 1}"
        model.save(save_path)
        env.close()
        agents.append(model)
        metadata.append({"agent_idx": idx + 1, "save_path": save_path})
    return metadata
