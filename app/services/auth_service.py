from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Optional
from datetime import timedelta

from app.core.config import settings
from app.core.security import verify_password, create_access_token
from app.models.auth import TokenData
from app.models.user import UserInDB, UserCreate
from app.repositories.user_repository import UserRepository
import logging
from fastapi import Depends

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_user_repository(user_repository: UserRepository = Depends()):
    return user_repository

class AuthService:
    def __init__(self, user_repository: UserRepository = Depends()):
        self.user_repository = user_repository
        logger.info("AuthService initialized")

    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        logger.info(f"Authentication attempt for email: {email}")
        user = await self.user_repository.get_by_email(email)
        if not user:
            logger.warning(f"User not found for email: {email}")
            return None
        if not verify_password(password, user.password):
            logger.warning(f"Invalid password for email: {email}")
            return None
        logger.info(f"User authenticated successfully: {email}")
        return user

    def create_access_token(self, user: UserInDB) -> str:
        token_data = {
            "sub": user.id,
            "email": user.email,
            "role": user.role
        }
        expires_delta = timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
        return create_access_token(token_data, expires_delta)

    async def register_user(self, user_data: UserCreate) -> UserInDB:
        logger.info(f"Registration attempt for email: {user_data.email}")
        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            logger.warning(f"Registration failed: Email already registered: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user_dict = user_data.model_dump()
        user = await self.user_repository.create(user_dict)
        logger.info(f"User registered successfully: {user.email}")
        return user

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> UserInDB:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
            token_data = TokenData(id=user_id, email=payload.get("email"), role=payload.get("role"))
        except JWTError:
            raise credentials_exception
            
        user = await self.user_repository.get_by_id(token_data.id)
        if user is None:
            raise credentials_exception
            
        return user
