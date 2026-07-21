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

        self.assertTrue({"CostAssumptions", "RawMixDaily"}.issubset(sheet_names))
