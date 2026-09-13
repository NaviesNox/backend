from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..database import get_db
from ..models.all import Budget, Category, User
from ..schemas.finance import BudgetAllocationCreate
from .wallets import get_current_user

router = APIRouter()

@router.post("/allocate")
def allocate_monthly_budget(data: BudgetAllocationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Calculate sizes
    needs_amt = data.income * 0.5
    wants_amt = data.income * 0.3
    invest_amt = data.income * 0.2
    
    # Define exact category names
    cat_names = {
        "Kebutuhan Pokok (50%)": needs_amt,
        "Hobi & Keinginan (30%)": wants_amt,
        "Investasi & Tabungan (20%)": invest_amt
    }
    
    for name, amount in cat_names.items():
        # Find or create category
        category = db.query(Category).filter(Category.name == name, Category.user_id == current_user.id).first()
        if not category:
            category = Category(name=name, type="BUDGET_GROUP", user_id=current_user.id)
            db.add(category)
            db.commit()
            db.refresh(category)
        
        # Find or create budget for month/year
        budget = db.query(Budget).filter(Budget.category_id == category.id, Budget.month == data.month, Budget.year == data.year, Budget.user_id == current_user.id).first()
        if budget:
            budget.amount = amount
        else:
            budget = Budget(amount=amount, month=data.month, year=data.year, category_id=category.id, user_id=current_user.id)
            db.add(budget)
        
    db.commit()
    return {"message": "Budget allocated successfully", "month": data.month, "year": data.year, "total_income": data.income}

@router.get("/history", response_model=List[Dict[str, Any]])
def get_budget_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Fetch all budgets and their corresponding category names
    budgets = db.query(Budget, Category.name).join(Category).filter(Budget.user_id == current_user.id).all()
    
    history = {}
    for b, cat_name in budgets:
        key = f"{b.year}-{b.month:02d}"
        if key not in history:
            history[key] = {
                "id": key,
                "year": b.year, 
                "month": b.month, 
                "needs": 0, 
                "wants": 0, 
                "investments": 0, 
                "total": 0
            }
        
        history[key]["total"] += b.amount
        
        if "Kebutuhan" in cat_name:
            history[key]["needs"] = b.amount
        elif "Hobi" in cat_name:
            history[key]["wants"] = b.amount
        elif "Investasi" in cat_name:
            history[key]["investments"] = b.amount
            
    # Convert to list and sort descending by year and month
    result = list(history.values())
    result.sort(key=lambda x: (x["year"], x["month"]), reverse=True)
    
    return result
