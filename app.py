"""BudgetBuddy AI — Streamlit hackathon MVP.

Launch with: python -m streamlit run app.py
Everything shown is mock data unless the user enters their own transactions.
"""
import csv
from datetime import date
from io import StringIO
from pathlib import Path
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from budget import (
    CATEGORIES, DEFAULT_INCOME, DEFAULT_LIMITS, DEFAULT_SAVINGS_TARGET,
    find_budget_pressure, get_budget_overview, money, seed_transactions, simulate_purchase,
)
from agent import ask_budgetbuddy

load_dotenv(Path(__file__).with_name(".env"))
st.set_page_config(page_title="BudgetBuddy AI", page_icon="💸", layout="wide")

st.markdown("""
<style>
  .block-container {padding-top: 1.7rem; max-width: 1150px;}
  .subtitle {color:#739181;font-size:1rem;margin-top:-8px;margin-bottom:14px;}
  .small-note {font-size:.87rem;color:#738179;}
  .stMetric {border:1px solid #dedede;border-radius:14px;padding:12px;}
</style>
""", unsafe_allow_html=True)

if "income" not in st.session_state:
    st.session_state.income = DEFAULT_INCOME
    st.session_state.savings_target = DEFAULT_SAVINGS_TARGET
    st.session_state.limits = DEFAULT_LIMITS.copy()
    st.session_state.transactions = seed_transactions()
    st.session_state.messages = []


def live_data():
    return {"income": st.session_state.income, "savings_target": st.session_state.savings_target,
            "limits": st.session_state.limits, "transactions": st.session_state.transactions}


st.title("💸 BudgetBuddy AI")
st.markdown('<div class="subtitle">A smarter way for students to stretch their monthly budget.</div>', unsafe_allow_html=True)
st.info("🎓 Hackathon prototype · Fictional starting data · Currency: Hungarian forint (HUF). No bank connections or real purchases.")

overview = get_budget_overview(
    st.session_state.income, st.session_state.limits, st.session_state.savings_target, st.session_state.transactions
)

dashboard, expenses_tab, assistant_tab, simulator_tab, settings_tab = st.tabs(
    ["📊 Dashboard", "🧾 Log expenses", "🤖 Ask BudgetBuddy", "🧮 What-if simulator", "⚙️ Settings"]
)

with dashboard:
    st.subheader("Monthly overview")
    a, b, c, d = st.columns(4)
    a.metric("Monthly income", money(overview["monthly_income_huf"]))
    b.metric("Spent this month", money(overview["spent_this_month_huf"]))
    c.metric("Balance remaining", money(overview["balance_remaining_huf"]))
    d.metric("Savings goal", money(overview["savings_target_huf"]))
    st.caption("After setting aside savings: " + money(overview["balance_after_reserving_savings_huf"]) +
               " · Planning guide per remaining day: " + money(overview["guide_per_day_after_savings_huf"]))
    st.caption("The daily guide is a simple average, not a projection; future unlogged bills are not included.")
    st.subheader("Category spending")
    left, right = st.columns([1.25, 1])
    with left:
        for name, details in overview["categories"].items():
            pct = details["spent_huf"] / max(1, details["limit_huf"])
            st.markdown(f"**{name}** · {money(details['spent_huf'])} / {money(details['limit_huf'])}")
            st.progress(min(1.0, pct))
            if details["over_budget_huf"]:
                st.warning(f"{name} exceeds its category budget by {money(details['over_budget_huf'])}.")
    with right:
        chart_data = pd.DataFrame([
            {"Category": name, "Spent": details["spent_huf"], "Budget": details["limit_huf"]}
            for name, details in overview["categories"].items()
        ]).set_index("Category")
        st.bar_chart(chart_data)
    st.subheader("Recent transactions")
    tx = pd.DataFrame(st.session_state.transactions)
    if not tx.empty:
        st.dataframe(tx.sort_values("date", ascending=False).head(10), use_container_width=True, hide_index=True)

