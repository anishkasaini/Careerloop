from pydantic import BaseModel, EmailStr
from typing import Literal


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Literal["student", "industry", "faculty", "admin"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str