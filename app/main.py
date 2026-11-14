from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from .database import engine, Base
from .models.all import User, Wallet, Category, Transaction, Budget, FinancialGoal, Notification
from .routes import auth, wallets, transactions, categories, budgets

# Create tables (simpler than Alembic for demonstration, but you can swap to Alembic later)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Failed to create tables: {e}")

app = FastAPI(
    title="ManageKeuangan SuperApp API",
    description="Backend API for Financial Management System",
    version="1.0.0"
)

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(wallets.router, prefix="/wallets", tags=["Wallets"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(budgets.router, prefix="/budgets", tags=["Budgets"])

@app.get("/")
def read_root():
    return {"message": "Welcome to ManageKeuangan SuperApp API"}
