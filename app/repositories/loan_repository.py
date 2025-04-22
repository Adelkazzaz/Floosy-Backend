from typing import Optional, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.loan import Loan

class LoanRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.loans

    async def create(self, loan: Loan) -> Loan:
        loan_dict = loan.model_dump()
        await self.collection.insert_one(loan_dict)
        return loan

    async def get_by_id(self, loan_id: str) -> Optional[Loan]:
        loan = await self.collection.find_one({"id": loan_id})
        if loan:
            return Loan(**loan)
        return None

    async def get_by_user(self, user_id: str) -> List[Loan]:
        loans = await self.collection.find({"userId": user_id}).to_list(length=100)
        return [Loan(**loan) for loan in loans]

    async def update_status(self, loan_id: str, status: str) -> Optional[Loan]:
        update_data = {"status": status}
        
        if status == "approved":
            now = datetime.utcnow()
            update_data["approvalDate"] = now
            
            # Get loan to calculate due date
            loan = await self.get_by_id(loan_id)
            if loan:
                # Calculate due date based on term
                due_date = now + timedelta(days=loan.term * 30)  # Approximate months to days
                update_data["dueDate"] = due_date
        
        await self.collection.update_one(
            {"id": loan_id},
            {"$set": update_data}
        )
        
        return await self.get_by_id(loan_id)

    async def get_all(self, limit: int = 10, offset: int = 0, status: Optional[str] = None) -> List[Loan]:
        query = {}
        if status:
            query["status"] = status
            
        loans = await self.collection.find(query).skip(offset).limit(limit).to_list(length=limit)
        return [Loan(**loan) for loan in loans]

    async def count(self, status: Optional[str] = None) -> int:
        query = {}
        if status:
            query["status"] = status
            
        return await self.collection.count_documents(query)

    async def get_total_loans(self) -> int:
        return await self.collection.count_documents({})
        
    async def get_loans_by_status(self, status: str) -> List[Loan]:
        """Get all loans with a specific status"""
        try:
            loans = await self.collection.find({"status": status}).to_list(length=100)
            return [Loan(**loan) for loan in loans]
        except Exception as e:
            print(f"Database error in get_loans_by_status: {e}")
            return []
            
    async def get_total_loan_amount(self) -> float:
        """Get the total amount of all loans"""
        try:
            pipeline = [
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]
            result = await self.collection.aggregate(pipeline).to_list(length=1)
            if result and len(result) > 0:
                return result[0].get("total", 0)
            return 0
        except Exception as e:
            print(f"Database error in get_total_loan_amount: {e}")
            return 0
            
    async def get_recent_loans(self, limit: int = 10) -> List[Loan]:
        """
        Get most recently created loans
        """
        try:
            loans = await self.collection.find().sort("requestDate", -1).limit(limit).to_list(length=limit)
            return [Loan(**loan) for loan in loans]
        except Exception as e:
            print(f"Database error in get_recent_loans: {e}")
            return []
