import numpy as np
from stable_baselines3 import PPO, DQN
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.monitor import Monitor
import os

class TrafficRLModel:
    def __init__(self, algo="PPO", model_path="models/traffic_model"):
        self.algo = algo
        self.model_path = model_path
        self.model = None
        os.makedirs("models", exist_ok=True)

    def train(self, env, total_timesteps=50_000):
        """Train the RL agent."""
        check_env(env)  # validates your custom env
        env = Monitor(env)

        if self.algo == "PPO":
            self.model = PPO(
                "MlpPolicy", env,
                learning_rate=3e-4,
                n_steps=2048,
                batch_size=64,
                n_epochs=10,
                verbose=1
            )
        elif self.algo == "DQN":
            self.model = DQN(
                "MlpPolicy", env,
                learning_rate=1e-4,
                buffer_size=50_000,
                learning_starts=1000,
                batch_size=32,
                verbose=1
            )

        self.model.learn(total_timesteps=total_timesteps)
        self.model.save(self.model_path)
        print(f"Model saved to {self.model_path}")
        return self.model

    def load(self):
        """Load a saved model."""
        if self.algo == "PPO":
            self.model = PPO.load(self.model_path)
        elif self.algo == "DQN":
            self.model = DQN.load(self.model_path)
        print(f"Model loaded from {self.model_path}")

    def predict(self, observation):
        """Get the next action from the trained model."""
        if self.model is None:
            # Fallback: greedy — pick lane with most vehicles
            return int(np.argmax(observation)), None
        action, _states = self.model.predict(observation, deterministic=True)
        return int(action), _states

    def evaluate(self, env, n_episodes=10):
        """Run evaluation episodes and return avg reward."""
        rewards = []
        for _ in range(n_episodes):
            obs, _ = env.reset()
            total_reward = 0
            done = False
            while not done:
                action, _ = self.predict(obs)
                obs, reward, terminated, truncated, _ = env.step(action)
                total_reward += reward
                done = terminated or truncated
            rewards.append(total_reward)
        avg = np.mean(rewards)
        print(f"Avg reward over {n_episodes} episodes: {avg:.4f}")
        return avg

def compare_baseline_vs_rl(env_class, env_kwargs, model_path, n_episodes=5):
    """
    Run side-by-side comparison: fixed-cycle baseline vs trained RL agent.
    Returns dict of avg rewards for both.
    """
    import numpy as np

    # --- Baseline: fixed cycle (rotate phases every 30s = 6 steps) ---
    baseline_rewards = []
    for _ in range(n_episodes):
        env = env_class(**env_kwargs)
        obs, _ = env.reset()
        total_r, done, step = 0, False, 0
        while not done:
            action = step % env.action_space.n   # round-robin
            obs, r, terminated, truncated, _ = env.step(action)
            total_r += r
            done = terminated or truncated
            step += 1
        baseline_rewards.append(total_r)
        env.close()

    # --- RL agent ---
    rl_model = TrafficRLModel(model_path=model_path)
    rl_model.load()
    rl_rewards = []
    for _ in range(n_episodes):
        env = env_class(**env_kwargs)
        obs, _ = env.reset()
        total_r, done = 0, False
        while not done:
            action, _ = rl_model.predict(obs)
            obs, r, terminated, truncated, _ = env.step(action)
            total_r += r
            done = terminated or truncated
        rl_rewards.append(total_r)
        env.close()

    results = {
        "baseline_avg": float(np.mean(baseline_rewards)),
        "rl_avg": float(np.mean(rl_rewards)),
        "improvement_pct": float(
            (np.mean(rl_rewards) - np.mean(baseline_rewards))
            / abs(np.mean(baseline_rewards)) * 100
        ),
    }
    print(f"Baseline avg reward: {results['baseline_avg']:.4f}")
    print(f"RL avg reward:       {results['rl_avg']:.4f}")
    print(f"Improvement:         {results['improvement_pct']:.1f}%")
    return results
