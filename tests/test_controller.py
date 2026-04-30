import pytest
import numpy as np
from src.controller import SumoTrafficEnv

def test_controller_init():
    # Test initialization without starting SUMO
    env = SumoTrafficEnv(backend="Python Simulator", max_steps=100)
    assert env.backend == "Python Simulator"
    assert env.step_count == 0
    env.close()

def test_step():
    env = SumoTrafficEnv(backend="Python Simulator", max_steps=100)
    obs, info = env.reset()
    action = 0
    new_obs, reward, terminated, truncated, info = env.step(action)
    assert len(new_obs) == 8  # 4 lane counts + 4 wait times
    assert isinstance(reward, float)
    env.close()

def test_reset():
    env = SumoTrafficEnv(backend="Python Simulator", max_steps=100)
    obs, info = env.reset()
    assert len(obs) == 8
    assert env.step_count == 0
    env.close()
