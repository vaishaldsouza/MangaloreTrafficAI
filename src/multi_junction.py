"""
src/multi_junction.py — Multi-junction SUMO environment.

Controls multiple traffic-light junctions simultaneously using a single
flattened discrete action index. This keeps the API compatible with SB3 while
demonstrating scalability beyond one intersection.
"""
import os
import sys
import itertools
import numpy as np
import gymnasium as gym
from gymnasium import spaces

if "SUMO_HOME" in os.environ:
    sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
else:
    for fb in [
        "D:/SUMO/tools",
        "C:/Program Files (x86)/Eclipse/Sumo/tools",
        "C:/Program Files/Eclipse/Sumo/tools",
    ]:
        if os.path.isdir(fb):
            sys.path.append(fb)
            break

import traci


class MultiJunctionTrafficEnv(gym.Env):
    """Jointly control the first N traffic lights in the SUMO network."""

    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        config_path: str = "simulation/config.sumocfg",
        use_gui: bool = False,
        max_steps: int = 3600,
        n_junctions: int = 2,
        reward_type: str = "wait_time",
    ):
        super().__init__()
        self.config_path = config_path
        self.use_gui = use_gui
        self.max_steps = max_steps
        self.n_junctions = n_junctions
        self.reward_type = reward_type
        self.step_count = 0
        self._sumo_running = False
        self.junction_ids = []
        self.junction_lanes = {}
        self.phase_counts = []
        self._action_map = []
        self._obs_lanes = 0
        self._start_sumo()

    def _start_sumo(self):
        try:
            traci.close()
        except Exception:
            pass

        binary = "sumo-gui" if self.use_gui else "sumo"
        traci.start([binary, "-c", self.config_path, "--no-warnings", "true", "--no-step-log", "true"])
        self._sumo_running = True

        tl_ids = list(traci.trafficlight.getIDList())
        if not tl_ids:
            raise RuntimeError("No traffic lights found in the loaded SUMO network.")

        self.junction_ids = tl_ids[: max(1, min(self.n_junctions, len(tl_ids)))]
        self.junction_lanes = {
            tl_id: list(set(traci.trafficlight.getControlledLanes(tl_id)))
            for tl_id in self.junction_ids
        }
        self.phase_counts = [
            len(traci.trafficlight.getAllProgramLogics(tl_id)[0].phases)
            for tl_id in self.junction_ids
        ]
        self._action_map = list(itertools.product(*[range(n) for n in self.phase_counts]))
        self._obs_lanes = sum(len(self.junction_lanes[tl_id]) for tl_id in self.junction_ids)
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(self._obs_lanes * 2,),
            dtype=np.float32,
        )
        self.action_space = spaces.Discrete(len(self._action_map))

    def _decode_action(self, action: int):
        return self._action_map[int(action)]

    def _get_obs(self):
        counts, waits = [], []
        for tl_id in self.junction_ids:
            for lane in self.junction_lanes[tl_id]:
                counts.append(traci.lane.getLastStepVehicleNumber(lane) / 20.0)
                waits.append(traci.lane.getWaitingTime(lane) / 300.0)
        return np.clip(np.array(counts + waits, dtype=np.float32), 0.0, 1.0)

    def _get_reward(self):
        if self.reward_type == "throughput":
            return float(traci.simulation.getArrivedNumber())
        total_wait = 0.0
        for tl_id in self.junction_ids:
            total_wait += sum(traci.lane.getWaitingTime(lane) for lane in self.junction_lanes[tl_id])
        return -total_wait / 1000.0

    def _get_info(self):
        junction_counts = {}
        total_queue = 0
        for tl_id in self.junction_ids:
            counts = {
                lane: traci.lane.getLastStepVehicleNumber(lane)
                for lane in self.junction_lanes[tl_id]
            }
            junction_counts[tl_id] = counts
            total_queue += sum(counts.values())
        return {
            "step": self.step_count,
            "junction_ids": self.junction_ids,
            "junction_lane_counts": junction_counts,
            "total_queue": total_queue,
            "total_vehicles": traci.simulation.getMinExpectedNumber(),
            "phases": {tl_id: traci.trafficlight.getPhase(tl_id) for tl_id in self.junction_ids},
        }

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.step_count = 0
        self._start_sumo()
        for _ in range(10):
            traci.simulationStep()
        return self._get_obs(), self._get_info()

    def step(self, action: int):
        for tl_id, phase in zip(self.junction_ids, self._decode_action(action)):
            traci.trafficlight.setPhase(tl_id, int(phase))
        for _ in range(5):
            traci.simulationStep()
        self.step_count += 1
        obs = self._get_obs()
        reward = self._get_reward()
        info = self._get_info()
        terminated = (
            self.step_count >= self.max_steps // 5
            or traci.simulation.getMinExpectedNumber() == 0
        )
        return obs, reward, terminated, False, info

    def close(self):
        if self._sumo_running:
            traci.close()
            self._sumo_running = False
