from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import UserInDB, User, UserProfileUpdate
from app.services.user_service import UserService
from app.api.dependencies import get_user_service, get_current_user

router = APIRouter()

@router.get("/profile", response_model=dict)
async def get_user_profile(
    current_user: UserInDB = Depends(get_current_user)
):
    user = User(
        id=current_user.id,
        email=current_user.email,
        firstName=current_user.firstName,
        lastName=current_user.lastName,
        accountNumber=current_user.accountNumber,
        balance=current_user.balance,
        createdAt=current_user.createdAt,
        role=current_user.role
    )
    
    return {
        "success": True,
        "data": user
    }

@router.put("/profile", response_model=dict)
async def update_user_profile(
    update_data: UserProfileUpdate,
    current_user: UserInDB = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    updated_user = await user_service.update_user_profile(current_user.id, update_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update profile. Email may already be in use."
        )
    
    return {
        "success": True,
        "message": "Profile updated successfully",
        "user": {
            "id": updated_user.id,
            "email": updated_user.email,
            "firstName": updated_user.firstName,
            "lastName": updated_user.lastName,
        }
    }
