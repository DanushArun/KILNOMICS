import unittest

from backend.app.runs import RunStore


class RunStoreTests(unittest.TestCase):
    def test_create_when_new_training_is_started_reports_queued_progress(self) -> None:
        store = RunStore()
        run_id = store.create()

        self.assertEqual(store.snapshot(run_id)["progress_pct"], 0)

    def test_update_when_validation_completes_reports_validation_progress(self) -> None:
        store = RunStore()
        run_id = store.create()
        store.update(run_id, "training", 30)

        self.assertEqual(store.snapshot(run_id)["phase"], "training")

    def test_complete_when_analysis_finishes_reports_full_progress(self) -> None:
        store = RunStore()
        run_id = store.create()
        store.complete(run_id, {"source": "demo.xlsx"})

        self.assertEqual(store.snapshot(run_id)["progress_pct"], 100)
