from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.all import Wallet, User
from ..schemas.finance import WalletCreate, Wallet as WalletSchema
from .auth import oauth2_scheme
from ..core.security import SECRET_KEY, ALGORITHM
from jose import jwt

router = APIRouter()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/", response_model=List[WalletSchema])
def get_wallets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Wallet).filter(Wallet.user_id == current_user.id).all()

@router.post("/", response_model=WalletSchema)
def create_wallet(wallet: WalletCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_wallet = Wallet(**wallet.dict(), user_id=current_user.id)
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet

@router.put("/{wallet_id}", response_model=WalletSchema)
def update_wallet(wallet_id: int, wallet: WalletCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_wallet = db.query(Wallet).filter(Wallet.id == wallet_id, Wallet.user_id == current_user.id).first()
    if not db_wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    for key, value in wallet.dict().items():
        setattr(db_wallet, key, value)
    
    db.commit()
    db.refresh(db_wallet)
    return db_wallet

@router.delete("/{wallet_id}")
def delete_wallet(wallet_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_wallet = db.query(Wallet).filter(Wallet.id == wallet_id, Wallet.user_id == current_user.id).first()
    if not db_wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    db.delete(db_wallet)
    db.commit()
    return {"message": "Wallet deleted successfully"}
