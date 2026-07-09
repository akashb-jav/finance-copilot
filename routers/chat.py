from fastapi import APIRouter, Depends  # routing and dependency injection
from sqlalchemy.orm import Session  # database session
from database import get_db  # database helper
import models  # table definitions
import os  # to read environment variables
from openai import OpenAI  # Fireworks uses OpenAI compatible API
from dotenv import load_dotenv  # to load .env file
from datetime import datetime  # for current month filter
import sys
print("API KEY:", os.getenv("FIREWORKS_API_KEY"), file=sys.stderr)

load_dotenv()  # load .env file

router = APIRouter()  # create chat router

# Connect to Fireworks AI using OpenAI compatible client
client = OpenAI(
    api_key=os.getenv("FIREWORKS_API_KEY"),  # your Fireworks API key
    base_url="https://api.fireworks.ai/inference/v1"  # Fireworks API endpoint
)

@router.post("/chat")  # POST request to /chat
def chat(data: dict, db: Session = Depends(get_db)):

    user_message = data["message"]  # get user's message
    user_id = data.get("user_id", 1)  # get user id, default 1

    current_month = datetime.utcnow().strftime("%Y-%m")  # current month e.g. "2026-07"

    # Get user's expenses from database
    expenses = db.query(models.Expense).filter(
        models.Expense.user_id == user_id
    ).all()

    # Filter this month's expenses only
    monthly_expenses = [
        e for e in expenses
        if e.date.strftime("%Y-%m") == current_month
    ]

    # Get user's budgets
    budgets = db.query(models.Budget).filter(
        models.Budget.user_id == user_id,
        models.Budget.month == current_month
    ).all()

    # Calculate totals
    total_spent = sum(e.amount for e in monthly_expenses)  # total spent this month
    total_budget = sum(b.amount for b in budgets)  # total budget this month
    remaining = total_budget - total_spent  # remaining balance

    # Build expense summary for AI context
    expense_summary = ""
    for e in monthly_expenses:
        expense_summary += f"- ₹{e.amount} on {e.category} ({e.description}) on {e.date.strftime('%Y-%m-%d')}\n"

    # Build budget summary for AI context
    budget_summary = ""
    for b in budgets:
        budget_summary += f"- {b.category}: ₹{b.amount}\n"

    # System prompt - tells AI who it is and what context it has
    system_prompt = f"""You are an intelligent personal finance assistant for an Indian user. 
You are helpful, friendly, and give practical advice in simple English.
Always use ₹ for currency.

Here is the user's current financial data for {current_month}:

BUDGETS SET:
{budget_summary if budget_summary else "No budgets set yet"}

EXPENSES THIS MONTH:
{expense_summary if expense_summary else "No expenses recorded yet"}

SUMMARY:
- Total Budget: ₹{total_budget}
- Total Spent: ₹{total_spent}
- Remaining: ₹{remaining}

Based on this data, answer the user's questions and give personalized financial advice.
Keep responses concise and helpful. Give specific tips based on their actual spending."""

    # Call Fireworks AI
    response = client.chat.completions.create(
        model="accounts/fireworks/models/llama-v3p3-70b-instruct",  # free model on Fireworks
        messages=[
            {"role": "system", "content": system_prompt},  # AI context and instructions
            {"role": "user", "content": user_message}  # what user asked
        ],
        max_tokens=500  # limit response length
    )

    # Extract AI reply
    ai_reply = response.choices[0].message.content  # get the text response

    return {
        "reply": ai_reply,  # AI's response
        "user_message": user_message,  # echo back user message
        "context": {
            "total_spent": total_spent,  # financial context
            "total_budget": total_budget,
            "remaining": remaining
        }
    }