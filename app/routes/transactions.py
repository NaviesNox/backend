from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.all import Transaction, Wallet, User
from ..schemas.finance import TransactionCreate, Transaction as TransactionSchema
from .wallets import get_current_user

router = APIRouter()

@router.get("/", response_model=List[TransactionSchema])
def get_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Simple query fetching all transactions for wallets owned by this user
    wallets = db.query(Wallet).filter(Wallet.user_id == current_user.id).all()
    wallet_ids = [w.id for w in wallets]
    
    return db.query(Transaction).filter(Transaction.wallet_id.in_(wallet_ids)).all()

@router.post("/", response_model=TransactionSchema)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wallet = db.query(Wallet).filter(Wallet.id == transaction.wallet_id, Wallet.user_id == current_user.id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    db_transaction = Transaction(**transaction.dict())
    db.add(db_transaction)
    
    # Update wallet balance
    if transaction.type == "INCOME":
        wallet.balance += transaction.amount
    elif transaction.type == "EXPENSE":
        wallet.balance -= transaction.amount
        
    db.commit()
    db.refresh(db_transaction)
    return db_transaction
