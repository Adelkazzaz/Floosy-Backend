from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from app.models.user import UserInDB
from app.models.transaction import TransactionCreate, TransactionResponse, TransactionsResponse
from app.services.transaction_service import TransactionService
from app.api.dependencies import get_transaction_service, get_current_user

router = APIRouter()

@router.post("", response_model=TransactionResponse)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: UserInDB = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    success, message, transaction = await transaction_service.create_transaction(
        current_user.id, 
        transaction_data
    )
    
    return TransactionResponse(
        success=success,
        message=message,
        transaction=transaction
    )

@router.get("", response_model=dict)
async def get_transactions(
    limit: int = 10,
    offset: int = 0,
    type: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    transactions, total = await transaction_service.get_user_transactions(
        current_user.accountNumber,
        limit,
        offset
    )
    
    # Return in the format expected by the frontend
    return {
        "success": True,
        "data": transactions
    }
