import asyncio
from app.database import engine, SessionLocal, Base
from app.models.all import User, Wallet, Category
from app.core.security import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # 1. Create a default user
    default_email = "admin@example.com"
    if not db.query(User).filter(User.email == default_email).first():
        hashed_password = get_password_hash("admin123")
        user = User(email=default_email, full_name="Admin", hashed_password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        print("Created default user: admin@example.com / admin123")
    else:
        user = db.query(User).filter(User.email == default_email).first()
        print("Default user already exists.")

    # 2. Add some dummy wallets
    if not db.query(Wallet).filter(Wallet.user_id == user.id).first():
        wallet1 = Wallet(name="My Cash", type="Cash", balance=500000, user_id=user.id)
        wallet2 = Wallet(name="BCA Account", type="Bank", balance=15000000, user_id=user.id)
        db.add_all([wallet1, wallet2])
        db.commit()
        print("Created dummy wallets.")

    # 3. Add default categories
    if not db.query(Category).filter(Category.user_id == user.id).first():
        cat1 = Category(name="Salary", type="INCOME", user_id=user.id)
        cat2 = Category(name="Food", type="EXPENSE", user_id=user.id)
        cat3 = Category(name="Transport", type="EXPENSE", user_id=user.id)
        db.add_all([cat1, cat2, cat3])
        db.commit()
        print("Created dummy categories.")

    db.close()

if __name__ == "__main__":
    seed_data()
