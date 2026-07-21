import tempfile
import unittest
from pathlib import Path

from backend.app.demo import create_demo_workbook
from backend.app.summary import workbook_summary


class SummaryTests(unittest.TestCase):
    def test_workbook_summary_when_demo_is_loaded_returns_positive_cement_cost(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workbook = create_demo_workbook(Path(directory) / "demo.xlsx", days=10)
            summary = workbook_summary(workbook)

        self.assertGreater(summary["cement_cost_per_t"], 0)

    def test_workbook_summary_when_demo_is_loaded_returns_daily_shc_series(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workbook = create_demo_workbook(Path(directory) / "demo.xlsx", days=45)
            summary = workbook_summary(workbook)

        self.assertEqual(len(summary["shc_series"]), 45)
