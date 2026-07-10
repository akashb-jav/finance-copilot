from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter()

# Set a budget
@router.post("/budget")
def set_budget(data: dict, db: Session = Depends(get_db)):

    budget = db.query(models.Budget).filter(
        models.Budget.user_id == data["user_id"],
        models.Budget.category == data["category"],
        models.Budget.month == data["month"]
    ).first()

    if budget:
        # Update existing budget
        budget.amount = data["amount"]
        db.commit()
        db.refresh(budget)

        return {
            "message": "Budget updated",
            "budget": {
                "id": budget.id,
                "category": budget.category,
                "amount": budget.amount,
                "month": budget.month
            }
        }

    # Create new budget
    new_budget = models.Budget(
        category=data["category"],
        amount=data["amount"],
        month=data["month"],
        user_id=data["user_id"]
    )

    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)

    return {
        "message": "Budget created",
        "budget": {
            "id": new_budget.id,
            "category": new_budget.category,
            "amount": new_budget.amount,
            "month": new_budget.month
        }
    }

# Get all budgets for a user
@router.get("/budget/{user_id}")
def get_budget(user_id: int, db: Session = Depends(get_db)):
    budgets = db.query(models.Budget).filter(
        models.Budget.user_id == user_id
    ).all()
    return {"budgets": [
        {
            "id": b.id,
            "category": b.category,
            "amount": b.amount,
            "month": b.month
        } for b in budgets
    ]}