"""
src/multi_agent_rl.py — Cooperative multi-agent RL over multiple junctions.

Implements a practical independent-PPO baseline for each controlled junction.
"""
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

from multi_junction import MultiJunctionTrafficEnv


def train_independent_ppo_agents(
    n_junctions: int = 2,
    total_timesteps: int = 100_000,
    config_path: str = "simulation/config.sumocfg",
):
    env = Monitor(MultiJunctionTrafficEnv(
        config_path=config_path,
        n_junctions=n_junctions,
        use_gui=False,
    ))
    
    # Single PPO on the joint action space (all junctions at once)
    model = PPO(
        "MlpPolicy", env,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        verbose=1,
    )
    model.learn(total_timesteps=total_timesteps)
    model.save("models/marl_joint")
    env.close()
    return model
