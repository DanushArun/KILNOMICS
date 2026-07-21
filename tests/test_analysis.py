import tempfile
import unittest
from pathlib import Path

from backend.app.analysis import analyze_workbook, evaluate_scenario
from backend.app.demo import create_demo_workbook


class AnalysisTests(unittest.TestCase):
    def test_analyze_workbook_when_demo_is_loaded_returns_illustrative_portfolio(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workbook = create_demo_workbook(Path(directory) / "demo.xlsx", days=45)
            result = analyze_workbook(workbook)

        self.assertEqual(result["provenance"]["mode"], "simulated")

    def test_analyze_workbook_when_demo_is_loaded_keeps_realised_value_at_zero(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workbook = create_demo_workbook(Path(directory) / "demo.xlsx", days=45)
            result = analyze_workbook(workbook)

        self.assertEqual(result["finance_status"]["realised_annual_rs"], 0)

    def test_analyze_workbook_when_demo_is_loaded_returns_each_plant(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workbook = create_demo_workbook(Path(directory) / "demo.xlsx", days=45)
            result = analyze_workbook(workbook)

        self.assertEqual(len(result["plants"]), 3)

    def test_evaluate_scenario_when_tsr_exceeds_capability_blocks_value(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workbook = create_demo_workbook(Path(directory) / "demo.xlsx", days=45)
            analysis = analyze_workbook(workbook)
            result = evaluate_scenario(analysis, "DEMO_ASTER", {"tsr_pct": 30})

        self.assertFalse(result["feasible"])

    def test_evaluate_scenario_when_tsr_exceeds_capability_returns_no_savings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workbook = create_demo_workbook(Path(directory) / "demo.xlsx", days=45)
            analysis = analyze_workbook(workbook)
            result = evaluate_scenario(analysis, "DEMO_ASTER", {"tsr_pct": 30})

        self.assertEqual(result["annual_savings_rs"], 0)
