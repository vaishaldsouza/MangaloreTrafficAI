"""
Entry point: trains PPO against the real Mangalore SUMO simulation.
Run: py src/train.py
"""
import argparse
import sys
sys.path.insert(0, "src")

from controller import SumoTrafficEnv
from model import TrafficRLModel, compare_baseline_vs_rl
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.monitor import Monitor

def make_env(reward_type="wait_time"):
    def _init():
        env = SumoTrafficEnv(
            config_path="simulation/config.sumocfg",
            use_gui=False,
            max_steps=3600,
            reward_type=reward_type,
        )
        return Monitor(env)
    return _init


def parse_args():
    parser = argparse.ArgumentParser(description="Train PPO or DQN on the SUMO traffic environment.")
    parser.add_argument("--algo", choices=["PPO", "DQN"], default="PPO")
    parser.add_argument("--timesteps", type=int, default=10_000)
    parser.add_argument("--reward-type", choices=["wait_time", "throughput"], default="wait_time")
    parser.add_argument("--model-path", default=None)
    parser.add_argument("--curve-path", default=None,
                        help="Optional CSV path to save the learning curve.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    model_path = args.model_path or f"models/{args.algo.lower()}_mangalore_sumo"
    curve_path = args.curve_path or f"models/{args.algo.lower()}_learning_curve.csv"

    # Single-env sanity check first
    print("Checking environment...")
    env = SumoTrafficEnv(
        config_path="simulation/config.sumocfg",
        use_gui=False,
        reward_type=args.reward_type,
    )
    check_env(env, warn=True)
    env.close()
    print("Environment OK.")

    # Train with a single env (safe for SUMO)
    train_env = Monitor(SumoTrafficEnv(
        config_path="simulation/config.sumocfg",
        use_gui=False,
        reward_type=args.reward_type,
    ))
    model = TrafficRLModel(algo=args.algo, model_path=model_path)
    model.train(train_env, total_timesteps=args.timesteps)
    model.save_training_curve(curve_path)
    train_env.close()

    # Compare against fixed-cycle baseline
    compare_baseline_vs_rl(
        env_class=SumoTrafficEnv,
        env_kwargs={
            "config_path": "simulation/config.sumocfg",
            "use_gui": False,
            "reward_type": args.reward_type,
        },
        model_path=model_path,
        n_episodes=3,
    )
