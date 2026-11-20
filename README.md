# 💸 BudgetBuddy AI — Beginner Hackathon Starter

An educational Smart Campus student budgeting application for Debrecen.

### What works now
- Fictional HUF income, expenses and category budgets
- Dashboard with spending totals, limits and charts
- Record an expense and see the dashboard update
- What-if simulator (read-only, no transactions created)
- AI chat that can use 3 Python tools: `get_budget_overview`, `find_budget_pressure`, `simulate_purchase`
- Clearly labeled rules-based offline demo when no API key is provided
- Customize income, category limits, savings goal; export transactions as CSV
- Four unit tests of the math

### Run on Windows (VS Code terminal)
1. Install Python 3.11 or newer.
2. Open this folder in VS Code.
3. Run these commands **one at a time** in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL shown by Streamlit (normally `http://localhost:8501`).

No Python activation required! Mac/Linux versions:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

### Turn on real AI tool calling (optional)

1. Obtain an OpenAI API key with API billing access.
2. Make a copy of `.env.example` and name it `.env`.
3. Add `OPENAI_API_KEY=YOUR_KEY_HERE`. Leave `OPENAI_MODEL=gpt-4.1-mini` or select a model accessible to your project.
4. Restart Streamlit.

**Never push `.env` to GitHub.** An API key is not included in this ZIP.
The ChatGPT subscription is separate from API billing.
Do not share real banking logins, card numbers, or other sensitive credentials.

### Test the budget logic
```powershell
.\.venv\Scripts\python.exe -m unittest test_budget.py
```

### How the project works

- `app.py`: website UI (Streamlit), inputs, tabs, charts, session state
- `budget.py`: accurate Python calculations and fake sample data
- `agent.py`: optional OpenAI API function/tool calling; offline fallback
- `test_budget.py`: unit tests
- `.env.example`: optional AI configuration template
- `requirements.txt`: Python dependencies

The model **requests** a tool, Python runs it, returns the structured result, and the model explains it. Nothing here connects to a bank, moves money or buys products. Simulations never change records. Settings and transactions last for the current Streamlit session only; refreshing or restarting the server may reset them.

### Demo (two-minute flow)

1. Show income, spending and an overspent category in the dashboard.
2. Add "Groceries — 1,500 Ft" and show the totals change.
3. Ask the agent "Why am I over budget?" and reveal its tool calls.
4. Ask "Can I spend 7000 Ft on a hoodie?"; observe the agent or simulator calculate category pressure.
5. Emphasize student usefulness, tool-backed arithmetic, privacy-by-design and future features.

### Ideas for expanding after the MVP

- CSV imports from a bank statement (only with clear user consent and redaction)
- Receipt scanning with explicit review before adding expenses
- User accounts + secure database with encrypted storage
- Recurring bills and due-date reminders
- Real store price comparison via permitted APIs, with source dates

### Limitations

This is a hackathon MVP, not a production financial product. Income, budgets and example transactions are fictional. Savings are a *goal*, not a real account balance. Calculations omit unlogged bills. The offline version is not AI: it is a deterministic rules-based demonstration. No guarantee of affordability or professional financial guidance is given.
