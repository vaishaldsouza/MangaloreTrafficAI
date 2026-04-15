"""
Entry point: trains PPO against the real Mangalore SUMO simulation.
Run: py src/train.py
"""
import sys
sys.path.insert(0, "src")

from controller import SumoTrafficEnv
from model import TrafficRLModel, compare_baseline_vs_rl
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.monitor import Monitor

def make_env():
    def _init():
        env = SumoTrafficEnv(
            config_path="simulation/config.sumocfg",
            use_gui=False,
            max_steps=3600,
        )
        return Monitor(env)
    return _init

if __name__ == "__main__":
    # Single-env sanity check first
    print("Checking environment...")
    env = SumoTrafficEnv(config_path="simulation/config.sumocfg", use_gui=False)
    check_env(env, warn=True)
    env.close()
    print("Environment OK.")

    # Train with a single env (safe for SUMO)
    train_env = Monitor(SumoTrafficEnv(
        config_path="simulation/config.sumocfg", use_gui=False
    ))
    model = TrafficRLModel(algo="PPO", model_path="models/ppo_mangalore_sumo")
    model.train(train_env, total_timesteps=10_000)
    train_env.close()

    # Compare against fixed-cycle baseline
    compare_baseline_vs_rl(
        env_class=SumoTrafficEnv,
        env_kwargs={"config_path": "simulation/config.sumocfg", "use_gui": False},
        model_path="models/ppo_mangalore_sumo",
        n_episodes=3,
    )
