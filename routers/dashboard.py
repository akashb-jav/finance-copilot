from fastapi import APIRouter, Depends  # APIRouter to create routes, Depends for database injection
from sqlalchemy.orm import Session  # Session type for database operations
from database import get_db  # our database connection helper
import models  # our table definitions
from datetime import datetime  # to get current month

router = APIRouter()  # create router for dashboard routes

@router.get("/dashboard/{user_id}")  # GET request to /dashboard/1 for user with id 1
def get_dashboard(user_id: int, db: Session = Depends(get_db)):  # user_id from URL, db from FastAPI
    
    current_month = datetime.utcnow().strftime("%Y-%m")  # get current month e.g. "2026-07"

    # Get all budgets for this user for current month
    budgets = db.query(models.Budget).filter(
        models.Budget.user_id == user_id,  # only this user's budgets
        models.Budget.month == current_month  # only this month's budgets
    ).all()

    # Get all expenses for this user for current month
    all_expenses = db.query(models.Expense).filter(
        models.Expense.user_id == user_id  # only this user's expenses
    ).all()

    # Filter expenses for current month only
    monthly_expenses = [
        e for e in all_expenses  # loop through all expenses
        if e.date.strftime("%Y-%m") == current_month  # keep only this month's expenses
    ]

    # Calculate total budget across all categories
    total_budget = sum(b.amount for b in budgets)  # add up all budget amounts

    # Calculate total spent across all expenses this month
    total_spent = sum(e.amount for e in monthly_expenses)  # add up all expense amounts

    # Calculate remaining balance
    remaining = total_budget - total_spent  # simple subtraction

    # Build category breakdown
    category_summary = {}  # empty dictionary to store per-category data

    for b in budgets:  # loop through each budget category
        category = b.category  # get category name e.g. "food"
        
        # Calculate how much was spent in this category
        spent_in_category = sum(
            e.amount for e in monthly_expenses  # add expense amounts
            if e.category == category  # only if category matches
        )
        
        category_summary[category] = {
            "budget": b.amount,  # how much they planned to spend
            "spent": spent_in_category,  # how much they actually spent
            "remaining": b.amount - spent_in_category,  # how much left in this category
            "warning": spent_in_category > b.amount * 0.8  # True if spent more than 80% of budget
        }

    # Smart prediction - how many days until they run out of money
    today = datetime.utcnow().day  # what day of the month is today e.g. 6
    days_passed = today  # number of days passed this month
    days_in_month = 31  # approximate days in a month
    days_remaining = days_in_month - days_passed  # days left this month

    if days_passed > 0 and total_spent > 0:  # avoid division by zero
        daily_spending = total_spent / days_passed  # average spending per day
        projected_total = daily_spending * days_in_month  # projected spend for full month
        prediction = f"At this rate you will spend ₹{projected_total:.0f} this month"  # prediction message
        
        if projected_total > total_budget:  # if projected spend exceeds budget
            days_until_broke = remaining / daily_spending  # how many days until money runs out
            prediction = f"Warning! At this rate you will run out of money in {days_until_broke:.0f} days"
    else:
        prediction = "No expenses recorded yet this month"  # no data yet

    return {
        "user_id": user_id,  # which user this is for
        "month": current_month,  # current month
        "total_budget": total_budget,  # total budget set
        "total_spent": total_spent,  # total spent so far
        "remaining": remaining,  # remaining balance
        "prediction": prediction,  # smart prediction message
        "categories": category_summary  # breakdown by category
    }