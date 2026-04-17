"""
src/curriculum_learning.py — Curriculum RL training utilities.
"""
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

from controller import SumoTrafficEnv
from scenarios import get_scenario


def train_curriculum(
    curriculum_steps=None,
    timesteps_per_stage: int = 5_000,
    save_path: str = "models/curriculum_ppo",
):
    """
    Train PPO through progressively harder traffic scenarios.
    """
    curriculum_steps = curriculum_steps or [
        "Weekend",
        "Normal",
        "Rush Hour AM",
        "Heavy Rain",
        "Accident",
    ]
    model = None
    history = []
    for idx, scen_name in enumerate(curriculum_steps):
        env = Monitor(SumoTrafficEnv(
            config_path="simulation/config.sumocfg",
            scenario=get_scenario(scen_name),
            use_gui=False,
        ))
        if model is None:
            model = PPO("MlpPolicy", env, verbose=0)
        else:
            model.set_env(env)
        model.learn(total_timesteps=timesteps_per_stage, reset_num_timesteps=False)
        history.append({"stage": idx + 1, "scenario": scen_name, "timesteps": timesteps_per_stage})
        env.close()

    model.save(save_path)
    return history
