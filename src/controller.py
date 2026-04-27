"""
src/controller.py — Gymnasium environment wrapping SUMO via TraCI.

Enhancements over v1:
  • ScenarioConfig support (demand multiplier, speed factor, accident)
  • Weather simulation (road speed scaling)
  • Lane accident closure at configurable step
  • CO₂ emission tracking per step
  • Junction position export for the map overlay
"""
import os
import sys
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
import traci.constants as tc

# CV Imports (optional/lazy)
try:
    from .cv.cv_pipeline import CVPipeline
    from .cv.sumo_virtual_camera import render_topdown_frame, get_junction_bounds
    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False


class SumoTrafficEnv(gym.Env):
    """
    Gymnasium environment wrapping either a real SUMO simulation or a pure Python stochastic model.
    """

    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        config_path: str = "simulation/config.sumocfg",
        junction_id: str = "cluster_1",
        use_gui: bool = False,
        max_steps: int = 3600,
        scenario=None,            # ScenarioConfig | None
        reward_type: str = "wait_time",  # "wait_time" or "throughput"
        use_cv: bool = False,
        backend: str = "SUMO"     # "SUMO" or "Python Simulator"
    ):

        super().__init__()
        self.config_path   = config_path
        self.junction_id   = junction_id
        self.use_gui       = use_gui
        self.max_steps     = max_steps
        self.scenario      = scenario
        self.reward_type   = reward_type
        self.backend       = backend
        self.step_count    = 0
        self._sumo_running = False
        self._accident_done = False
        self.use_cv = use_cv
        self.cv_pipeline = None

        # State for Python Simulator
        self._python_queues = np.zeros(4, dtype=float)
        self._last_served = 0.0

        if self.use_cv and not CV_AVAILABLE:
            print("[WARN] CV requested but dependencies missing. Falling back to TraCI.")
            self.use_cv = False

        if self.backend == "SUMO":
            self._num_lanes  = 8
            self._num_phases = 4
            self._start_sumo()
        else:
            # Python simulator defaults
            self._num_lanes = 4
            self._num_phases = 4

        self.observation_space = spaces.Box(
            low=0.0, high=1.0,
            shape=(self._num_lanes * 2,),
            dtype=np.float32,
        )
        self.action_space = spaces.Discrete(self._num_phases)

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _start_sumo(self):
        try:
            traci.close()
        except Exception:
            pass

        binary = "sumo-gui" if self.use_gui else "sumo"

        cmd = [binary, "-c", self.config_path,
               "--no-warnings", "true",
               "--no-step-log", "true"]

        if self.scenario is not None:
            os.makedirs("simulation/output", exist_ok=True)
            cmd += ["--emission-output", "simulation/output/emissions.xml"]

        traci.start(cmd)
        self._sumo_running = True
        self._accident_done = False

        tl_ids = traci.trafficlight.getIDList()
        if not tl_ids:
            return # might be just testing backend=Python
        if self.junction_id not in tl_ids:
            self.junction_id = tl_ids[0]

        self._controlled_lanes = list(
            set(traci.trafficlight.getControlledLanes(self.junction_id))
        )
        self._num_lanes = len(self._controlled_lanes)
        self._num_phases = len(
            traci.trafficlight.getAllProgramLogics(self.junction_id)[0].phases
        )

        self.observation_space = spaces.Box(
            low=0.0, high=1.0,
            shape=(self._num_lanes * 2,),
            dtype=np.float32,
        )
        self.action_space = spaces.Discrete(self._num_phases)

        if self.use_cv and CV_AVAILABLE:
            bounds = get_junction_bounds(self.junction_id)
            self.cv_pipeline = CVPipeline(frame_width=640, frame_height=480)

        if self.scenario is not None:
            self._apply_scenario()

        self._add_pedestrian_phase()

    def _apply_scenario(self):
        if self.backend != "SUMO": return
        sc = self.scenario
        if sc.speed_factor != 1.0:
            for edge_id in traci.edge.getIDList():
                try:
                    orig = traci.edge.getMaxSpeed(edge_id)
                    traci.edge.setMaxSpeed(edge_id, orig * sc.speed_factor)
                except Exception:
                    pass

    def _apply_accident(self):
        if self.backend == "SUMO":
            if self._controlled_lanes:
                lane = self._controlled_lanes[0]
                try:
                    traci.lane.setMaxSpeed(lane, 0.5)
                    traci.lane.setDisallowed(lane, ["passenger", "bus"])
                except Exception:
                    pass
        self._accident_done = True

    def _get_obs(self) -> np.ndarray:
        if self.backend == "Python Simulator":
            # 4 lane queues normalized + 4 saturation + 4 padding
            return np.concatenate([
                self._python_queues / 20.0,
                np.clip(self._python_queues / 50.0, 0, 1),
                np.zeros(max(0, self._num_lanes * 2 - 8), dtype=np.float32)
            ]).astype(np.float32)[:self._num_lanes * 2]

        if self.use_cv and self.cv_pipeline is not None:
            # Grab frame from virtual camera and run CV
            frame = render_topdown_frame(self.junction_id)
            counts = self.cv_pipeline.process_frame(frame)
            # Build same shape as TraCI obs: [counts..., waits...]
            lanes = list(counts.keys())
            count_vec = [counts.get(l, 0) / 20.0 for l in lanes]
            # Waits still come from TraCI (CV can't measure these)
            wait_vec = [traci.lane.getWaitingTime(l) / 300.0 for l in self._controlled_lanes]
            obs = count_vec + wait_vec[:len(count_vec)]
            return np.clip(np.array(obs, dtype=np.float32), 0.0, 1.0)

        # Original TraCI path
        counts = [traci.lane.getLastStepVehicleNumber(l) / 20.0 for l in self._controlled_lanes]
        waits  = [traci.lane.getWaitingTime(l) / 300.0 for l in self._controlled_lanes]
        return np.clip(np.array(counts + waits, dtype=np.float32), 0.0, 1.0)

    def _get_reward(self) -> float:
        if self.backend == "Python Simulator":
            if self.reward_type == "throughput":
                return float(self._last_served)
            return -float(np.sum(self._python_queues)) / 20.0

        if self.reward_type == "throughput":
            return float(traci.simulation.getArrivedNumber())
        
        total_wait = sum(
            traci.lane.getWaitingTime(lane)
            for lane in self._controlled_lanes
        )
        return -total_wait / 1000.0

    def _get_co2(self) -> float:
        if self.backend == "Python Simulator":
            return float(np.sum(self._python_queues)) * 120.0
        total = 0.0
        try:
            for vid in traci.vehicle.getIDList():
                total += traci.vehicle.getCO2Emission(vid)
        except Exception:
            pass
        return total

    def _get_info(self) -> dict:
        if self.backend == "Python Simulator":
            # Mock vehicles for the map
            vehicles = []
            for i in range(int(np.sum(self._python_queues))):
                vehicles.append({
                    "id": f"v_{i}",
                    "lat": 12.8700 + (np.random.rand() - 0.5) * 0.005,
                    "lng": 74.8436 + (np.random.rand() - 0.5) * 0.005,
                    "speed": 10.5,
                    "type": "passenger"
                })
            
            info = {
                "step":           self.step_count,
                "junction_id":    "virtual_1",
                "lane_counts":    {f"lane_{i}": int(q) for i, q in enumerate(self._python_queues)},
                "total_queue":    float(np.sum(self._python_queues)),
                "current_phase":  0,
                "phase_name":     "Python Adaptive",
                "total_vehicles": int(np.sum(self._python_queues) + self._last_served),
                "vehicles":       vehicles,
                "co2_mg":         self._get_co2(),
                "congestion":     "free" if np.sum(self._python_queues) < 5 else ("moderate" if np.sum(self._python_queues) < 12 else "high"),
            }
            return info

        counts = {
            lane: traci.lane.getLastStepVehicleNumber(lane)
            for lane in self._controlled_lanes
        }
        
        vehicles = []
        try:
            for vid in traci.vehicle.getIDList():
                x, y = traci.vehicle.getPosition(vid)
                lon, lat = traci.simulation.convertGeo(x, y)
                vehicles.append({
                    "id": vid,
                    "lat": lat,
                    "lng": lon,
                    "speed": traci.vehicle.getSpeed(vid),
                    "type": traci.vehicle.getTypeID(vid)
                })
        except Exception:
            pass

        try:
            logic = traci.trafficlight.getAllProgramLogics(self.junction_id)[0]
            phase_idx = traci.trafficlight.getPhase(self.junction_id)
            phase_name = logic.phases[phase_idx].name or f"Phase {phase_idx}"
        except Exception:
            phase_name = f"Phase {traci.trafficlight.getPhase(self.junction_id)}"

        total_q = sum(counts.values())
        info = {
            "step":           self.step_count,
            "junction_id":    self.junction_id,
            "lane_counts":    counts,
            "total_queue":    float(total_q),
            "current_phase":  traci.trafficlight.getPhase(self.junction_id),
            "phase_name":     phase_name,
            "total_vehicles": traci.simulation.getMinExpectedNumber(),
            "vehicles":       vehicles,
            "co2_mg":         self._get_co2(),
            "scenario":       self.scenario.name if self.scenario else "Normal",
            "accident_active": self._accident_done,
            "congestion":     "free" if total_q < 5 else ("moderate" if total_q < 12 else "high"),
        }
        return info

    def _check_emergency_preempt(self):
        """Force green for the lane with an approaching emergency vehicle."""
        for veh_id in traci.vehicle.getIDList():
            if traci.vehicle.getTypeID(veh_id) == "emergency":
                lane = traci.vehicle.getLaneID(veh_id)
                if lane in self._controlled_lanes:
                    lane_idx = self._controlled_lanes.index(lane)
                    # Set phase that gives green to this lane index
                    emergency_phase = lane_idx % self._num_phases
                    traci.trafficlight.setPhase(self.junction_id, emergency_phase)
                    return True
        return False

    def _add_pedestrian_phase(self):
        """Inject an all-red pedestrian clearance phase programmatically."""
        if self.backend != "SUMO": return
        try:
            logic = traci.trafficlight.getAllProgramLogics(self.junction_id)[0]
            # Create an all-red state (e.g., "rrrrrrrr")
            num_signals = len(logic.phases[0].state)
            red_state = "r" * num_signals
            new_phase = traci.trafficlight.Phase(duration=10, state=red_state, name="Pedestrian Crossing")
            
            phases = list(logic.phases)
            phases.append(new_phase)
            logic.phases = tuple(phases)
            
            traci.trafficlight.setProgramLogic(self.junction_id, logic)
            self._num_phases = len(phases)
            self.action_space = spaces.Discrete(self._num_phases)
            print(f"[INFO] Injected Pedestrian Phase into {self.junction_id}")
        except Exception as e:
            print(f"[ERROR] Failed to inject pedestrian phase: {e}")

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.step_count = 0
        if self.backend == "SUMO":
            self._start_sumo()
            for _ in range(10): traci.simulationStep()
        else:
            self._python_queues = np.zeros(4, dtype=float)
            self._last_served = 0.0
        return self._get_obs(), self._get_info()

    def step(self, action: int):
        if self.backend == "SUMO":
            preempted = self._check_emergency_preempt()
            if not preempted:
                traci.trafficlight.setPhase(self.junction_id, int(action))
            for _ in range(5):
                traci.simulationStep()
            self.step_count += 1
            return self._get_obs(), self._get_reward(), self.step_count >= self.max_steps // 5 or traci.simulation.getMinExpectedNumber() == 0, False, self._get_info()
        else:
            # Python Stochastic Step
            demand_multiplier = self.scenario.demand_multiplier if self.scenario else 1.0
            split = np.array([0.30, 0.25, 0.25, 0.20])
            arrivals = np.random.poisson(demand_multiplier * split * 2.0)
            self._python_queues += arrivals
            
            service = np.zeros(4)
            if action in [0, 1]:
                service[0] = 2.5 if action == 0 else 0.3
                service[1] = 2.5 if action == 0 else 0.3
            else:
                service[2] = 2.5 if action == 2 else 0.3
                service[3] = 2.5 if action == 2 else 0.3
            
            served = np.minimum(self._python_queues, service)
            self._python_queues = np.maximum(0.0, self._python_queues - served)
            self._last_served = float(np.sum(served))
            
            self.step_count += 1
            return self._get_obs(), self._get_reward(), self.step_count >= self.max_steps, False, self._get_info()

    def get_junction_map_data(self) -> list[tuple]:
        if self.backend != "SUMO": return []
        result = []
        try:
            for tl_id in traci.trafficlight.getIDList():
                lanes = traci.trafficlight.getControlledLanes(tl_id)
                if not lanes: continue
                x, y = traci.lane.getShape(lanes[0])[0]
                lon, lat = traci.simulation.convertGeo(x, y)
                queue = sum(traci.lane.getLastStepVehicleNumber(l) for l in set(lanes))
                cong = "free" if queue < 5 else ("moderate" if queue < 12 else "high")
                result.append((lat, lon, tl_id, cong))
        except Exception: pass
        return result

    def render(self):
        pass

    def close(self):
        if self._sumo_running:
            traci.close()
            self._sumo_running = False
