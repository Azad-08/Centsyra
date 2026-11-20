"""BudgetBuddy: AI tool calling + a no-API demo fallback.

All money calculations happen in budget.py, never inside the model.
"""
import json
import os
import re
from budget import CATEGORIES, get_budget_overview, simulate_purchase, find_budget_pressure, money

TOOLS = [
    {
        "type": "function", "name": "get_budget_overview",
        "description": "Get accurate monthly income, spending, savings, and category balances in HUF.",
        "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
        "strict": True,
    },
    {
        "type": "function", "name": "find_budget_pressure",
        "description": "Identify spending categories over budget and calculate a simple daily guide.",
        "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
        "strict": True,
    },
    {
        "type": "function", "name": "simulate_purchase",
        "description": "Simulate a hypothetical purchase without recording it, using exact HUF arithmetic.",
        "parameters": {
            "type": "object",
            "properties": {
                "amount_huf": {"type": "integer", "description": "Positive integer cost in HUF"},
                "category": {"type": "string", "enum": CATEGORIES},
            },
            "required": ["amount_huf", "category"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]

INSTRUCTIONS = """You are BudgetBuddy, a practical and supportive student-budget planning assistant.
You help students living in Debrecen manage budgets in HUF, without shame or pressure.
Use the provided Python tools for all numeric budget claims. Never invent amounts,
expense records, actual supermarket prices, external data, or bank balances.
Prefer using multiple tools when helpful. Explain numbers simply and concisely.
A hypothetical purchase is NOT automatically recorded. The dashboard shows only
transactions entered into this application. Flag unlogged essential bills,
non-monthly expenses, and uncertainty. Do not claim purchases are guaranteed affordable.
You are not a licensed financial adviser; do not recommend financial products or trades.
Only propose actions; you cannot pay, transfer money, or change records.
Don't ask students to share account numbers, passwords, or card information.
"""


def _execute_tool(name, args, data):
    positional = (data["income"], data["limits"], data["savings_target"], data["transactions"])
    if name == "get_budget_overview":
        return get_budget_overview(*positional)
    if name == "find_budget_pressure":
        return find_budget_pressure(*positional)
    if name == "simulate_purchase":
        return simulate_purchase(int(args["amount_huf"]), args["category"], *positional)
    return {"error": "Unknown tool"}


def demo_answer(question, data):
    """Transparent rules-based demonstration when an API key is unavailable."""
    overview = get_budget_overview(data["income"], data["limits"], data["savings_target"], data["transactions"])
    pressure = find_budget_pressure(data["income"], data["limits"], data["savings_target"], data["transactions"])
    match = re.search(r"([\d][\d., ]*)\s*(?:huf|ft|forints?)\b", question.lower())
    if match and any(word in question.lower() for word in ["buy", "spend", "purchase", "afford", "cost"]):
        amount = int(re.sub(r"\D", "", match.group(1)))
        q = question.lower()
        if any(word in q for word in ["restaurant", "dinner", "lunch", "coffee", "eating", "takeaway"]):
            category = "Eating out"
        elif any(word in q for word in ["grocery", "groceries", "supermarket", "chicken", "rice", "milk"]):
            category = "Groceries"
        elif any(word in q for word in ["bus", "transport", "tram", "ticket"]):
            category = "Transport"
        else:
            category = "Shopping & other"
        try:
            scenario = simulate_purchase(amount, category, data["income"], data["limits"], data["savings_target"], data["transactions"])
            return (
                f"**Offline demo (rules-based, not AI):** A hypothetical {money(amount)} purchase in **{category}** "
                f"would leave **{money(scenario['balance_after_purchase_huf'])}** in total, "
                f"or **{money(scenario['after_reserving_savings_huf'])}** after setting aside your savings goal. "
                f"Your remaining budget for that category would be **{money(scenario['category_remaining_after_huf'])}**. "
                + ("This would exceed your category limit. " if not scenario["within_category_limit"] else "It fits this category's limit. ")
                + "Check unlogged bills before deciding. Nothing has been purchased or recorded."
            ), ["simulate_purchase (offline demo)"]
        except ValueError:
            pass
    alerts = ", ".join(f"{entry['category']} by {money(entry['amount_over_huf'])}" for entry in pressure["overspent_categories"])
    return (
        f"**Offline demo (rules-based, not AI):** You have **{money(overview['balance_remaining_huf'])}** left "
        f"of your {money(overview['monthly_income_huf'])} monthly income. "
        f"After setting aside your {money(overview['savings_target_huf'])} savings goal, "
        f"the planning balance is **{money(overview['balance_after_reserving_savings_huf'])}**. "
        f"Categories over budget: **{alerts or 'none'}**. "
        f"A rough daily guide is **{money(overview['guide_per_day_after_savings_huf'])}** "
        f"for the {overview['remaining_days_including_today']} days left (including today). "
        "This is only a guide: check unlogged bills and planned expenses first. "
        "Add an OpenAI API key to enable real AI tool calling."
    ), ["get_budget_overview (offline demo)", "find_budget_pressure (offline demo)"]


def ask_budgetbuddy(question, data):
    """Return (answer, tool_names, is_ai). No tools change records or move money."""
    if not os.getenv("OPENAI_API_KEY", "").strip():
        answer, calls = demo_answer(question, data)
        return answer, calls, False

    from openai import OpenAI  # only needed when using a real API key
    client = OpenAI()
    tool_log = []
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    messages = [{"role": "user", "content": question}]
    # Stateless request: retain tool calls and tool outputs in the local messages list.
    for _ in range(4):
        response = client.responses.create(
            model=model,
            instructions=INSTRUCTIONS,
            tools=TOOLS,
            input=messages,
            store=False,
        )
        messages.extend(item.model_dump(exclude_none=True) for item in response.output)
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            return response.output_text or "I couldn't generate an answer. Try rephrasing your question.", tool_log, True
        for call in calls:
            try:
                args = json.loads(call.arguments or "{}")
                output = _execute_tool(call.name, args, data)
            except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
                output = {"error": str(exc)}
            tool_log.append(call.name)
            messages.append({"type": "function_call_output", "call_id": call.call_id, "output": json.dumps(output)})
    return "The agent reached its tool-call limit. Try a simpler question.", tool_log, True
