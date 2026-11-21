"""Centsyra's budgeting engine. Owned by: Backend / AI teammate.

Public contract used by app.py:
    analyze_budget(income, expenses) -> dict

Money amounts are in Hungarian forints (HUF).
"""

from __future__ import annotations

from typing import Mapping


def _amount(value: float | int, label: str) -> float:
    """Validate numeric, finite, non-negative amounts."""
    import math

    if isinstance(value, bool):
        raise ValueError(f"{label} must be a number, not a true/false value.")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a number.") from exc
    if not math.isfinite(number) or number < 0:
        raise ValueError(f"{label} must be a non-negative, finite amount.")
    return number


def analyze_budget(income: float, expenses: Mapping[str, float]) -> dict:
    """Summarize the user's monthly budget.

    The names of the return keys are shared with the frontend. Do not rename
    them without coordinating with the frontend teammate.
    """
    monthly_income = _amount(income, "Income")
    if not isinstance(expenses, Mapping):
        raise ValueError("Expenses must be a dictionary of category to amount.")

    breakdown: dict[str, float] = {}
    for category, raw_amount in expenses.items():
        if not isinstance(category, str) or not category.strip():
            raise ValueError("Each expense category needs a name.")
        name = category.strip()
        if name in breakdown:
            raise ValueError(f"Duplicate category name: {name}")
        breakdown[name] = _amount(raw_amount, f"Expense for {name}")

    total = round(sum(breakdown.values()), 2)
    remaining = round(monthly_income - total, 2)
    savings_rate = round(remaining / monthly_income * 100, 1) if monthly_income > 0 else 0.0
    expense_ratio = round(total / monthly_income * 100, 1) if monthly_income > 0 else (100.0 if total else 0.0)

    top_category = max(breakdown, key=breakdown.get) if breakdown and total > 0 else None
    return {
        "income": round(monthly_income, 2),
        "total_expenses": total,
        "remaining_balance": remaining,
        "savings_rate": savings_rate,
        "expense_ratio": expense_ratio,
        "category_breakdown": breakdown,
        "largest_expense_category": top_category,
        "overspending": remaining < 0,
    }


def suggest_savings_actions(income: float, expenses: Mapping[str, float], goal: float) -> list[str]:
    """A tiny, transparent 'tool' used by the AI coach to create actionable options."""
    budget = analyze_budget(income, expenses)
    target = _amount(goal, "Savings goal")
    actions: list[str] = []
    balance = budget["remaining_balance"]
    if balance < 0:
        actions.append(f"Expenses exceed income by {abs(balance):,.0f} HUF. First reduce spending or increase income to break even.")
    if budget["largest_expense_category"]:
        largest = budget["largest_expense_category"]
        amount = budget["category_breakdown"][largest]
        if amount > 0:
            actions.append(f"Review {largest}, your largest expense ({amount:,.0f} HUF); even a small reduction may help.")
    if target > max(balance, 0):
        shortfall = target - max(balance, 0)
        actions.append(f"Your savings target exceeds the amount currently left by {shortfall:,.0f} HUF per month.")
    elif target > 0:
        actions.append(f"You can currently meet your {target:,.0f} HUF monthly savings goal if spending stays on plan.")
    if not actions:
        actions.append("Review your expenses each week and set aside a small emergency-fund contribution.")
    return actions
