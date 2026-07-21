import tempfile
import unittest
from pathlib import Path

import pandas as pd

from backend.app.demo import create_demo_workbook


class DemoWorkbookTests(unittest.TestCase):
    def test_create_demo_workbook_when_called_writes_required_sheets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = create_demo_workbook(Path(directory) / "demo.xlsx")
            sheet_names = set(pd.ExcelFile(path).sheet_names)

        expected = {
            "README", "PlantMaster", "MaterialSources", "FuelLibrary", "CementConstituents",
            "KilnConfig", "Targets", "ProductRecipe", "KilnFeedDaily", "FuelDaily",
            "ClinkerDaily", "CementDaily", "EnergyDaily", "ProcessDaily", "CircLoad",
            "CostAssumptions", "RawMixDaily",
        }
        self.assertSetEqual(sheet_names, expected)

    def test_create_demo_workbook_when_loaded_uses_fictional_portfolio_names(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = create_demo_workbook(Path(directory) / "demo.xlsx")
            plants = pd.read_excel(path, sheet_name="PlantMaster")

        self.assertListEqual(plants["plant_name"].tolist(), ["Aster Works", "Beacon Works", "Crest Works"])

    def test_create_demo_workbook_when_loaded_gives_each_plant_a_distinct_tsr_limit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = create_demo_workbook(Path(directory) / "demo.xlsx")
            limits = pd.read_excel(path, sheet_name="KilnConfig")

        self.assertListEqual(limits["tsrMaxPct"].tolist(), [18, 16, 12])
