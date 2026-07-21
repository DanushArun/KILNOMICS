import unittest

from backend.app.chemistry import calculate_moduli


class ChemistryTests(unittest.TestCase):
    def test_calculate_moduli_when_valid_oxides_returns_expected_lsf(self) -> None:
        result = calculate_moduli(65.0, 22.0, 5.0, 3.0)

        self.assertAlmostEqual(result.lsf, 93.59, places=2)

    def test_calculate_moduli_when_valid_oxides_returns_expected_sm(self) -> None:
        result = calculate_moduli(65.0, 22.0, 5.0, 3.0)

        self.assertAlmostEqual(result.sm, 2.75, places=2)

    def test_calculate_moduli_when_valid_oxides_returns_expected_am(self) -> None:
        result = calculate_moduli(65.0, 22.0, 5.0, 3.0)

        self.assertAlmostEqual(result.am, 1.67, places=2)
