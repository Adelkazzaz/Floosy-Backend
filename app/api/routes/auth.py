from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.models.auth import LoginRequest, LoginResponse, RegisterResponse
from app.models.user import UserCreate, User
from app.services.auth_service import AuthService
from app.api.dependencies import get_auth_service

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        return LoginResponse(
            success=False,
            message="Invalid email or password"
        )
    
    access_token = auth_service.create_access_token(user)
    
    # Convert UserInDB to User (remove password)
    user_response = User(
        id=user.id,
        email=user.email,
        firstName=user.firstName,
        lastName=user.lastName,
        accountNumber=user.accountNumber,
        balance=user.balance,
        createdAt=user.createdAt,
        role=user.role
    )
    
    return LoginResponse(
        success=True,
        message="Login successful",
        token=access_token,
        user=user_response
    )

@router.post("/register", response_model=RegisterResponse)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        user = await auth_service.register_user(user_data)
        
        # Convert UserInDB to User (remove password)
        user_response = User(
            id=user.id,
            email=user.email,
            firstName=user.firstName,
            lastName=user.lastName,
            accountNumber=user.accountNumber,
            balance=user.balance,
            createdAt=user.createdAt,
            role=user.role
        )
        access_token = auth_service.create_access_token(user)
        
        return RegisterResponse(
            success=True,
            message="Registration successful",
            token=access_token,
            user=user_response
        )
    except HTTPException as e:
        return RegisterResponse(
            success=False,
            message=e.detail
        )
    except ValueError as e:
        return RegisterResponse(
            success=False,
            message=str(e)
        )
    except Exception as e:
        auth_service.logger.exception("An unexpected error occurred during registration.")
        return RegisterResponse(
            success=False,
            message="An unexpected error occurred during registration."
        )
