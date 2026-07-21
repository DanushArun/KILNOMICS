import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.demo import create_demo_workbook
from backend.app.main import create_app


class ApiTests(unittest.TestCase):
    def test_start_training_when_workbook_is_valid_returns_a_run_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workbook = create_demo_workbook(Path(directory) / "demo.xlsx", days=45)
            with workbook.open("rb") as file_handle:
                response = TestClient(create_app()).post(
                    "/api/workbooks/train/start",
                    files={"workbook": (
                        "demo.xlsx",
                        file_handle,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )},
                )

        self.assertIsInstance(response.json()["run_id"], str)

    def test_upload_when_demo_workbook_is_valid_returns_training_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workbook = create_demo_workbook(Path(directory) / "demo.xlsx", days=45)
            with workbook.open("rb") as file_handle:
                response = TestClient(create_app()).post(
                    "/api/workbooks/train",
                    files={"workbook": ("demo.xlsx", file_handle, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                )

        self.assertEqual(response.status_code, 200)

    def test_upload_when_demo_workbook_is_valid_returns_data_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workbook = create_demo_workbook(Path(directory) / "demo.xlsx", days=45)
            with workbook.open("rb") as file_handle:
                response = TestClient(create_app()).post(
                    "/api/workbooks/train",
                    files={"workbook": ("demo.xlsx", file_handle, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                )

        self.assertEqual(response.json()["data_status"]["overall_status"], "ready")

    def test_upload_when_demo_workbook_is_valid_returns_portfolio_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workbook = create_demo_workbook(Path(directory) / "demo.xlsx", days=45)
            with workbook.open("rb") as file_handle:
                response = TestClient(create_app()).post(
                    "/api/workbooks/train",
                    files={"workbook": ("demo.xlsx", file_handle, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                )

        self.assertEqual(response.json()["provenance"]["mode"], "simulated")
