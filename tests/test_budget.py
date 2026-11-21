import unittest

from budget import analyze_budget, suggest_savings_actions


class TestBudget(unittest.TestCase):
    def test_normal_budget(self):
        result = analyze_budget(180000, {"Rent": 85000, "Food": 45000})
        self.assertEqual(result["total_expenses"], 130000)
        self.assertEqual(result["remaining_balance"], 50000)
        self.assertFalse(result["overspending"])
        self.assertEqual(result["largest_expense_category"], "Rent")

    def test_overspending(self):
        result = analyze_budget(10000, {"Food": 12000})
        self.assertTrue(result["overspending"])
        self.assertEqual(result["remaining_balance"], -2000)

    def test_zero_income(self):
        result = analyze_budget(0, {})
        self.assertEqual(result["savings_rate"], 0)

    def test_invalid_amount(self):
        with self.assertRaises(ValueError):
            analyze_budget(1000, {"Food": -1})

    def test_actions(self):
        actions = suggest_savings_actions(10000, {"Food": 12000}, 2000)
        self.assertGreaterEqual(len(actions), 2)


if __name__ == "__main__":
    unittest.main()
