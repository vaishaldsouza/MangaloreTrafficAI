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
    Gymnasium environment wrapping a real SUMO Mangalore simulation.
    One env instance = one episode (one SUMO run).

    Observation : normalized vehicle counts + avg wait time per lane at
                  the controlled junction (flattened 1-D array).
    Action      : integer index of the traffic light phase to activate.
    Reward      : negative total waiting time across all controlled lanes.

    Args:
        config_path   : path to the .sumocfg file
        junction_id   : traffic-light node id (auto-detected if wrong)
        use_gui       : open SUMO-GUI window
        max_steps     : episode length in env steps (1 step = 5 SUMO seconds)
        scenario      : ScenarioConfig from scenarios.py (optional)
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
    ):

        super().__init__()
        self.config_path   = config_path
        self.junction_id   = junction_id
        self.use_gui       = use_gui
        self.max_steps     = max_steps
        self.scenario      = scenario
        self.reward_type   = reward_type
        self.step_count    = 0
        self._sumo_running = False
        self._accident_done = False
        self.use_cv = use_cv
        self.cv_pipeline = None

        if self.use_cv and not CV_AVAILABLE:
            print("[WARN] CV requested but dependencies missing. Falling back to TraCI.")
            self.use_cv = False

        # Dummy sizes — overwritten after SUMO starts
        self._num_lanes  = 8
        self._num_phases = 4

        self._start_sumo()

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

        # CO₂ emission output (scenarios that track emissions)
        if self.scenario is not None:
            os.makedirs("simulation/output", exist_ok=True)
            cmd += ["--emission-output", "simulation/output/emissions.xml"]

        traci.start(cmd)
        self._sumo_running = True
        self._accident_done = False

        # Discover actual traffic-light IDs
        tl_ids = traci.trafficlight.getIDList()
        if not tl_ids:
            raise RuntimeError(
                "No traffic lights in the network. "
                "Re-run generate_network.py with --tls.guess-signals"
            )
        if self.junction_id not in tl_ids:
            self.junction_id = tl_ids[0]
            print(f"[ENV] Using traffic light: {self.junction_id}")

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

        # Initialize CV pipeline if requested
        if self.use_cv:
            self.cv_pipeline = CVPipeline(frame_width=640, frame_height=480)
            # Infer network path from config path
            net_path = self.config_path.replace("config.sumocfg", "mangalore.net.xml")
            self._world_bounds = get_junction_bounds(net_path, self.junction_id)

        # Apply scenario settings
        if self.scenario is not None:
            self._apply_scenario()

    def _apply_scenario(self):
        """Apply speed factor from the scenario to all road edges."""
        sc = self.scenario
        if sc.speed_factor != 1.0:
            for edge_id in traci.edge.getIDList():
                try:
                    orig = traci.edge.getMaxSpeed(edge_id)
                    traci.edge.setMaxSpeed(edge_id, orig * sc.speed_factor)
                except Exception:
                    pass

    def _apply_accident(self):
        """Block the first controlled lane to simulate an accident."""
        if self._controlled_lanes:
            lane = self._controlled_lanes[0]
            try:
                traci.lane.setMaxSpeed(lane, 0.5)          # near-stop
                traci.lane.setDisallowed(lane, ["passenger", "bus"])
                print(f"[ACCIDENT] Lane {lane} closed at step {self.step_count}")
            except Exception:
                pass
        self._accident_done = True

    def _get_obs(self) -> np.ndarray:
        if self.use_cv:
            return self._get_obs_from_cv()
            
        counts, waits = [], []
        for lane in self._controlled_lanes:
            counts.append(traci.lane.getLastStepVehicleNumber(lane) / 20.0)
            waits.append(traci.lane.getWaitingTime(lane) / 300.0)
        obs = np.array(counts + waits, dtype=np.float32)
        return np.clip(obs, 0.0, 1.0)

    def _get_obs_from_cv(self) -> np.ndarray:
        """
        Alternative to _get_obs() — uses internal CV pipeline by rendering
        a synthetic frame from TraCI data.
        """
        # 1. Collect current vehicle positions from TraCI
        vehicles = []
        for vid in traci.vehicle.getIDList():
            x, y = traci.vehicle.getPosition(vid)
            type_id = traci.vehicle.getTypeID(vid)
            vehicles.append({"x": x, "y": y, "type": type_id})

        # 2. Render synthetic top-down frame
        frame = render_topdown_frame(vehicles, self._world_bounds, (640, 480))

        # 3. Process frame through CV pipeline
        counts = self.cv_pipeline.process_frame(frame)

        # 4. Map to observation space (N/S/E/W -> first 4 lanes)
        lanes = list(self._controlled_lanes)
        cv_lanes = ["N", "S", "E", "W"]
        norm_counts = []
        for i in range(len(lanes)):
            cv_key = cv_lanes[i % 4]
            norm_counts.append(counts.get(cv_key, 0) / 20.0)

        # 5. Approximate waiting time (CV doesn't give this directly in one-shot)
        # Using heuristic: queue size * 5 seconds normalized by 300s
        waits = [c * 5.0 / 300.0 for c in norm_counts]
        
        obs = np.array(norm_counts + waits, dtype=np.float32)
        return np.clip(obs, 0.0, 1.0)

    def _get_reward(self) -> float:
        if self.reward_type == "throughput":
            # Reward vehicles reaching destination in the last step
            return float(traci.simulation.getArrivedNumber())
        
        # Default: "wait_time" (minimize waiting time)
        total_wait = sum(
            traci.lane.getWaitingTime(lane)
            for lane in self._controlled_lanes
        )
        return -total_wait / 1000.0

    def _get_co2(self) -> float:
        """Total CO₂ (mg) emitted by all vehicles this step."""
        total = 0.0
        try:
            for vid in traci.vehicle.getIDList():
                total += traci.vehicle.getCO2Emission(vid)
        except Exception:
            pass
        return total  # mg per simulation step

    def _get_junction_positions(self) -> list[tuple]:
        """Return [(lat, lon, tl_id), …] for all traffic lights in the network."""
        positions = []
        try:
            for tl_id in traci.trafficlight.getIDList():
                # Get controlled lanes to find a junction node position
                lanes = traci.trafficlight.getControlledLanes(tl_id)
                if lanes:
                    x, y = traci.lane.getShape(lanes[0])[0]
                    lon, lat = traci.simulation.convertGeo(x, y)
                    positions.append((lat, lon, tl_id))
        except Exception:
            pass
        return positions

    def _get_info(self) -> dict:
        counts = {
            lane: traci.lane.getLastStepVehicleNumber(lane)
            for lane in self._controlled_lanes
        }
        
        # Get vehicle locations for the map overlay
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

        # Get phase name for the action log
        try:
            logic = traci.trafficlight.getAllProgramLogics(self.junction_id)[0]
            phase_idx = traci.trafficlight.getPhase(self.junction_id)
            phase_name = logic.phases[phase_idx].name or f"Phase {phase_idx}"
        except Exception:
            phase_name = f"Phase {traci.trafficlight.getPhase(self.junction_id)}"

        info = {
            "step":           self.step_count,
            "junction_id":    self.junction_id,
            "lane_counts":    counts,
            "current_phase":  traci.trafficlight.getPhase(self.junction_id),
            "phase_name":     phase_name,
            "total_vehicles": traci.simulation.getMinExpectedNumber(),
            "vehicles":       vehicles,
            "co2_mg":         self._get_co2(),
            "scenario":       self.scenario.name if self.scenario else "Normal",
            "accident_active": self._accident_done,
        }
        return info

    # ── Gymnasium API ──────────────────────────────────────────────────────────

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.step_count = 0
        self._start_sumo()
        for _ in range(10):                  # warm-up
            traci.simulationStep()
        return self._get_obs(), self._get_info()

    def step(self, action: int):
        # Trigger accident if configured
        if (self.scenario is not None and
                self.scenario.accident_step is not None and
                self.step_count == self.scenario.accident_step and
                not self._accident_done):
            self._apply_accident()

        traci.trafficlight.setPhase(self.junction_id, int(action))

        for _ in range(5):
            traci.simulationStep()

        self.step_count += 1
        obs     = self._get_obs()
        reward  = self._get_reward()
        info    = self._get_info()

        terminated = (
            self.step_count >= self.max_steps // 5
            or traci.simulation.getMinExpectedNumber() == 0
        )
        return obs, reward, terminated, False, info

    def get_junction_map_data(self) -> list[tuple]:
        """
        Expose all TL positions + current congestion for the map overlay.
        Call this between steps (SUMO must be running).
        Returns list of (lat, lon, tl_id, congestion_label)
        """
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
        except Exception:
            pass
        return result

    def render(self):
        pass   # SUMO-GUI handles rendering when use_gui=True

    def close(self):
        if self._sumo_running:
            traci.close()
            self._sumo_running = False
