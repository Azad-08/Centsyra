"""Centsyra Streamlit frontend. Owned by: Frontend / Design teammate.

Keep calls to analyze_budget(income, expenses) and
get_ai_advice(income, expenses, goal) compatible with the backend.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from agent import ai_is_configured, get_ai_advice
from budget import analyze_budget

st.set_page_config(
    page_title="Centsyra | Student Money Companion",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Streamlit styling: app frontend teammate can redesign freely */
    .stApp {background: #080f1b; color: #e9f1f6;}
    [data-testid="stSidebar"] {background: #101e2b; border-right: 1px solid #294151;}
    [data-testid="stSidebar"] * {color: #e7f3f8;}
    h1,h2,h3 {color: #f0faf9; letter-spacing: -0.025em;}
    [data-testid="stMetric"] {background: #132533; border: 1px solid #294251;
        border-radius: 15px; padding: 18px 20px;}
    [data-testid="stMetricLabel"] {color: #a3bcc8;}
    div.stButton > button {background: #42dfb2; color: #08201d; border-radius: 9px;
        font-weight: 700; border: none; width: 100%; min-height: 45px;}
    div.stButton > button:hover {background: #78edca; color: #061915;}
    [data-testid="stAlert"] {border-radius: 13px;}
    .tag {display:inline-block; padding: 6px 12px; background:#163d3c;
          border:1px solid #1d7565; color:#a4f7db; border-radius:99px; font-size:13px;}
    .subtitle {color:#a6bac8; font-size:16px; margin-top:-8px; margin-bottom:24px;}
    .panel {background:#132533; border:1px solid #294251; border-radius:15px;
        padding:20px; margin:12px 0 22px 0;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("# 💠 Centsyra")
st.sidebar.caption("Your student money companion")
st.sidebar.divider()
st.sidebar.subheader("Your monthly budget")

income = st.sidebar.number_input("Monthly income · HUF", min_value=0, max_value=10000000, value=180000, step=5000)

st.sidebar.markdown("**Monthly expenses · HUF**")
DEFAULT_EXPENSES = {
    "Rent": 85000,
    "Groceries": 45000,
    "Transport": 8000,
    "Subscriptions": 5000,
    "Other": 15000,
}
expenses: dict[str, int] = {}
for category, default in DEFAULT_EXPENSES.items():
    expenses[category] = st.sidebar.number_input(
    category,
    min_value=0,
    max_value=1000000,
    value=default,
    step=1000,
    key=f"expense_{category}"
)

# Simple Expense Logger
def add_logged_expense():
    category = st.session_state["log_category"]
    amount = st.session_state["log_amount"]

    if amount > 0:
        st.session_state[f"expense_{category}"] += amount
        st.session_state["log_amount"] = 0


st.sidebar.markdown("### Log an Expense")

with st.sidebar.form("log_expense_form"):
    st.selectbox(
        "Category",
        list(DEFAULT_EXPENSES.keys()),
        key="log_category"
    )

    st.number_input(
        "Amount spent (Ft)",
        min_value=0,
        step=100,
        key="log_amount"
    )

    st.form_submit_button(
        "Add Expense",
        on_click=add_logged_expense
    )

goal = st.sidebar.number_input("Monthly savings goal · HUF", min_value=0, max_value=10000000, value=30000, step=1000)
st.sidebar.caption("Example numbers are editable. No bank connection required.")

st.markdown('<span class="tag">✦ SMART CAMPUS & CITY TECH</span>', unsafe_allow_html=True)
st.title("Take control of your money.")
st.markdown('<p class="subtitle">Clarity for today. Confidence for tomorrow. Made for students in Debrecen.</p>', unsafe_allow_html=True)

budget = analyze_budget(income, expenses)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Monthly income", f"{budget['income']:,.0f} Ft")
col2.metric("Total spending", f"{budget['total_expenses']:,.0f} Ft")
col3.metric("Money remaining", f"{budget['remaining_balance']:,.0f} Ft")
col4.metric("Savings rate", f"{budget['savings_rate']:.1f}%")

if budget["overspending"]:
    st.error("You are currently spending more than your monthly income. Your coach can help you find a starting point.")
elif budget["remaining_balance"] < goal:
    st.warning("You're within budget, but your monthly savings goal needs a little more room.")
else:
    st.success("Great — based on your entries, your current budget can cover your savings goal.")

left, right = st.columns([1.4, 1], gap="large")
with left:
    st.subheader("Where your money goes")
    plot_data = pd.DataFrame(
        {"Category": list(budget["category_breakdown"]),
         "HUF": list(budget["category_breakdown"].values())}
    ).set_index("Category")
    st.bar_chart(plot_data, color="#42dfb2", horizontal=True)
    st.caption("Update any number in the sidebar to see the dashboard recalculate instantly.")

with right:
    st.subheader("Savings goal")
    current_savings = max(budget["remaining_balance"], 0)
    progress = min(current_savings / goal, 1.0) if goal > 0 else 1.0
    st.progress(progress)
    st.metric("Potential monthly savings", f"{current_savings:,.0f} Ft")
    if goal:
        st.caption(f"Goal: {goal:,.0f} Ft/month · {progress*100:.0f}% covered")
    else:
        st.caption("Set a savings goal in the sidebar to track your progress.")
    st.markdown('<div class="panel"><b>💡 Small steps add up.</b><br>Start by reviewing your largest monthly expense, then check spending once a week.</div>', unsafe_allow_html=True)

st.divider()
st.subheader("🧪 What-if Savings Simulator")
st.caption("Try different spending cuts to see how your budget could change. Your real budget inputs stay the same.")

with st.container(border=True):
    st.markdown("**Adjust hypothetical monthly spending**")
    st.caption("Example: Reduce Groceries by 20% to free up 9,000 Ft each month.")
    simulated_expenses = {}
    slider_columns = st.columns(2)
    for index, (category, original_amount) in enumerate(expenses.items()):
        with slider_columns[index % 2]:
            reduction_percent = st.slider(
                f"Reduce {category} by",
                min_value=0,
                max_value=100,
                value=0,
                step=5,
                format="%d%%",
                key=f"whatif_{category}",
            )
        simulated_expenses[category] = round(original_amount * (100 - reduction_percent) / 100, 2)

    scenario = analyze_budget(income, simulated_expenses)
    extra_savings = round(scenario["remaining_balance"] - budget["remaining_balance"], 2)
    goal_shortfall = max(0, goal - scenario["remaining_balance"])

    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric(
        "What-if money remaining",
        f"{scenario['remaining_balance']:,.0f} Ft",
        delta=f"+{extra_savings:,.0f} Ft vs current" if extra_savings else None,
    )
    metric_b.metric("What-if total spending", f"{scenario['total_expenses']:,.0f} Ft")
    metric_c.metric("Gap to savings goal", f"{goal_shortfall:,.0f} Ft")

    if goal <= 0:
        st.info("Set a monthly savings goal in the sidebar to check whether your scenario meets it.")
    elif scenario["remaining_balance"] >= goal:
        st.success(f"Goal reached in this scenario! You could have {scenario['remaining_balance']:,.0f} Ft left per month.")
    else:
        st.warning(f"This scenario is still {goal_shortfall:,.0f} Ft short of your monthly savings goal.")

    st.markdown("**Current spending vs simulated spending**")
    comparison = pd.DataFrame(
        {
            "Current": [expenses[category] for category in expenses],
            "What-if": [simulated_expenses[category] for category in expenses],
        },
        index=list(expenses),
    )
    st.bar_chart(comparison, horizontal=True, color=["#607787", "#42dfb2"])
    st.caption("These numbers are hypothetical, not automatically applied to your budget. All amounts are monthly HUF.")


# Smart Spending Insights
st.subheader("📊 Smart Spending Insights")

total_spending = sum(expenses.values())

if total_spending > 0:
    largest_category = max(expenses, key=expenses.get)
    largest_amount = expenses[largest_category]
    largest_percentage = largest_amount / total_spending * 100

    st.info(
        f"💰 Your largest expense is **{largest_category}**: "
        f"{largest_amount:,.0f} Ft "
        f"({largest_percentage:.1f}% of total spending)."
    )

    st.markdown("### Spending Breakdown")

    sorted_expenses = sorted(
        expenses.items(),
        key=lambda item: item[1],
        reverse=True
    )

    for category, amount in sorted_expenses:
        percentage = amount / total_spending

        st.write(
            f"**{category}** — {amount:,.0f} Ft "
            f"({percentage * 100:.1f}%)"
        )

        st.progress(percentage)

    # Potential Savings Opportunity
    st.markdown("### 💡 Potential Savings Opportunity")

    flexible_expenses = {
        category: amount
        for category, amount in expenses.items()
        if category.lower() in {
            "groceries", "subscriptions", "other", "transport"
        } and amount > 0
    }

    if flexible_expenses:
        category = max(flexible_expenses, key=flexible_expenses.get)
        monthly_saving = flexible_expenses[category] * 0.10
        yearly_saving = monthly_saving * 12

        st.success(
            f"If you reduce **{category}** spending by 10%, "
            f"you could save **{monthly_saving:,.0f} Ft/month** "
            f"or **{yearly_saving:,.0f} Ft/year**."
        )

    st.caption(
        "Illustrative savings scenario, not a guaranteed saving."
    )



st.divider()
st.subheader("✦ Your Centsyra coach")
if ai_is_configured():
    st.caption("Live AI mode · An LLM uses your calculated budget and local savings tools.")
else:
    st.caption("Offline demo mode · Add an OpenAI API key later for AI-generated recommendations.")

if st.button("Analyze my budget ✨", type="primary"):
    with st.spinner("Reviewing your budget and creating next steps..."):
        st.session_state["centsyra_advice"] = get_ai_advice(income, expenses, goal)

if "centsyra_advice" in st.session_state:
    st.markdown(st.session_state["centsyra_advice"])
else:
    st.info("Press **Analyze my budget** to get personalized next steps.")

st.caption("Centsyra is a hackathon prototype, not a banking service or professional financial adviser.")
