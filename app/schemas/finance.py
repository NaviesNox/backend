from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TransactionBase(BaseModel):
    amount: float
    type: str
    description: str
    wallet_id: int
    category_id: Optional[int] = None

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    date: datetime
    class Config:
        orm_mode = True

class WalletBase(BaseModel):
    name: str
    type: str # Cash, Bank, E-Wallet

class WalletCreate(WalletBase):
    pass

class Wallet(WalletBase):
    id: int
    balance: float
    user_id: int
    class Config:
        orm_mode = True

class CategoryBase(BaseModel):
    name: str
    type: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    user_id: int
    class Config:
        orm_mode = True

class BudgetAllocationCreate(BaseModel):
    income: float
    month: int
    year: int
