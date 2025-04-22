from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from uuid import uuid4

class LoanBase(BaseModel):
    amount: float
    term: int  # in months

class LoanCreate(LoanBase):
    pass

class Loan(LoanBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    userId: str
    interestRate: float
    status: Literal["pending", "approved", "rejected", "paid"] = "pending"
    requestDate: datetime = Field(default_factory=datetime.utcnow)
    approvalDate: Optional[datetime] = None
    dueDate: Optional[datetime] = None

class LoanResponse(BaseModel):
    success: bool
    message: str
    loan: Optional[Loan] = None

class LoansResponse(BaseModel):
    loans: list[Loan]
