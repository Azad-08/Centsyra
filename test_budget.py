"""Run: python -m unittest test_budget.py"""
import unittest
from datetime import date
from budget import (
    DEFAULT_LIMITS, DEFAULT_INCOME, DEFAULT_SAVINGS_TARGET,
    get_budget_overview, simulate_purchase, seed_transactions,
)


class BudgetBuddyTests(unittest.TestCase):
    def setUp(self):
        self.now = date.today()
        self.tx = seed_transactions()

    def test_sample_month_total(self):
        result = get_budget_overview(DEFAULT_INCOME, DEFAULT_LIMITS, DEFAULT_SAVINGS_TARGET, self.tx, self.now)
        self.assertEqual(result["spent_this_month_huf"], 64650)
        self.assertEqual(result["balance_remaining_huf"], 30350)
        self.assertEqual(result["balance_after_reserving_savings_huf"], 22350)

    def test_overspend_flags_dining(self):
        result = get_budget_overview(DEFAULT_INCOME, DEFAULT_LIMITS, DEFAULT_SAVINGS_TARGET, self.tx)
        self.assertEqual(result["categories"]["Eating out"]["over_budget_huf"], 700)

    def test_simulation_does_not_change_data(self):
        before = len(self.tx)
        result = simulate_purchase(7000, "Shopping & other", DEFAULT_INCOME,
                                   DEFAULT_LIMITS, DEFAULT_SAVINGS_TARGET, self.tx)
        self.assertEqual(result["balance_after_purchase_huf"], 23350)
        self.assertFalse(result["within_category_limit"])
        self.assertEqual(len(self.tx), before)

    def test_previous_month_excluded(self):
        self.tx.append({"date": "2020-01-01", "category": "Groceries", "amount": 99999, "description": "Old"})
        result = get_budget_overview(DEFAULT_INCOME, DEFAULT_LIMITS, DEFAULT_SAVINGS_TARGET, self.tx)
        self.assertEqual(result["spent_this_month_huf"], 64650)


if __name__ == "__main__":
    unittest.main()
