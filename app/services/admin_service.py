from fastapi import Depends
from app.repositories.user_repository import UserRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.loan_repository import LoanRepository
from datetime import datetime, timedelta

class AdminService:
    def __init__(
        self,
        user_repository: UserRepository = Depends(),
        transaction_repository: TransactionRepository = Depends(),
        loan_repository: LoanRepository = Depends()
    ):
        self.user_repository = user_repository
        self.transaction_repository = transaction_repository
        self.loan_repository = loan_repository

    async def get_admin_dashboard_stats(self):
        total_users = await self.user_repository.get_total_users()
        active_users = await self.user_repository.get_active_users_count()
        
        total_transactions = await self.transaction_repository.get_total_transactions()
        transaction_volume = await self.transaction_repository.get_total_volume()
        
        total_loans = await self.loan_repository.get_total_loans()
        pending_loans = await self.loan_repository.get_loans_by_status("pending")
        approved_loans = await self.loan_repository.get_loans_by_status("approved")
        total_loan_amount = await self.loan_repository.get_total_loan_amount()

        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_transactions": total_transactions,
            "transaction_volume": transaction_volume,
            "total_loans": total_loans,
            "pending_loans": len(pending_loans) if pending_loans else 0,
            "approved_loans": len(approved_loans) if approved_loans else 0,
            "total_loan_amount": total_loan_amount,
        }

    async def get_transaction_chart_data(self, days: int = 14):
        """
        Get transaction data grouped by day for the chart
        """
        # Calculate the start date (days ago from now)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get transactions within the date range
        transactions = await self.transaction_repository.get_transactions_in_date_range(start_date, end_date)
        
        # Initialize result array with one entry per day
        result = []
        for i in range(days):
            day = end_date - timedelta(days=days-i-1)
            result.append({
                "date": day.strftime("%Y-%m-%d"),
                "count": 0,
                "volume": 0
            })
            
        # Aggregate transactions by date
        for transaction in transactions:
            transaction_date = transaction.timestamp.strftime("%Y-%m-%d")
            
            # Find the matching day in our result array
            for day_data in result:
                if day_data["date"] == transaction_date:
                    day_data["count"] += 1
                    day_data["volume"] += transaction.amount
                    break
        
        return result
    
    async def get_transaction_distribution(self):
        """
        Get distribution of transactions by type
        """
        transactions = await self.transaction_repository.get_all(limit=1000)  # Using get_all instead of get_all_transactions
        
        # Initialize counters for each type
        types = {
            "deposit": 0,
            "withdrawal": 0,
            "transfer": 0
        }
        
        # Count transactions by type
        for transaction in transactions:
            if transaction.type in types:
                types[transaction.type] += 1
                
        # Format for frontend
        result = []
        for type_name, count in types.items():
            result.append({
                "type": type_name,
                "count": count
            })
            
        return result
    
    async def get_user_growth_data(self, months: int = 12):
        """
        Get user growth data for the given number of months
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30 * months)
        
        # Get users created within this date range, ordered by creation date
        users = await self.user_repository.get_users_registered_in_range(start_date, end_date)
        
        # Group users by month
        result = []
        current_date = start_date
        while current_date <= end_date:
            month_start = datetime(current_date.year, current_date.month, 1)
            
            # Check if we're in the current month
            if month_start.month == end_date.month and month_start.year == end_date.year:
                month_end = end_date
            else:
                # Get the last day of the month
                if month_start.month == 12:
                    month_end = datetime(month_start.year + 1, 1, 1) - timedelta(days=1)
                else:
                    month_end = datetime(month_start.year, month_start.month + 1, 1) - timedelta(days=1)
            
            # Count users registered in this month
            count = 0
            for user in users:
                if month_start <= user.createdAt <= month_end:
                    count += 1
                    
            result.append({
                "date": month_start.strftime("%Y-%m"),
                "count": count
            })
            
            # Move to next month
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)
                
        return result
    
    async def get_loan_status_distribution(self):
        """
        Get distribution of loans by status
        """
        # Get counts for different loan statuses
        pending_loans = await self.loan_repository.get_loans_by_status("pending")
        approved_loans = await self.loan_repository.get_loans_by_status("approved")
        rejected_loans = await self.loan_repository.get_loans_by_status("rejected")
        completed_loans = await self.loan_repository.get_loans_by_status("completed")
        
        # Format for frontend
        result = [
            {"status": "pending", "count": len(pending_loans) if pending_loans else 0},
            {"status": "approved", "count": len(approved_loans) if approved_loans else 0},
            {"status": "rejected", "count": len(rejected_loans) if rejected_loans else 0},
            {"status": "completed", "count": len(completed_loans) if completed_loans else 0}
        ]
        
        return result
    
    async def get_recent_system_activity(self, limit: int = 10):
        """
        Get recent system activity (transactions, loans, etc.)
        """
        # Get recent transactions
        recent_transactions = await self.transaction_repository.get_recent_transactions(limit)
        
        # Get recent loan applications
        recent_loans = await self.loan_repository.get_recent_loans(limit)
        
        # Combine and sort by timestamp
        activities = []
        
        for transaction in recent_transactions:
            # For transactions, use fromAccount as the account identifier
            account_id = transaction.fromAccount if transaction.fromAccount else transaction.toAccount
            
            activities.append({
                "id": str(transaction.id),
                "type": "transaction",
                "description": f"{transaction.type.capitalize()} of {transaction.amount}",
                "amount": transaction.amount,
                "status": transaction.status,
                "timestamp": transaction.timestamp,
                "accountId": account_id,
                "username": "Account " + str(account_id) if account_id else "System"
            })
            
        for loan in recent_loans:
            activities.append({
                "id": str(loan.id),
                "type": "loan",
                "description": f"Loan application for {loan.amount}",
                "amount": loan.amount,
                "status": loan.status,
                "timestamp": loan.requestDate,
                "userId": loan.userId,
                "username": await self._get_user_name(loan.userId)
            })
            
        # Sort by timestamp (newest first) and limit
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:limit]
    
    async def _get_user_name(self, user_id):
        """
        Helper method to get user's full name by ID
        """
        user = await self.user_repository.get_by_id(user_id)
        if user:
            return f"{user.firstName} {user.lastName}"
        return "Unknown User"
