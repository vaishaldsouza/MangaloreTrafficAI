# src/api/main.py
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure the root project directory is in the path for importing src modules
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

app = FastAPI(
    title="Mangalore Traffic AI API",
    description="Backend API for the Next.js Traffic Dashboard",
    version="2.0.0"
)

# CORS configuration for Next.js (usually runs on port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.api.endpoints import admin, simulation, analytics, research

# Include routers
app.include_router(admin.router, prefix="/auth", tags=["Authentication"])
app.include_router(simulation.router, prefix="/simulation", tags=["Simulation"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(research.router, prefix="/research", tags=["Research"])

@app.get("/")
async def health_check():
    return {"status": "online", "system": "Mangalore Traffic AI"}
