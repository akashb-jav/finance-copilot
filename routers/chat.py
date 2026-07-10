from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models
import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import sys

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

print("API KEY:", os.getenv("FIREWORKS_API_KEY"), file=sys.stderr)

router = APIRouter()


@router.post("/chat")
def chat(data: dict, db: Session = Depends(get_db)):

    client = OpenAI(
        api_key=os.getenv("FIREWORKS_API_KEY"),
        base_url="https://api.fireworks.ai/inference/v1"
    )

    user_message = data.get("message", "")
    print("USER MESSAGE:", user_message, flush=True)
    user_id = data.get("user_id", 1)

    current_month = datetime.utcnow().strftime("%Y-%m")

    expenses = db.query(models.Expense).filter(
        models.Expense.user_id == user_id
    ).all()

    monthly_expenses = [
        e for e in expenses
        if e.date.strftime("%Y-%m") == current_month
    ]

    budgets = db.query(models.Budget).filter(
        models.Budget.user_id == user_id,
        models.Budget.month == current_month
    ).all()

    total_spent = sum(e.amount for e in monthly_expenses)
    total_budget = sum(b.amount for b in budgets)
    remaining = total_budget - total_spent

    # ----------------------------
    # Expense Summary
    # ----------------------------

    expense_summary = ""

    category_totals = {}

    for e in monthly_expenses:

        expense_summary += (
            f"• {e.category}: ₹{e.amount} "
            f"({e.description}) on "
            f"{e.date.strftime('%d %b %Y')}\n"
        )

        category_totals[e.category] = (
            category_totals.get(e.category, 0) + e.amount
        )

    category_summary = ""

    if category_totals:

        for category, amount in category_totals.items():
            category_summary += f"• {category}: ₹{amount}\n"

    else:

        category_summary = "No category spending yet."

    # ----------------------------
    # Budget Summary
    # ----------------------------

    budget_summary = ""

    if budgets:

        for b in budgets:

            budget_summary += (
                f"• {b.category}: ₹{b.amount}\n"
            )

    else:

        budget_summary = "No budgets have been set."

    # ----------------------------
    # Spending Percentage
    # ----------------------------

    if total_budget > 0:

        percent_used = round(
            (total_spent / total_budget) * 100,
            1
        )

    else:

        percent_used = 0

    # ----------------------------
    # AI Prompt
    # ----------------------------

    system_prompt = f"""
You are Finance Copilot.

You are an intelligent AI financial advisor similar to ChatGPT.

Your personality:

- Friendly
- Professional
- Encouraging
- Natural
- Easy to understand
- Never robotic

You help users with:

• Budgeting
• Saving money
• Monthly planning
• Spending analysis
• Expense tracking
• Shopping decisions
• Price comparisons
• Student budgeting
• Financial education
• Investment basics
• Emergency funds
• Credit cards
• Loans
• Insurance
• Subscription management
• Financial goal planning

You are NOT limited to the user's database.

If the user asks general finance questions,
answer using your financial knowledge.

If the user asks about their own money,
use the information below.

----------------------------------------

CURRENT MONTH

{current_month}

----------------------------------------

USER BUDGETS

{budget_summary}

----------------------------------------

USER EXPENSES

{expense_summary if expense_summary else "No expenses recorded."}

----------------------------------------

CATEGORY TOTALS

{category_summary}

----------------------------------------

FINANCIAL SUMMARY

Total Budget:
₹{total_budget}

Total Spent:
₹{total_spent}

Remaining:
₹{remaining}

Budget Used:
{percent_used}%

----------------------------------------

Rules

1. Always answer naturally like ChatGPT.

2. Never say
"I only answer finance questions."

3. If information is missing,
tell the user what additional information would help.

4. Always explain WHY.

5. Give practical advice.

6. Encourage better financial habits.

7. If someone asks
"Should I buy this?"
consider their remaining budget.

8. If someone asks
"Can I afford this?"
calculate it.

9. If someone asks about investing,
explain beginner concepts clearly.

10. Keep answers informative but conversational.

11. Use ₹ whenever discussing money.

12. If the user is already managing money well,
compliment them briefly and explain why.

13. If the user is overspending,
suggest realistic improvements instead of criticizing them.

14. Whenever possible,
end with one useful financial tip.
"""

    response = client.chat.completions.create(

        # KEEP THE MODEL THAT ALREADY WORKS FOR YOU
        model="accounts/fireworks/models/kimi-k2p6",

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ],

        temperature=0.7,

        max_tokens=900
    )

    ai_reply = response.choices[0].message.content

    return {

        "reply": ai_reply,

        "user_message": user_message,

        "context": {

            "total_budget": total_budget,

            "total_spent": total_spent,

            "remaining": remaining,

            "budget_used": percent_used
        }
    }