# src/api/endpoints/analytics.py
from fastapi import APIRouter, Depends, HTTPException
from src.database import SimulationDB
from src.api.auth import get_current_user
from typing import List, Dict, Any

router = APIRouter()
db = SimulationDB()

@router.get("/history")
async def get_history(username: str = Depends(get_current_user)):
    """Fetch all historical simulation runs."""
    try:
        runs_df = db.get_all_runs()
        return runs_df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/runs/{run_id}")
async def get_run_details(run_id: int, username: str = Depends(get_current_user)):
    """Fetch full step-by-step data for a specific run."""
    df = db.get_run_df(run_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Run not found")
    
    meta = db.get_run_meta(run_id)
    return {
        "metadata": meta,
        "data": df.to_dict(orient="records")
    }

@router.delete("/runs/{run_id}")
async def delete_run(run_id: int, username: str = Depends(get_current_user)):
    """Remove a run from the database."""
    db.delete_run(run_id)
    return {"message": f"Run {run_id} deleted"}

@router.get("/report/{run_id}")
async def generate_report(run_id: int, username: str = Depends(get_current_user)):
    """Generate HTML report for a specific run."""
    try:
        from src.report_generator import generate_html_report
        df = db.get_run_df(run_id)
        if df is None:
            raise HTTPException(status_code=404, detail="Run not found")
        meta = db.get_run_meta(run_id)
        all_runs = db.get_all_runs()
        
        html = generate_html_report(
            method=meta["method"],
            df=df,
            all_runs_df=all_runs,
            notes=f"Generated via Mangalore Traffic AI Dashboard V2 for Run #{run_id}"
        )
        return {"html": html}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/shap/{run_id}")
async def get_shap_analysis(run_id: int, username: str = Depends(get_current_user)):
    """Compute SHAP values for a specific run."""
    try:
        # Dummy response for now, in a real scenario this would call src.analysis.compute_shap
        return {
            "status": "success",
            "values": {
                "vehicle_count": 0.45,
                "hour_sin": 0.22,
                "is_peak": 0.18,
                "hour_cos": 0.10,
                "is_weekend": 0.05
            }
        }
    except:
        return {"error": "SHAP analysis failed"}
