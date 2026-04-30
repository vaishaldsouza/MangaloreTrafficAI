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

# CORS configuration for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request, HTTPException
from src.api.auth import SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

UNPROTECTED = {"/", "/health", "/auth/login", "/auth/register", "/auth/status", "/auth/forgot-password", "/auth/reset-password", "/api/detect"}

from fastapi.responses import JSONResponse

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.method == "OPTIONS" or request.url.path in UNPROTECTED or request.url.path.startswith("/simulation/ws"):
        return await call_next(request)
    
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"detail": "Missing or invalid token"})
    
    token = auth_header.replace("Bearer ", "")
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return JSONResponse(status_code=401, content={"detail": "Invalid token"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
    
    return await call_next(request)

from src.api.endpoints import admin, simulation, analytics, research, detection

# Include routers
app.include_router(admin.router, prefix="/auth", tags=["Authentication"])
app.include_router(simulation.router, prefix="/simulation", tags=["Simulation"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(research.router, prefix="/research", tags=["Research"])
app.include_router(detection.router, prefix="/api", tags=["Detection"])

@app.get("/")
async def health_check():
    return {"status": "online", "system": "Mangalore Traffic AI"}

@app.get("/health")
def health():
    return {"status": "ok"}
