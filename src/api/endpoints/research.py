# src/api/endpoints/research.py
import subprocess
import sys
import os
import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from src.api.auth import get_current_user
from typing import List, Dict, Any

router = APIRouter()
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@router.get("/literature")
async def get_literature_benchmarks():
    """Static lit benchmarks from app.py"""
    return [
        {"Method": "Fixed-cycle (baseline)", "Reduction %": 0.0,  "Source": "— (Our baseline)"},
        {"Method": "Actuated signals",        "Reduction %": 15.0, "Source": "Koonce et al. (2008)"},
        {"Method": "Fuzzy logic control",     "Reduction %": 22.0, "Source": "Trabia et al. (1999)"},
        {"Method": "Random Forest (ML)",      "Reduction %": 18.0, "Source": "Liang et al. (2019)"},
        {"Method": "LSTM predictor",          "Reduction %": 28.0, "Source": "Zhang et al. (2020)"},
        {"Method": "GCN + LSTM (DCRNN)",      "Reduction %": 33.0, "Source": "Li et al. (2018) — DCRNN"},
        {"Method": "DQN (RL)",                "Reduction %": 31.0, "Source": "Wei et al. (2018) — IntelliLight"},
    ]

@router.post("/ablation")
async def run_ablation_study(username: str = Depends(get_current_user)):
    """Runs the RF ablation study logic."""
    try:
        from src.models.random_forest_model import generate_synthetic_data, build_features, label_congestion
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import LabelEncoder
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score
        import pandas as pd
        import numpy as np

        df_syn = generate_synthetic_data(n_hours=100) # Smaller for speed
        df_syn = build_features(df_syn)
        df_syn["label"] = df_syn["vehicle_count"].apply(label_congestion)
        le = LabelEncoder()
        df_syn["y"] = le.fit_transform(df_syn["label"])

        ALL_FEATS = ["hour_sin","hour_cos","is_peak","is_weekend","is_rain","vehicle_count"]
        results = []
        
        # baseline
        X = df_syn[ALL_FEATS].fillna(0)
        y = df_syn["y"]
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=.2, shuffle=False)
        clf = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
        clf.fit(X_tr, y_tr)
        baseline_acc = accuracy_score(y_te, clf.predict(X_te)) * 100
        results.append({"Configuration": "All features", "Accuracy %": round(baseline_acc, 2), "Impact": "0.00%"})

        for drop_feat in ALL_FEATS:
            feats = [f for f in ALL_FEATS if f != drop_feat]
            X = df_syn[feats].fillna(0)
            clf.fit(X_tr[feats], y_tr)
            acc = accuracy_score(y_te, clf.predict(X_te)) * 100
            results.append({
                "Configuration": f"Without {drop_feat}",
                "Accuracy %": round(acc, 2),
                "Impact": f"{acc - baseline_acc:+.2f}%"
            })
            
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/training/ws/{client_id}")
async def training_websocket(websocket: WebSocket, client_id: str):
    await websocket.accept()
    proc = None
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data.get("type") == "START_TRAINING":
                algo = data.get("algo", "PPO")
                timesteps = data.get("timesteps", 10000)
                reward_type = data.get("reward_type", "wait_time")
                
                train_script = os.path.join(ROOT, "src", "train.py")
                curve_path = os.path.join(ROOT, "models", f"{algo.lower()}_learning_curve.csv")
                
                proc = await asyncio.create_subprocess_exec(
                    sys.executable, train_script,
                    "--algo", algo,
                    "--timesteps", str(timesteps),
                    "--reward-type", reward_type,
                    "--curve-path", curve_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                    cwd=ROOT
                )
                
                asyncio.create_task(stream_proc_output(websocket, proc))
                
            elif data.get("type") == "STOP_TRAINING":
                if proc:
                    proc.terminate()
                    await websocket.send_json({"type": "LOG", "message": "Training terminated by user."})
                    
    except WebSocketDisconnect:
        if proc: proc.terminate()
    except Exception as e:
        await websocket.send_json({"type": "ERROR", "message": str(e)})

async def stream_proc_output(websocket, proc):
    import re
    try:
        async for line in proc.stdout:
            decoded_line = line.decode().rstrip()
            payload = {"type": "LOG", "message": decoded_line}
            
            # parse reward
            m = re.search(r"ep_rew_mean\s*\|\s*([-\d.]+)", decoded_line)
            if m:
                payload["reward"] = float(m.group(1))
            
            await websocket.send_json(payload)
            
        return_code = await proc.wait()
        await websocket.send_json({"type": "COMPLETE", "code": return_code})
    except Exception as e:
        await websocket.send_json({"type": "ERROR", "message": str(e)})

@router.post("/optimize")
async def start_optimization(username: str = Depends(get_current_user)):
    """Triggers Optuna study."""
    # Since Optuna is slow, we just return a message that it started 
    # (In a real app, use Celery or a background task)
    cmd = [sys.executable, "-m", "src.optimization"]
    try:
        subprocess.Popen(cmd, cwd=ROOT)
        return {"message": "Optimization study started in background. Results will be saved to logs.db"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