with expenses_tab:
    st.subheader("Add an expense")
    st.write("When you enter a purchase here, it updates every dashboard and AI calculation immediately.")
    with st.form("expense_form", clear_on_submit=True):
        description = st.text_input("What did you buy?", placeholder="Example: Chicken breast")
        amount = st.number_input("Amount (Ft)", min_value=1, max_value=1_000_000, value=1500, step=100)
        category = st.selectbox("Category", CATEGORIES)
        spend_date = st.date_input("Purchase date", value=date.today(), max_value=date.today())
        submitted = st.form_submit_button("Record expense", type="primary")
        if submitted:
            if not description.strip():
                st.error("Please add a short description.")
            else:
                st.session_state.transactions.append({
                    "date": spend_date.isoformat(), "category": category,
                    "amount": int(amount), "description": description.strip()[:80]})
                st.success(f"Recorded {money(amount)} in {category}.")
                st.rerun()

    st.markdown("#### Export your demo transactions")
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=["date", "category", "amount", "description"])
    writer.writeheader()
    writer.writerows(st.session_state.transactions)
    st.download_button("Download CSV", buffer.getvalue(), file_name="budgetbuddy_transactions.csv", mime="text/csv")

with assistant_tab:
    st.subheader("Ask your AI budget planner")
    st.caption("Try: 'Can I spend 7000 Ft on a hoodie?' or 'Where am I over budget and how should I adapt?' ")
    if os.getenv("OPENAI_API_KEY"):
        st.success("AI mode enabled: OpenAI model can choose and call your Python budget tools.")
    else:
        st.warning("Offline demo mode: no API key. Responses below are rules-based, not generated by AI.")
    for item in st.session_state.messages:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
            if item.get("tools"):
                st.caption("Tools used: " + ", ".join(item["tools"]))
    prompt = st.chat_input("Ask a budgeting question...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            with st.spinner("Checking your budget..."):
                answer, used, ai_mode = ask_budgetbuddy(prompt, live_data())
            st.session_state.messages.append({"role": "assistant", "content": answer, "tools": used})
        except Exception:
            st.session_state.messages.append({"role": "assistant", "content":
                "The AI request failed. Check your API key, API billing, internet connection, and model access. "
                "The rest of the app still works without an API key."})
        st.rerun()

with simulator_tab:
    st.subheader("Can I afford this?")
    st.write("Explore a potential purchase without recording or paying for anything.")
    simulated_amount = st.number_input("How much would it cost (Ft)?", min_value=1,
                                       max_value=1_000_000, value=7000, step=500, key="sim_amount")
    simulated_cat = st.selectbox("Which category?", CATEGORIES, index=4, key="sim_cat")
    scenario = simulate_purchase(
        int(simulated_amount), simulated_cat, st.session_state.income, st.session_state.limits,
        st.session_state.savings_target, st.session_state.transactions)
    x, y = st.columns(2)
    x.metric("Balance after purchase", money(scenario["balance_after_purchase_huf"]))
    y.metric("After setting aside savings", money(scenario["after_reserving_savings_huf"]))
    st.metric(f"{simulated_cat} budget remaining after purchase", money(scenario["category_remaining_after_huf"]))
    if scenario["within_category_limit"] and scenario["savings_target_still_covered"]:
        st.success("Fits the selected category limit and leaves room for the savings target.")
    else:
        st.warning("This purchase may conflict with your category budget or savings plan.")
    st.caption(scenario["warning"])

with settings_tab:
    st.subheader("Customize the student's monthly plan")
    with st.form("settings_form"):
        income = st.number_input("Monthly income (Ft)", min_value=0, max_value=5_000_000,
                                 value=int(st.session_state.income), step=1000)
        savings_target = st.number_input("Savings target (Ft)", min_value=0, max_value=5_000_000,
                                         value=int(st.session_state.savings_target), step=1000)
        new_limits = {}
        for category_name in CATEGORIES:
            new_limits[category_name] = st.number_input(
                f"{category_name} monthly budget (Ft)", min_value=1, max_value=5_000_000,
                value=int(st.session_state.limits[category_name]), step=1000,
                key=f"limit_{category_name}")
        if st.form_submit_button("Save monthly plan"):
            st.session_state.income = int(income)
            st.session_state.savings_target = int(savings_target)
            st.session_state.limits = {k: int(v) for k, v in new_limits.items()}
            st.rerun()
    planned = sum(st.session_state.limits.values()) + st.session_state.savings_target
    if planned > st.session_state.income:
        st.warning("Your category limits + savings target exceed your monthly income by " +
                   money(planned - st.session_state.income) + ". Consider revising your plan.")
    else:
        st.info("Unallocated buffer in your plan: " + money(st.session_state.income - planned))
    if st.button("Reset all fictional demo data", type="secondary"):
        for key in ("income", "limits", "savings_target", "transactions", "messages"):
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

st.divider()
st.caption("Educational hackathon MVP · Session-only data (resets when session ends). No bank connection. "
           "Not professional financial advice. Don't enter confidential banking details.")
