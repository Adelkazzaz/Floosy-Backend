from typing import Optional, List
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.user import UserInDB, UserProfileUpdate
from app.core.security import get_password_hash
from app.core.database import get_database
import uuid
from datetime import datetime

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_database)):
        self.db = db
        self.collection = db.users

    async def _get_by_field(self, field: str, value: str) -> Optional[UserInDB]:
        try:
            user = await self.collection.find_one({field: value})
            if user:
                return UserInDB(**user)
            return None
        except Exception as e:
            print(f"Database error: {e}")
            return None

    async def get_by_id(self, user_id: str) -> Optional[UserInDB]:
        return await self._get_by_field("id", user_id)

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        return await self._get_by_field("email", email)

    async def get_by_account_number(self, account_number: str) -> Optional[UserInDB]:
        return await self._get_by_field("accountNumber", account_number)

    async def create(self, user_data: dict) -> UserInDB:
        try:
            # Generate account number
            while True:
                account_number = str(uuid.uuid4().int)[:10]
                existing_user = await self.get_by_account_number(account_number)
                if not existing_user:
                    break

            hashed_password = get_password_hash(user_data["password"])
            user_data.pop("password")

            # Create user object
            user = UserInDB(
                **user_data,
                accountNumber=account_number,
                password=hashed_password
            )
            
            # Insert into database
            user_dict = user.model_dump()
            await self.collection.insert_one(user_dict)
            
            return user
        except Exception as e:
            print(f"Database error: {e}")
            return None

    async def update(self, user_id: str, update_data: UserProfileUpdate) -> Optional[UserInDB]:
        try:
            # Filter out None values
            update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}

            if not update_dict:
                return await self.get_by_id(user_id)

            # Update user
            result = await self.collection.update_one(
                {"id": user_id},
                {"$set": update_dict}
            )

            if result.modified_count > 0:
                return await self.get_by_id(user_id)
            else:
                return None
        except Exception as e:
            print(f"Database error: {e}")
            return None

    async def update_balance(self, user_id: str, new_balance: float) -> Optional[UserInDB]:
        try:
            result = await self.collection.update_one(
                {"id": user_id},
                {"$set": {"balance": new_balance}}
            )
            if result.modified_count > 0:
                return await self.get_by_id(user_id)
            else:
                return None
        except Exception as e:
            print(f"Database error: {e}")
            return None

    async def get_all(self, limit: int = 10, offset: int = 0) -> List[UserInDB]:
        try:
            users = []
            cursor = self.collection.find().skip(offset).limit(limit)
            async for user in cursor:
                users.append(UserInDB(**user))
            return users
        except Exception as e:
            print(f"Database error: {e}")
            return []

    async def count(self) -> int:
        try:
            return await self.collection.count_documents({})
        except Exception as e:
            print(f"Database error: {e}")
            return 0

    async def get_total_users(self) -> int:
        return await self.collection.count_documents({})
        
    async def get_active_users_count(self) -> int:
        """Get count of active users (users who logged in within the last 30 days)"""
        try:
            # This is a placeholder implementation
            # In a real app, you would check for users with recent login activity
            # For example: await self.collection.count_documents({"lastLogin": {"$gte": thirty_days_ago}})
            return int(await self.collection.count_documents({}) * 0.8)  # Assume 80% of users are active
        except Exception as e:
            print(f"Database error: {e}")
            return 0
            
    async def get_users_registered_in_range(self, start_date: datetime, end_date: datetime) -> List[UserInDB]:
        """
        Get users who registered between start_date and end_date
        """
        try:
            query = {
                "createdAt": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            
            users = []
            cursor = self.collection.find(query).sort("createdAt", 1)
            async for user in cursor:
                users.append(UserInDB(**user))
            return users
        except Exception as e:
            print(f"Database error in get_users_registered_in_range: {e}")
            return []
