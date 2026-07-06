from fastapi import APIRouter, Depends  # APIRouter for routes, Depends for database
from sqlalchemy.orm import Session  # database session type
from database import get_db  # database connection helper
import models  # table definitions

router = APIRouter()  # create router for chat routes

@router.post("/chat")  # POST request to /chat
def chat(data: dict, db: Session = Depends(get_db)):  # data from frontend, db session
    
    user_message = data["message"]  # get the message user typed
    user_id = data.get("user_id", 1)  # get user id, default to 1 for now

    # Get user's expenses from database for context
    expenses = db.query(models.Expense).filter(
        models.Expense.user_id == user_id  # only this user's expenses
    ).all()

    # Get user's budgets from database for context
    budgets = db.query(models.Budget).filter(
        models.Budget.user_id == user_id  # only this user's budgets
    ).all()

    # Calculate total spent
    total_spent = sum(e.amount for e in expenses)  # add up all expenses

    # Calculate total budget
    total_budget = sum(b.amount for b in budgets)  # add up all budgets

    # Dummy reply for now - this will be replaced with Fireworks AI after July 6
    reply = f"You have spent ₹{total_spent} out of your ₹{total_budget} budget. You asked: '{user_message}'. AI integration coming soon!"

    return {
        "reply": reply,  # send reply back to frontend
        "user_message": user_message,  # echo back what user said
        "context": {
            "total_spent": total_spent,  # give frontend the context too
            "total_budget": total_budget  # so it can display it
        }
    }