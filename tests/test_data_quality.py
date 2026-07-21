import tempfile
import unittest
from pathlib import Path

from backend.app.data_quality import inspect_workbook
from backend.app.demo import create_demo_workbook


class DataQualityTests(unittest.TestCase):
    def test_inspect_workbook_when_demo_is_complete_reports_ready_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workbook = create_demo_workbook(Path(directory) / "demo.xlsx", days=45)
            status = inspect_workbook(workbook)

        self.assertEqual(status.overall_status, "ready")
