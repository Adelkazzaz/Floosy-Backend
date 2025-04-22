from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import UserInDB
from app.models.loan import LoanCreate, LoanResponse, LoansResponse
from app.services.loan_service import LoanService
from app.api.dependencies import get_loan_service, get_current_user

router = APIRouter()

@router.post("", response_model=LoanResponse)
async def apply_for_loan(
    loan_data: LoanCreate,
    current_user: UserInDB = Depends(get_current_user),
    loan_service: LoanService = Depends(get_loan_service)
):
    loan = await loan_service.apply_for_loan(current_user.id, loan_data)
    
    return LoanResponse(
        success=True,
        message="Loan application submitted successfully",
        loan=loan
    )

@router.get("", response_model=dict)
async def get_loans(
    current_user: UserInDB = Depends(get_current_user),
    loan_service: LoanService = Depends(get_loan_service)
):
    loans = await loan_service.get_user_loans(current_user.id)
    
    # Return in the format expected by the frontend
    return {
        "success": True,
        "data": loans
    }
