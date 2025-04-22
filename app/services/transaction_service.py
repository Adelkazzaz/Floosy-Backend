from typing import List, Optional, Tuple
from app.models.transaction import Transaction, TransactionCreate
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository

class TransactionService:
    def __init__(
        self, 
        transaction_repository: TransactionRepository,
        user_repository: UserRepository
    ):
        self.transaction_repository = transaction_repository
        self.user_repository = user_repository

    async def create_transaction(
        self, 
        user_id: str, 
        transaction_data: TransactionCreate
    ) -> Tuple[bool, str, Optional[Transaction]]:
        # Get sender
        sender = await self.user_repository.get_by_id(user_id)
        if not sender:
            return False, "Sender not found", None
        
        # Check if it's a transfer
        if transaction_data.type == "transfer":
            # Get recipient
            recipient = await self.user_repository.get_by_account_number(transaction_data.toAccount)
            if not recipient:
                return False, "Recipient account not found", None

            if sender.accountNumber == recipient.accountNumber:
                return False, "Cannot transfer to the same account", None
            
            # Check if sender has enough balance
            if sender.balance < transaction_data.amount:
                return False, "Insufficient funds", None
            
            # Create transaction
            transaction = Transaction(
                fromAccount=sender.accountNumber,
                toAccount=recipient.accountNumber,
                amount=transaction_data.amount,
                description=transaction_data.description or "Transfer",
                type="transfer"
            )
            
            # Update balances
            await self.user_repository.update_balance(sender.id, sender.balance - transaction_data.amount)
            await self.user_repository.update_balance(recipient.id, recipient.balance + transaction_data.amount)
        
        # Handle deposit
        elif transaction_data.type == "deposit":
            transaction = Transaction(
                toAccount=sender.accountNumber,
                amount=transaction_data.amount,
                description=transaction_data.description or "Deposit",
                type="deposit"
            )
            
            # Update balance
            await self.user_repository.update_balance(sender.id, sender.balance + transaction_data.amount)
        
        # Handle withdrawal
        elif transaction_data.type == "withdrawal":
            # Check if user has enough balance
            if sender.balance < transaction_data.amount:
                return False, "Insufficient funds", None
                
            transaction = Transaction(
                fromAccount=sender.accountNumber,
                amount=transaction_data.amount,
                description=transaction_data.description or "Withdrawal",
                type="withdrawal"
            )
            
            # Update balance
            await self.user_repository.update_balance(sender.id, sender.balance - transaction_data.amount)
        
        # Save transaction
        saved_transaction = await self.transaction_repository.create(transaction)
        
        return True, "Transaction completed successfully", saved_transaction

    async def get_user_transactions(
        self, 
        account_number: str, 
        limit: int = 10, 
        offset: int = 0
    ) -> Tuple[List[Transaction], int]:
        transactions = await self.transaction_repository.get_by_account(account_number, limit, offset)
        total = await self.transaction_repository.count_by_account(account_number)
        return transactions, total

    async def get_all_transactions(
        self, 
        limit: int = 10, 
        offset: int = 0, 
        type: Optional[str] = None
    ) -> Tuple[List[Transaction], int]:
        transactions = await self.transaction_repository.get_all(limit, offset, type)
        total = await self.transaction_repository.count(type)
        return transactions, total
