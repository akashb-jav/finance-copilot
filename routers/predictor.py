from fastapi import APIRouter, Depends  # routing and dependency injection
from sqlalchemy.orm import Session  # database session
from database import get_db  # database helper
import models  # table definitions
from datetime import datetime, timedelta  # for date calculations
import calendar  # to get correct days in a month

router = APIRouter()  # create predictor router

@router.get("/predict/{user_id}")  # GET /predict/1
def get_prediction(user_id: int, db: Session = Depends(get_db)):

    now = datetime.utcnow()  # current date and time
    current_month = now.strftime("%Y-%m")  # e.g. "2026-07"
    today = now.day  # day of month e.g. 6
    days_in_month = calendar.monthrange(now.year, now.month)[1]  # total days in current month e.g. 31
    days_remaining = days_in_month - today  # days left this month

    # Get all budgets for this user this month
    budgets = db.query(models.Budget).filter(
        models.Budget.user_id == user_id,
        models.Budget.month == current_month
    ).all()

    # Get all expenses for this user this month
    all_expenses = db.query(models.Expense).filter(
        models.Expense.user_id == user_id
    ).all()

    # Filter only this month's expenses
    monthly_expenses = [
        e for e in all_expenses
        if e.date.strftime("%Y-%m") == current_month
    ]

    # Total budget and total spent
    total_budget = sum(b.amount for b in budgets)  # total budget this month
    total_spent = sum(e.amount for e in monthly_expenses)  # total spent this month
    remaining = total_budget - total_spent  # remaining balance

    # Daily spending average
    if today > 0 and total_spent > 0:
        daily_average = total_spent / today  # average spent per day so far
    else:
        daily_average = 0  # no data yet

    # Project total spend for full month
    projected_spend = daily_average * days_in_month  # if spending continues at same rate

    # How many days until money runs out
    if daily_average > 0:
        days_until_broke = remaining / daily_average  # remaining money divided by daily spend
    else:
        days_until_broke = days_remaining  # if no spending, money lasts till end of month

    # Generate warnings list
    warnings = []  # empty list to store warnings

    if projected_spend > total_budget:  # if projected spend exceeds budget
        warnings.append(f"At this rate you will overspend by ₹{projected_spend - total_budget:.0f} this month")

    if days_until_broke < days_remaining:  # if money runs out before month ends
        warnings.append(f"You may run out of money in {days_until_broke:.0f} days")

    if total_spent > total_budget * 0.8:  # if already spent 80% of budget
        warnings.append(f"You have used {(total_spent/total_budget*100):.0f}% of your monthly budget")

    # Generate tips based on spending patterns
    tips = []  # empty list to store tips

    # Category wise analysis
    category_analysis = {}  # store per category data

    for b in budgets:
        category = b.category  # get category name
        spent = sum(e.amount for e in monthly_expenses if e.category == category)  # spent in this category
        percent_used = (spent / b.amount * 100) if b.amount > 0 else 0  # percentage of budget used

        category_analysis[category] = {
            "budget": b.amount,  # budget limit
            "spent": spent,  # actual spend
            "remaining": b.amount - spent,  # remaining in category
            "percent_used": round(percent_used, 1),  # percentage used
            "daily_average": round(spent / today, 1) if today > 0 else 0,  # daily average for this category
            "projected": round((spent / today) * days_in_month, 1) if today > 0 else 0  # projected end of month
        }

        # Generate category specific tips
        if percent_used > 80:  # if over 80% used
            tips.append(f"You've used {percent_used:.0f}% of your {category} budget. Try to reduce spending here.")
        elif percent_used < 30 and today > 15:  # if under 30% used after mid month
            tips.append(f"You're well within your {category} budget. Keep it up!")

    # General tips based on overall spending
    if daily_average > 0:
        safe_daily = remaining / days_remaining if days_remaining > 0 else 0  # how much they can spend per day safely
        tips.append(f"To stay within budget, spend max ₹{safe_daily:.0f} per day for the rest of the month")

    if not warnings:  # if no warnings, user is doing well
        tips.append("Great job! You are on track with your budget this month")

    return {
        "user_id": user_id,
        "month": current_month,
        "summary": {
            "total_budget": total_budget,  # total budget
            "total_spent": total_spent,  # total spent
            "remaining": remaining,  # remaining balance
            "daily_average": round(daily_average, 1),  # average daily spend
            "projected_spend": round(projected_spend, 1),  # projected end of month spend
            "days_remaining": days_remaining,  # days left in month
            "days_until_broke": round(days_until_broke, 1)  # days until money runs out
        },
        "warnings": warnings,  # list of warnings
        "tips": tips,  # list of actionable tips
        "category_analysis": category_analysis  # per category breakdown
    }