import unittest

from dtrpg.core import DifferentialTester, ProportionalTester, ThresholdTester


class TestTester(unittest.TestCase):
    def test_differential(self) -> None:
        tester = DifferentialTester()

        self.assertEqual(tester._prob(3, 3), 0.5)
        self.assertEqual(tester._prob(5, 15), 0.05)
        self.assertEqual(tester._prob(5, 10), 0.25)
        self.assertEqual(tester._prob(0, 15), 0.05)
        self.assertEqual(tester._prob(15, 10), 0.75)
        self.assertEqual(tester._prob(15, 5), 0.95)
        self.assertEqual(tester._prob(0, 100), 0.05)

    def test_proportional(self) -> None:
        tester = ProportionalTester()

        self.assertEqual(tester._prob(3, 3), 0.5)
        self.assertEqual(tester._prob(5, 15), 1 / 6)
        self.assertEqual(tester._prob(5, 10), 0.25)
        self.assertEqual(tester._prob(0, 15), 0)
        self.assertEqual(tester._prob(20, 10), 0.75)

    def test_threshold(self) -> None:
        tester = ThresholdTester()

        self.assertFalse(tester.test(3, 5))
        self.assertFalse(tester.test(1, 2))
        self.assertFalse(tester.test(4, 6))
        self.assertTrue(tester.test(5, 5))
        self.assertTrue(tester.test(2, 2))
        self.assertTrue(tester.test(6, 2))
