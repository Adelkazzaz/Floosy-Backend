from typing import List, Optional
from app.models.user import UserInDB, UserProfileUpdate
from app.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_user_profile(self, user_id: str) -> Optional[UserInDB]:
        return await self.user_repository.get_by_id(user_id)

    async def update_user_profile(self, user_id: str, update_data: UserProfileUpdate) -> Optional[UserInDB]:
        # Check if email is being updated and if it's already in use
        if update_data.email:
            existing_user = await self.user_repository.get_by_email(update_data.email)
            if existing_user and existing_user.id != user_id:
                return None  # Email already in use by another user
        
        return await self.user_repository.update(user_id, update_data)

    async def get_all_users(self, limit: int = 10, offset: int = 0) -> List[UserInDB]:
        return await self.user_repository.get_all(limit, offset)

    async def count_users(self) -> int:
        return await self.user_repository.count()
