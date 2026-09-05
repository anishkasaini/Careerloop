from fastapi import APIRouter, HTTPException

from app.schemas.auth import SignupRequest, LoginRequest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

from app.supabase_client import supabase


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup")
def signup(data: SignupRequest):

    # Check if user already exists
    existing_user = (
        supabase
        .table("users")
        .select("*")
        .eq("email", data.email)
        .execute()
    )

    if existing_user.data:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(data.password)

    # Insert user into Supabase
    new_user = (
        supabase
        .table("users")
        .insert({
            "name": data.name,
            "email": data.email,
            "password": hashed_password,
            "role": data.role
        })
        .execute()
    )

    return {
        "message": "User registered successfully",
        "role": data.role
    }


@router.post("/login")
def login(data: LoginRequest):

    # Find user
    result = (
        supabase
        .table("users")
        .select("*")
        .eq("email", data.email)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    user = result.data[0]

    # Verify password
    if not verify_password(
        data.password,
        user["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create JWT
    token = create_access_token({
        "email": user["email"],
        "role": user["role"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"]
    }