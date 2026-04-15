import os
import sys
import numpy as np
import gymnasium as gym
from gymnasium import spaces

if "SUMO_HOME" in os.environ:
    sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
else:
    # Typical fallback paths (User should ideally set SUMO_HOME in env variables)
    sys.path.append("C:/Program Files (x86)/Eclipse/Sumo/tools") 

import traci
import traci.constants as tc


class SumoTrafficEnv(gym.Env):
    """
    Gymnasium environment wrapping a real SUMO Mangalore simulation.
    One env instance = one episode (one SUMO run).

    Observation: normalized vehicle counts + avg wait time per lane at
                 the chosen junction (flattened to 1D array).
    Action:      integer index of the traffic light phase to activate.
    Reward:      negative total waiting time across all controlled lanes.
    """

    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        config_path="simulation/config.sumocfg",
        junction_id="cluster_1",   # replace with actual TL id after generating network
        use_gui=False,
        max_steps=3600,
    ):
        super().__init__()
        self.config_path = config_path
        self.junction_id = junction_id
        self.use_gui = use_gui
        self.max_steps = max_steps
        self.step_count = 0
        self._sumo_running = False

        self._num_lanes = 8       # typical 4-way junction
        self._num_phases = 4
        
        # Start SUMO once to figure out actual lane counts & num phases
        self._start_sumo()

        # obs = [vehicle_count/lane (norm), avg_wait/lane (norm)] -> 2 x num_lanes
        self.observation_space = spaces.Box(
            low=0.0, high=1.0,
            shape=(self._num_lanes * 2,),
            dtype=np.float32,
        )
        self.action_space = spaces.Discrete(self._num_phases)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _start_sumo(self):
        try:
            traci.close()
        except Exception:
            pass

        binary = "sumo-gui" if self.use_gui else "sumo"
        traci.start([binary, "-c", self.config_path,
                     "--no-warnings", "true",
                     "--no-step-log", "true"])
        self._sumo_running = True

        # Discover the actual traffic light IDs in the network
        tl_ids = traci.trafficlight.getIDList()
        if not tl_ids:
            raise RuntimeError("No traffic lights found in the network. "
                               "Re-run generate_network.py with --tls.guess-signals")
        # Use the first TL if the configured one isn't found
        if self.junction_id not in tl_ids:
            self.junction_id = tl_ids[0]
            print(f"[ENV] Using traffic light: {self.junction_id}")

        self._controlled_lanes = list(set(traci.trafficlight.getControlledLanes(self.junction_id)))
        self._num_lanes = len(self._controlled_lanes)
        self._num_phases = len(
            traci.trafficlight.getAllProgramLogics(self.junction_id)[0].phases
        )
        # Update spaces now that we know real sizes
        self.observation_space = spaces.Box(
            low=0.0, high=1.0,
            shape=(self._num_lanes * 2,),
            dtype=np.float32,
        )
        self.action_space = spaces.Discrete(self._num_phases)

    def _get_obs(self):
        counts, waits = [], []
        for lane in self._controlled_lanes:
            counts.append(traci.lane.getLastStepVehicleNumber(lane) / 20.0)
            waits.append(traci.lane.getWaitingTime(lane) / 300.0)   # norm to 5 min
        obs = np.array(counts + waits, dtype=np.float32)
        return np.clip(obs, 0.0, 1.0)

    def _get_reward(self):
        """Reward = negative cumulative waiting time across all controlled lanes."""
        total_wait = sum(
            traci.lane.getWaitingTime(lane)
            for lane in self._controlled_lanes
        )
        return -total_wait / 1000.0   # scale down

    def _get_info(self):
        counts = {
            lane: traci.lane.getLastStepVehicleNumber(lane)
            for lane in self._controlled_lanes
        }
        return {
            "step": self.step_count,
            "junction_id": self.junction_id,
            "lane_counts": counts,
            "current_phase": traci.trafficlight.getPhase(self.junction_id),
            "total_vehicles": traci.simulation.getMinExpectedNumber(),
        }

    # ------------------------------------------------------------------
    # Gymnasium API
    # ------------------------------------------------------------------

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.step_count = 0
        self._start_sumo()
        # Warm up the simulation a few steps before the agent starts
        for _ in range(10):
            traci.simulationStep()
        obs = self._get_obs()
        return obs, self._get_info()

    def step(self, action):
        # Apply action: set the chosen phase
        traci.trafficlight.setPhase(self.junction_id, int(action))

        # Advance simulation by 5 steps (5 seconds)
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
        truncated = False

        return obs, reward, terminated, truncated, info

    def render(self):
        pass   # SUMO-GUI handles rendering when use_gui=True

    def close(self):
        if self._sumo_running:
            traci.close()
            self._sumo_running = False
