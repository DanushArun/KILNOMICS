import unittest

from backend.app.model_gate import ModelMetrics, passes_release_gate


class ModelGateTests(unittest.TestCase):
    def test_passes_release_gate_when_every_threshold_is_met_returns_true(self) -> None:
        metrics = ModelMetrics(0.81, 0.18, 16.0, 0.9, 0.91)

        self.assertTrue(passes_release_gate(metrics, 0.2))

    def test_passes_release_gate_when_r_squared_is_low_returns_false(self) -> None:
        metrics = ModelMetrics(0.79, 0.18, 16.0, 0.9, 0.91)

        self.assertFalse(passes_release_gate(metrics, 0.2))
