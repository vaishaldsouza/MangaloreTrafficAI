# src/api/endpoints/simulation.py
import asyncio
import json
import logging
import os
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.api.sim_utils import load_rf, load_lstm, load_rl_model, get_action, congestion_label
from src.controller import SumoTrafficEnv
from src.scenarios import get_scenario
from src.database import SimulationDB

router = APIRouter()
logger = logging.getLogger("simulation")
db = SimulationDB()

# Add at top of file level
active_sims: Dict[str, bool] = {}   # client_id -> should_run

# Model Cache
CACHE = {
    "rf": None,
    "rf_le": None,
    "lstm": None,
    "ppo": None,
    "dqn": None
}

def init_cache():
    CACHE["rf"], CACHE["rf_le"] = load_rf()
    CACHE["lstm"] = load_lstm()
    CACHE["ppo"] = load_rl_model("PPO")
    CACHE["dqn"] = load_rl_model("DQN")

init_cache()

class SimulationManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_json(self, client_id: str, data: Any):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(data)
            except:
                self.disconnect(client_id)

manager = SimulationManager()

from fastapi import WebSocket, WebSocketDisconnect, Query
from src.api.auth import SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, token: str = Query(...)):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        await websocket.close(code=4001)
        return
    await manager.connect(websocket, client_id)
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data.get("type") == "START":
                config = data.get("config", {})
                active_sims[client_id] = True
                asyncio.create_task(run_sim_loop(client_id, config))
            elif data.get("type") == "STOP":
                active_sims[client_id] = False
                
    except WebSocketDisconnect:
        active_sims[client_id] = False
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(client_id)

async def run_sim_loop(client_id: str, config: Dict[str, Any]):
    method = config.get("method", "Fixed-cycle baseline")
    max_steps = config.get("steps", 200)
    scenario_name = config.get("scenario", "Normal")
    backend = config.get("backend", "Python Simulator")
    reward_type = config.get("reward_type", "wait_time")

    logger.info(f"Starting {backend} simulation for {client_id} using {method}")
    
    scenario = get_scenario(scenario_name)
    env = SumoTrafficEnv(
        use_gui=config.get("showGui", False), 
        scenario=scenario, 
        backend=backend,
        reward_type=reward_type,
        max_steps=max_steps * 5,
        use_cv=config.get("use_cv", False),
    )
    
    # Handle multi-junction if applicable
    if config.get("n_junctions", 1) > 1:
        from multi_junction import MultiJunctionTrafficEnv
        env = MultiJunctionTrafficEnv(
            n_junctions=config.get("n_junctions", 1),
            use_gui=config.get("showGui", False),
            max_steps=max_steps * 5
        )
    
    history = []
    lstm_hist = []
    
    try:
        obs, info = env.reset()
        rl_model = CACHE["ppo"] if "PPO" in method else CACHE["dqn"]
        
        for step in range(max_steps):
            if not active_sims.get(client_id, False):
                break
            # 1. Decide action
            action = get_action(
                method=method, 
                obs=obs, 
                action_space_n=env.action_space.n if hasattr(env.action_space, 'n') else 4, 
                step=step,
                rf_clf=CACHE["rf"],
                rf_le=CACHE["rf_le"],
                lstm_model=CACHE["lstm"],
                lstm_hist=lstm_hist,
                rl_model=rl_model
            )
            
            # 2. Step environment
            obs, reward, terminated, truncated, info = env.step(action)
            
            # 3. Update history for LSTM
            hour = (step * 5 // 3600) % 24
            lane_counts = info.get("lane_counts", {})
            lv = list(lane_counts.values())[:4]
            while len(lv) < 4: lv.append(0)
            lstm_hist.append([v / 20.0 for v in lv] + [np.sin(hour * 2 * np.pi / 24), np.cos(hour * 2 * np.pi / 24)])
            
            # 4. Save to history for later DB save
            curr_row = {
                "step": step,
                "reward": float(reward),
                "total_queue": float(info.get("total_queue", 0)),
                "congestion": info.get("congestion", "free"),
                "phase_name": info.get("phase_name", "Fixed"),
                "co2_mg": float(info.get("co2_mg", 0))
            }
            history.append(curr_row)

            # 5. Stream payload
            payload = {
                "type": "STEP",
                **curr_row,
                "vehicles": info.get("vehicles", []),
                "junctions": env.get_junction_map_data() if backend == "SUMO" else []
            }
            
            await manager.send_json(client_id, payload)
            
            # 6. Check for end
            if terminated or truncated:
                break
                
            # Throttle if Python sim (its too fast otherwise)
            if backend == "Python Simulator":
                await asyncio.sleep(0.01)
            else:
                await asyncio.sleep(0.05)
                
        # 7. Save run to database
        try:
            df = pd.DataFrame(history)
            db.save_run(method, df)
        except Exception as e:
            logger.error(f"Failed to save run to DB: {e}")

        await manager.send_json(client_id, {"type": "COMPLETE", "message": "Simulation finished"})
        
    except Exception as e:
        logger.error(f"Simulation loop error: {e}")
        await manager.send_json(client_id, {"type": "ERROR", "message": str(e)})
    finally:
        env.close()
