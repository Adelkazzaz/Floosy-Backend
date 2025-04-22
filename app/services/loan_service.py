from typing import List, Optional, Tuple
from datetime import datetime
from app.models.loan import Loan, LoanCreate
from app.repositories.loan_repository import LoanRepository
from app.repositories.user_repository import UserRepository

class LoanService:
    def __init__(
        self, 
        loan_repository: LoanRepository,
        user_repository: UserRepository
    ):
        self.loan_repository = loan_repository
        self.user_repository = user_repository

    async def apply_for_loan(self, user_id: str, loan_data: LoanCreate) -> Loan:
        # Calculate interest rate based on term
        interest_rate = 5 + loan_data.term / 12  # Base rate + term adjustment
        
        # Create loan
        loan = Loan(
            userId=user_id,
            amount=loan_data.amount,
            term=loan_data.term,
            interestRate=interest_rate
        )
        
        return await self.loan_repository.create(loan)

    async def get_user_loans(self, user_id: str) -> List[Loan]:
        return await self.loan_repository.get_by_user(user_id)

    async def approve_loan(self, loan_id: str) -> Tuple[bool, str, Optional[Loan]]:
        # Get loan
        loan = await self.loan_repository.get_by_id(loan_id)
        if not loan:
            return False, "Loan not found", None
            
        if loan.status != "pending":
            return False, f"Loan is already {loan.status}", loan
        
        # Update loan status
        updated_loan = await self.loan_repository.update_status(loan_id, "approved")
        
        # Add loan amount to user's balance
        user = await self.user_repository.get_by_id(loan.userId)
        if user:
            await self.user_repository.update_balance(user.id, user.balance + loan.amount)
        
        return True, "Loan approved successfully", updated_loan

    async def reject_loan(self, loan_id: str) -> Tuple[bool, str, Optional[Loan]]:
        # Get loan
        loan = await self.loan_repository.get_by_id(loan_id)
        if not loan:
            return False, "Loan not found", None
            
        if loan.status != "pending":
            return False, f"Loan is already {loan.status}", loan
        
        # Update loan status
        updated_loan = await self.loan_repository.update_status(loan_id, "rejected")
        
        return True, "Loan rejected successfully", updated_loan

    async def get_all_loans(
        self, 
        limit: int = 10, 
        offset: int = 0, 
        status: Optional[str] = None
    ) -> Tuple[List[dict], int]:
        loans = await self.loan_repository.get_all(limit, offset, status)
        total = await self.loan_repository.count(status)
        
        # Enhance loan data with user account information
        enhanced_loans = []
        for loan in loans:
            loan_dict = loan.dict()
            # Get user information for this loan
            user = await self.user_repository.get_by_id(loan.userId)
            if user:
                loan_dict["accountNumber"] = user.accountNumber
                loan_dict["userName"] = f"{user.firstName} {user.lastName}"
            else:
                loan_dict["accountNumber"] = "Unknown"
                loan_dict["userName"] = "Unknown User"
            
            enhanced_loans.append(loan_dict)
            
        return enhanced_loans, total
