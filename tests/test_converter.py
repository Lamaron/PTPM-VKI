import unittest
from src.converter import Converter


class TestConverterBoundaries(unittest.TestCase):

    def test_lower_bound_of_top_range(self):
        self.assertEqual(Converter.do(100.7), 1000)

    def test_just_below_top_range(self):
        self.assertEqual(Converter.do(100.6), 100)

    def test_large_positive(self):
        self.assertEqual(Converter.do(9999.9), 1000)

    def test_min_positive(self):
        self.assertEqual(Converter.do(0.1), 0)

    def test_positive_fraction_truncated(self):
        self.assertEqual(Converter.do(65.7), 65)

    def test_positive_integer_part(self):
        self.assertEqual(Converter.do(50.0), 50)

    def test_zero_raises(self):
        with self.assertRaises(ValueError):
            Converter.do(0.0)

    def test_zero_raises_message(self):
        with self.assertRaises(ValueError) as ctx:
            Converter.do(0.0)
        self.assertIn("0.0", str(ctx.exception))

    def test_lower_bound_of_negative_range(self):
        self.assertEqual(Converter.do(-30.4), -35)

    def test_mid_negative_range(self):
        self.assertEqual(Converter.do(-15.7), -20)

    def test_close_to_zero_negative(self):
        self.assertEqual(Converter.do(-0.5), -5)

    def test_just_below_zero(self):
        self.assertEqual(Converter.do(-0.1), -5)

    def test_upper_bound_of_bottom_range(self):
        self.assertEqual(Converter.do(-30.5), -2000)

    def test_large_negative(self):
        self.assertEqual(Converter.do(-94.5), -2000)

    def test_very_large_negative(self):
        self.assertEqual(Converter.do(-1000000.0), -2000)


if __name__ == "__main__":
    unittest.main(verbosity=2)