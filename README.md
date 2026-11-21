# 💠 Centsyra — student budgeting companion

A working Streamlit starter app for a two-person hackathon team. **Python 3.13 recommended.** All values are monthly Hungarian forints (HUF). No data is stored or sent to a bank.

## Same project, two laptops

Both teammates should download and extract **the same ZIP** to their own laptops. Nobody needs to manually recreate the source files. In VS Code select **File → Open Folder → Centsyra**.

| Teammate | Owns | Work |
|---|---|---|
| You | `budget.py`, `agent.py` | Budget analysis, savings calculations, OpenAI coach |
| Brother | `app.py`, `.streamlit/config.toml` | Layout, input widgets, charts, styling |

**Do not change these integration functions without telling each other:**

- `analyze_budget(income, expenses) -> dict`
- `get_ai_advice(income, expenses, goal) -> str`

`expenses` is a dictionary like `{"Rent": 85000, "Groceries": 45000}`. The frontend expects the budget keys `income`, `total_expenses`, `remaining_balance`, `savings_rate`, `category_breakdown`, `largest_expense_category`, and `overspending`.

## Start the app on Windows (PowerShell / VS Code terminal)

Open the `Centsyra` folder in VS Code. In **Terminal → New Terminal**, run these commands one at a time:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If the first command reports that Python 3.13 isn't found, try `py -3 -m venv .venv` only if `py -3 --version` prints a working recent Python. You do **not** need to activate the virtual environment or change PowerShell execution policy.

A browser opens the app. To stop it press `Ctrl + C` in the terminal. To restart it later:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Optional live AI

Without an API key, the app still runs in *offline demo mode*, using transparent rule-based suggestions.

To use a real OpenAI API key, make a copy of `.env.example` named `.env` **inside your Centsyra folder**. Enter your key in `.env` after `OPENAI_API_KEY=`. Run the Streamlit command again. This requires Internet access and an OpenAI API account with API access; ChatGPT subscriptions don't automatically include API credits. **Never paste your key into a chat, commit it to GitHub, or put it in `app.py`.**

## Combine the two laptops' work

**Easiest hackathon method:** One person is the integration owner. When backend changes are ready, that person sends the updated `budget.py` and `agent.py` (not `.env` or `.venv`) to the frontend teammate, who replaces those two files in their own Centsyra folder and restarts Streamlit. Keep the frontend teammate's edited `app.py`. Later you can use a shared GitHub repo with branches, but don't both overwrite the same files.

## Verify calculations

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Demo walkthrough

1. Show the dashboard and edit rent or groceries to see instant metrics update.
2. Increase expenses above income to trigger the overspending warning.
3. Adjust the savings goal and show progress.
4. Click **Analyze my budget** for recommendations (offline by default; live AI after adding your own key).

## Ideas to add if you finish early

- Editable custom spending categories and CSV upload.
- A multi-step AI agent that chooses from budget-calculation and savings-plan tools.
- Student-specific local expense tips, weekly budgeting challenges, and an exportable action plan.
