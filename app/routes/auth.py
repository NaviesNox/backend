from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ..database import get_db
from ..models.all import User, Wallet, Category
from ..schemas.user import UserCreate, User as UserSchema, Token
from ..core.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from ..core.security import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, full_name=user.full_name, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create default wallet for new user
    default_wallet = Wallet(name="My Wallet", type="Cash", balance=0, user_id=db_user.id)
    db.add(default_wallet)
    
    # Create default categories for new user
    cat1 = Category(name="Gaji", type="INCOME", user_id=db_user.id)
    cat2 = Category(name="Makanan", type="EXPENSE", user_id=db_user.id)
    cat3 = Category(name="Transport", type="EXPENSE", user_id=db_user.id)
    cat4 = Category(name="Hiburan", type="EXPENSE", user_id=db_user.id)
    db.add_all([cat1, cat2, cat3, cat4])
    
    db.commit()
    return db_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
