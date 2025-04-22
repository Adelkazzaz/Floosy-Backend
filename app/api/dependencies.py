from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.auth_service import AuthService, oauth2_scheme
from app.services.user_service import UserService
from app.services.transaction_service import TransactionService
from app.services.loan_service import LoanService
from app.repositories.user_repository import UserRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.loan_repository import LoanRepository
from app.services.admin_service import AdminService
from app.models.user import UserInDB

from fastapi import Request

async def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.database

async def get_user_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

async def get_transaction_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> TransactionRepository:
    return TransactionRepository(db)

async def get_loan_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> LoanRepository:
    return LoanRepository(db)

async def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> AuthService:
    return AuthService(user_repository)

async def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(user_repository)

async def get_transaction_service(
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
    user_repository: UserRepository = Depends(get_user_repository)
) -> TransactionService:
    return TransactionService(transaction_repository, user_repository)

async def get_loan_service(
    loan_repository: LoanRepository = Depends(get_loan_repository),
    user_repository: UserRepository = Depends(get_user_repository)
) -> LoanService:
    return LoanService(loan_repository, user_repository)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserInDB:
    return await auth_service.get_current_user(token)

async def get_current_admin(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    return current_user

async def get_admin_service(
    user_repository: UserRepository = Depends(get_user_repository),
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
    loan_repository: LoanRepository = Depends(get_loan_repository)
) -> AdminService:
    return AdminService(user_repository, transaction_repository, loan_repository)
