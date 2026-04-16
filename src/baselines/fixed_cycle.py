"""
src/baselines/fixed_cycle.py

Method 1 — Fixed-cycle baseline.
Simulates the traditional fixed-timer traffic signal as it exists in most
real-world Mangalore junctions today. Rotates N-S / E-W every
`cycle_duration` steps (5s each) regardless of how many cars are waiting.

Run:
    python -m src.baselines.fixed_cycle
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np


def run_fixed_cycle(env, cycle_duration=30):
    """
    Simulates the current Mangalore fixed-cycle signal.
    Rotates N-S / E-W every 'cycle_duration' steps regardless of traffic.

    Returns:
        avg_queue (float): average queue length per step (vehicles/step).
                           This is the number your RL agent must beat.
    """
    obs, _ = env.reset()
    total_wait, steps, phase = 0, 0, 0

    done = False
    while not done:
        # Fixed rotation — ignores observation completely
        action = (phase // cycle_duration) % env.action_space.n
        obs, reward, terminated, truncated, info = env.step(action)
        total_wait += sum(info["lane_counts"].values())
        steps += 1
        phase += 1
        done = terminated or truncated

    avg = total_wait / max(steps, 1)
    print(f"[Fixed-cycle] Avg queue length: {avg:.2f} vehicles/step")
    return avg


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from controller import SumoTrafficEnv

    N_EPISODES = 3
    results = []
    for ep in range(N_EPISODES):
        env = SumoTrafficEnv(config_path="simulation/config.sumocfg", use_gui=False)
        avg = run_fixed_cycle(env, cycle_duration=30)
        results.append(avg)
        env.close()

    print(f"\n=== Fixed-cycle summary ({N_EPISODES} episodes) ===")
    print(f"  Mean avg queue : {np.mean(results):.2f} vehicles/step")
    print(f"  Std            : {np.std(results):.2f}")
