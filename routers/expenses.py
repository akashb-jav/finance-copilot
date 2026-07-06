from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter()

# Add a new expense
@router.post("/expenses")
def add_expense(data: dict, db: Session = Depends(get_db)):
    new_expense = models.Expense(
        amount=data["amount"],
        category=data["category"],
        description=data.get("description", ""),
        user_id=data["user_id"]
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return {"message": "Expense added", "expense": {
        "id": new_expense.id,
        "amount": new_expense.amount,
        "category": new_expense.category,
        "description": new_expense.description,
        "date": new_expense.date
    }}

# Get all expenses for a user
@router.get("/expenses/{user_id}")
def get_expenses(user_id: int, db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).filter(
        models.Expense.user_id == user_id
    ).all()
    return {"expenses": [
        {
            "id": e.id,
            "amount": e.amount,
            "category": e.category,
            "description": e.description,
            "date": e.date
        } for e in expenses
    ]}