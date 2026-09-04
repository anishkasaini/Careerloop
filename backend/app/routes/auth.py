from fastapi import APIRouter, HTTPException

from app.schemas.auth import SignupRequest, LoginRequest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter(prefix="/auth", tags=["Auth"])

users = {}


@router.post("/signup")
def signup(data: SignupRequest):

    if data.email in users:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    users[data.email] = {
        "name": data.name,
        "email": data.email,
        "password": hash_password(data.password),
        "role": data.role
    }

    return {
        "message": "User registered successfully",
        "role": data.role
    }


@router.post("/login")
def login(data: LoginRequest):

    user = users.get(data.email)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(data.password, user["password"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token({
        "email": user["email"],
        "role": user["role"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"]
    }