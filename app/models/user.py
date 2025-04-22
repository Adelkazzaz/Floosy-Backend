from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import uuid4

class UserBase(BaseModel):
    email: EmailStr
    firstName: str
    lastName: str

class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        description="Password must be at least 8 characters long and contain at least one letter, one number, and one special character."
    )
    firstName: str = Field(..., min_length=1, description="First name cannot be empty.")
    lastName: str = Field(..., min_length=1, description="Last name cannot be empty.")

class UserInDB(UserBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    password: str
    accountNumber: str
    balance: float = 0.0
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    role: str = "user"

class User(UserBase):
    id: str
    accountNumber: str
    balance: float
    createdAt: datetime
    role: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    firstName: str
    lastName: str
    accountNumber: str
    balance: float
    createdAt: datetime
    role: str

class UserProfileUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[EmailStr] = None
