"""Transparent, deterministic HUF arithmetic for the BudgetBuddy hackathon demo.

This file does not use AI. The model asks these Python tools for numbers.
"""
from collections import defaultdict
from datetime import date
import calendar

CATEGORIES = ["Rent & bills", "Groceries", "Transport", "Eating out", "Shopping & other"]
DEFAULT_LIMITS = {
    "Rent & bills": 42000,
    "Groceries": 18000,
    "Transport": 8000,
    "Eating out": 5000,
    "Shopping & other": 5000,
}
DEFAULT_INCOME = 95000
DEFAULT_SAVINGS_TARGET = 8000


def seed_transactions():
    """Entirely fictional transactions, dated in the current calendar month."""
    month = date.today()
    examples = [
        (1, "Rent & bills", 42000, "Rent and utilities"),
        (3, "Groceries", 5600, "Weekly groceries"),
        (6, "Transport", 3100, "Bus pass / tickets"),
        (9, "Groceries", 4200, "Food shopping"),
        (12, "Eating out", 1900, "Lunch out"),
        (15, "Shopping & other", 1200, "Toiletries"),
        (17, "Groceries", 2850, "Groceries top-up"),
        (18, "Eating out", 3800, "Dinner out"),
    ]
    return [
        {"date": date(month.year, month.month, min(day, month.day)).isoformat(),
         "category": category, "amount": amount, "description": description}
        for day, category, amount, description in examples
    ]


def money(amount):
    return f"{int(amount):,} Ft"


def current_month_transactions(transactions, today=None):
    today = today or date.today()
    prefix = today.strftime("%Y-%m")
    return [t for t in transactions if str(t["date"]).startswith(prefix)]


def get_budget_overview(income, limits, savings_target, transactions, today=None):
    """Return exact numbers. Do NOT ask an LLM to calculate balances."""
    today = today or date.today()
    monthly = current_month_transactions(transactions, today)
    spent = sum(int(t["amount"]) for t in monthly)
    remaining = int(income) - spent
    protected = remaining - int(savings_target)
    days_left = calendar.monthrange(today.year, today.month)[1] - today.day + 1
    by_category = defaultdict(int)
    for transaction in monthly:
        by_category[transaction["category"]] += int(transaction["amount"])
    categories = {
        name: {
            "limit_huf": int(limits[name]),
            "spent_huf": by_category[name],
            "remaining_huf": int(limits[name]) - by_category[name],
            "over_budget_huf": max(0, by_category[name] - int(limits[name])),
        }
        for name in CATEGORIES
    }
    return {
        "currency": "HUF",
        "period": today.strftime("%Y-%m"),
        "monthly_income_huf": int(income),
        "spent_this_month_huf": spent,
        "balance_remaining_huf": remaining,
        "savings_target_huf": int(savings_target),
        "balance_after_reserving_savings_huf": protected,
        "remaining_days_including_today": days_left,
        "guide_per_day_after_savings_huf": max(0, protected) // max(1, days_left),
        "categories": categories,
    }


def simulate_purchase(amount, category, income, limits, savings_target, transactions, today=None):
    if category not in CATEGORIES:
        raise ValueError(f"Unknown category: {category}")
    if isinstance(amount, bool) or not isinstance(amount, int) or not 0 < amount <= 1_000_000:
        raise ValueError("Purchase amount must be an integer from 1 to 1,000,000 Ft")
    overview = get_budget_overview(income, limits, savings_target, transactions, today)
    category_info = overview["categories"][category]
    return {
        "hypothetical_only": True,
        "category": category,
        "purchase_huf": amount,
        "balance_after_purchase_huf": overview["balance_remaining_huf"] - amount,
        "after_reserving_savings_huf": overview["balance_after_reserving_savings_huf"] - amount,
        "category_remaining_after_huf": category_info["remaining_huf"] - amount,
        "within_category_limit": category_info["remaining_huf"] >= amount,
        "within_total_remaining_balance": overview["balance_remaining_huf"] >= amount,
        "savings_target_still_covered": overview["balance_after_reserving_savings_huf"] >= amount,
        "warning": "This ignores future unlogged bills and expenses; it is not a guarantee of affordability.",
    }


def find_budget_pressure(income, limits, savings_target, transactions, today=None):
    overview = get_budget_overview(income, limits, savings_target, transactions, today)
    over = [
        {"category": name, "amount_over_huf": info["over_budget_huf"]}
        for name, info in overview["categories"].items()
        if info["over_budget_huf"] > 0
    ]
    over.sort(key=lambda item: item["amount_over_huf"], reverse=True)
    return {
        "overspent_categories": over,
        "safe_spendable_after_savings_huf": overview["balance_after_reserving_savings_huf"],
        "days_left": overview["remaining_days_including_today"],
        "simple_daily_guide_huf": overview["guide_per_day_after_savings_huf"],
        "notes": [
            "The daily guide is an average of remaining funds, not a forecast.",
            "Check for bills and essential expenses not yet logged before spending.",
            "A category being under budget does not guarantee future bills are covered.",
        ],
    }
