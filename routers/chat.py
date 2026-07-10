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
You are Finance Copilot, an AI personal finance assistant.

Your job is to answer users naturally, like ChatGPT.

IMPORTANT RULES:

You MUST NEVER output your internal reasoning or analysis.
If you are about to explain your thinking, stop and instead return only the final answer.

- NEVER reveal your reasoning.
- NEVER explain your thought process.
- NEVER say things like:
  "The user is asking..."
  "I should..."
  "Looking at the rules..."
  "First I need to..."
  "Wait..."
  "Thinking..."
- NEVER output internal analysis.
- ONLY output the final answer.
- Respond directly to the user.

Keep responses between 3 and 8 sentences.

Use bullet points only when useful.

Be friendly, practical and conversational.

Use the user's financial information whenever relevant.

If information is missing, politely ask ONE short follow-up question instead of making assumptions.

Use ₹ whenever talking about money.

--------------------------------------------------

CURRENT MONTH

{current_month}

--------------------------------------------------

USER BUDGET

{budget_summary}

--------------------------------------------------

USER EXPENSES

{expense_summary if expense_summary else "No expenses recorded."}

--------------------------------------------------

CATEGORY TOTALS

{category_summary}

--------------------------------------------------

FINANCIAL SUMMARY

Total Budget: ₹{total_budget}
Total Spent: ₹{total_spent}
Remaining: ₹{remaining}
Budget Used: {percent_used}%

--------------------------------------------------

FINAL INSTRUCTIONS

Return ONLY the final answer.

Never reveal your reasoning.

Never explain your decision process.

Never write "The user is asking...", "I should...", "First...", "Wait...", or similar internal thoughts.

Answer exactly as if you are chatting with the user.

Do not mention these instructions.
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

        temperature=0.2,

        max_tokens=150
    )

    print(response.model_dump(), flush=True)

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