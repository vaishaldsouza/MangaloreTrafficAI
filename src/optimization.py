"""
src/optimization.py — Hyperparameter tuning for PPO using Optuna.

Tuning parameters:
  - learning_rate
  - n_steps
  - gamma
  - batch_size

Usage:
    python -m src.optimization
"""
import os
import sys
import optuna
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import EvalCallback

# Ensure project root is in path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.controller import SumoTrafficEnv

DB_PATH = "simulation/logs.db"
os.makedirs("simulation", exist_ok=True)

def objective(trial: optuna.Trial):
    # Suggest hyperparameters
    learning_rate = trial.suggest_float("learning_rate", 1e-5, 1e-3, log=True)
    n_steps = trial.suggest_categorical("n_steps", [1024, 2048, 4096])
    gamma = trial.suggest_float("gamma", 0.9, 0.9999)
    batch_size = trial.suggest_categorical("batch_size", [32, 64, 128])

    # Create environment
    # Use a shorter max_steps for faster trials
    env = Monitor(SumoTrafficEnv(config_path="simulation/config.sumocfg", 
                                 use_gui=False, 
                                 max_steps=1800))
    eval_env = Monitor(SumoTrafficEnv(config_path="simulation/config.sumocfg", 
                                      use_gui=False, 
                                      max_steps=1800))

    try:
        model = PPO(
            "MlpPolicy",
            env,
            learning_rate=learning_rate,
            n_steps=n_steps,
            batch_size=batch_size,
            gamma=gamma,
            verbose=0
        )

        # Train for a small number of timesteps per trial
        # In a real study, use 50k-100k
        model.learn(total_timesteps=10000)

        # Evaluate
        eval_rewards = []
        for _ in range(3):
            obs, _ = eval_env.reset()
            done = False
            total_r = 0
            while not done:
                action, _ = model.predict(obs, deterministic=True)
                obs, r, terminated, truncated, _ = eval_env.step(action)
                total_r += r
                done = terminated or truncated
            eval_rewards.append(total_r)
        
        avg_reward = np.mean(eval_rewards)
    finally:
        env.close()
        eval_env.close()

    return avg_reward

def run_optimization(n_trials=10):
    print(f"[Optuna] Starting optimization with {n_trials} trials...")
    
    # Use SQLite for persistence
    storage = f"sqlite:///{DB_PATH}"
    study = optuna.create_study(
        study_name="ppo_mangalore_tuning",
        storage=storage,
        direction="maximize",
        load_if_exists=True
    )
    
    study.optimize(objective, n_trials=n_trials)

    print("\n" + "="*40)
    print("  OPTIMIZATION COMPLETE")
    print("="*40)
    print(f"  Best trial:  {study.best_trial.number}")
    print(f"  Best value: {study.best_value:.4f}")
    print("  Best params:")
    for key, value in study.best_params.items():
        print(f"    {key}: {value}")
    print("="*40)
    
    return study.best_params

if __name__ == "__main__":
    run_optimization(n_trials=5)
