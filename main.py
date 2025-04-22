from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

from app.api.routes import auth, users, transactions, loans, admin, admin_stats
from app.core.config import settings
from app.core.database import get_database, connect_to_mongo, close_mongo_connection

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Floosy API",
    lifespan=connect_to_mongo,
    description="API for Floosy Banking Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(loans.router, prefix="/api/loans", tags=["Loans"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(admin_stats.router, prefix="/api", tags=["Admin Stats"])

@app.get("/api/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
