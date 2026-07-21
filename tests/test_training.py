import tempfile
import unittest
from pathlib import Path

from backend.app.demo import create_demo_workbook
from backend.app.training import train_workbook


class TrainingTests(unittest.TestCase):
    def test_train_workbook_when_demo_is_uploaded_returns_target_reports(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workbook = create_demo_workbook(Path(directory) / "demo.xlsx", days=45)
            reports = train_workbook(workbook)

        self.assertIn("C3S", reports)
