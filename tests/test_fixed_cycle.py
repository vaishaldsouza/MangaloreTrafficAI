import numpy as np
import pytest
from unittest.mock import MagicMock
from baselines.fixed_cycle import run_fixed_cycle

def make_mock_env(n_steps=20, n_actions=4):
    env = MagicMock()
    env.action_space.n = n_actions
    obs = np.zeros(8)
    env.reset.return_value = (obs, {})
    
    step_count = {"n": 0}
    def fake_step(action):
        step_count["n"] += 1
        done = step_count["n"] >= n_steps
        return obs, -1.0, done, False, {"lane_counts": {"l0": 5, "l1": 3, "l2": 7, "l3": 2}}
    env.step.side_effect = fake_step
    return env

def test_fixed_cycle_returns_float():
    env = make_mock_env()
    result = run_fixed_cycle(env, cycle_duration=5)
    assert isinstance(result, float)

def test_fixed_cycle_avg_is_positive():
    env = make_mock_env()
    result = run_fixed_cycle(env, cycle_duration=5)
    assert result > 0

def test_fixed_cycle_rotates_phases():
    env = make_mock_env(n_steps=40, n_actions=4)
    run_fixed_cycle(env, cycle_duration=10)
    actions_used = {call.args[0] for call in env.step.call_args_list}
    assert len(actions_used) > 1   # must have used multiple phases
