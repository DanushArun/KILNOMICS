import unittest

from backend.app.costs import annualized_savings


class CostTests(unittest.TestCase):
    def test_annualized_savings_when_cost_is_reduced_returns_annual_rupees(self) -> None:
        result = annualized_savings(2_638.0, 2_571.0, 260_000.0)

        self.assertEqual(result, 209_040_000.0)
