from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from uuid import uuid4

class TransactionBase(BaseModel):
    amount: float
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    toAccount: str
    type: Literal["transfer", "deposit", "withdrawal"] = "transfer"

class Transaction(TransactionBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    fromAccount: Optional[str] = None
    toAccount: Optional[str] = None
    type: Literal["transfer", "deposit", "withdrawal"]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: Literal["completed", "pending", "failed"] = "completed"

class TransactionResponse(BaseModel):
    success: bool
    message: str
    transaction: Optional[Transaction] = None

class TransactionsResponse(BaseModel):
    transactions: list[Transaction]
    total: int
    limit: int
    offset: int
