"""
src/transfer_learning.py — Junction transfer learning utilities.
"""
from stable_baselines3 import PPO, DQN
from stable_baselines3.common.monitor import Monitor

from controller import SumoTrafficEnv


def _algo_cls(algo: str):
    if algo == "PPO":
        return PPO
    if algo == "DQN":
        return DQN
    raise ValueError(f"Unsupported algorithm: {algo}")


def train_and_finetune(
    source_junction: str,
    target_junction: str,
    algo: str = "PPO",
    pretrain_steps: int = 10_000,
    finetune_steps: int = 5_000,
    config_path: str = "simulation/config.sumocfg",
    reward_type: str = "wait_time",
    save_path: str = "models/transfer_agent",
):
    """
    Train on one junction and fine-tune on another.
    Returns a dict with pre/post evaluation metadata.
    """
    cls = _algo_cls(algo)
    source_env = Monitor(SumoTrafficEnv(
        config_path=config_path,
        junction_id=source_junction,
        reward_type=reward_type,
        use_gui=False,
    ))
    model = cls("MlpPolicy", source_env, verbose=0)
    model.learn(total_timesteps=pretrain_steps)
    source_env.close()

    target_env = Monitor(SumoTrafficEnv(
        config_path=config_path,
        junction_id=target_junction,
        reward_type=reward_type,
        use_gui=False,
    ))
    model.set_env(target_env)
    model.learn(total_timesteps=finetune_steps, reset_num_timesteps=False)
    model.save(save_path)
    target_env.close()

    return {
        "algo": algo,
        "source_junction": source_junction,
        "target_junction": target_junction,
        "pretrain_steps": pretrain_steps,
        "finetune_steps": finetune_steps,
        "save_path": save_path,
    }
