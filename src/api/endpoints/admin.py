# src/api/endpoints/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from src.database import SimulationDB
from src.api.auth import create_access_token, get_current_user

router = APIRouter()
db = SimulationDB()

class UserRegister(BaseModel):
    username: str
    password: str

class ForgotPasswordRequest(BaseModel):
    username: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register")
async def register(user: UserRegister):
    success, message = db.register_admin(user.username, user.password)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not db.authenticate_admin(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def get_me(username: str = Depends(get_current_user)):
    return {"username": username}

@router.get("/status")
async def check_admin_status():
    """Returns True if at least one admin exists in the system."""
    return {"has_admins": db.has_admins()}

@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    """Generates a reset token for the user."""
    # Note: In a real app, check if user exists first to prevent enumeration
    # But for this PBL, we'll keep it simple
    token = db.create_reset_token(req.username)
    # Log the token for dev purposes (since we don't have SMTP)
    print(f"🔑 RESET TOKEN for {req.username}: {token}")
    return {"message": "If that user exists, a reset link has been generated.", "debug_token": token}

@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    """Validates token and updates password."""
    username = db.validate_reset_token(req.token)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    db.reset_password(username, req.new_password)
    return {"message": "Password updated successfully"}
