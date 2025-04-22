from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import User

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[User] = None

class RegisterResponse(BaseModel):
    success: bool
    message: str
    user: Optional[User] = None
