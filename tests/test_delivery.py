# tests/test_delivery.py

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))


from delivery_service import calculate_delivery_cost


ERROR_DATE = "0000-00-00"


class TestDeliveryWeightLimits(unittest.TestCase):

    def test_weight_below_minimum_returns_error(self):
        cost, date = calculate_delivery_cost(0.05, 100, "обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, ERROR_DATE)

    def test_weight_above_maximum_returns_error(self):
        cost, date = calculate_delivery_cost(51.0, 100, "обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, ERROR_DATE)

    def test_weight_minimum_boundary_is_valid(self):
        cost, date = calculate_delivery_cost(0.1, 100, "обычный")
        self.assertNotEqual(cost, -1)

    def test_weight_maximum_boundary_is_valid(self):
        cost, date = calculate_delivery_cost(50.0, 100, "обычный")
        self.assertNotEqual(cost, -1)


class TestDeliveryDistanceLimits(unittest.TestCase):

    def test_distance_below_minimum_returns_error(self):
        cost, date = calculate_delivery_cost(1.0, 0, "обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, ERROR_DATE)

    def test_distance_above_maximum_returns_error(self):
        cost, date = calculate_delivery_cost(1.0, 5001, "обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, ERROR_DATE)

    def test_distance_minimum_boundary_is_valid(self):
        cost, date = calculate_delivery_cost(1.0, 1, "обычный")
        self.assertNotEqual(cost, -1)

    def test_distance_maximum_boundary_is_valid(self):
        cost, date = calculate_delivery_cost(1.0, 5000, "обычный")
        self.assertNotEqual(cost, -1)


class TestDeliveryPackageType(unittest.TestCase):

    def test_invalid_package_type_returns_error(self):
        cost, date = calculate_delivery_cost(1.0, 100, "супер")
        self.assertEqual(cost, -1)
        self.assertEqual(date, ERROR_DATE)

    def test_empty_package_type_returns_error(self):
        cost, date = calculate_delivery_cost(1.0, 100, "")
        self.assertEqual(cost, -1)
        self.assertEqual(date, ERROR_DATE)


class TestDeliveryBaseCost(unittest.TestCase):

    def test_base_cost_simple_case(self):
        # weight=1 (не >5), distance=100 -> 200 + 100*5 = 700
        cost, date = calculate_delivery_cost(1.0, 100, "обычный")
        self.assertEqual(cost, 700)

    def test_base_cost_long_distance(self):
        # distance=1000 -> 200 + 5000 = 5200
        cost, date = calculate_delivery_cost(1.0, 1000, "обычный")
        self.assertEqual(cost, 5200)


class TestDeliveryWeightCoefficients(unittest.TestCase):

    def test_weight_between_5_and_20_uses_1_2_multiplier(self):
        cost, date = calculate_delivery_cost(10.0, 100, "обычный")
        self.assertEqual(cost, 840)

    def test_weight_exactly_5_no_multiplier(self):
        cost, date = calculate_delivery_cost(5.0, 100, "обычный")
        self.assertEqual(cost, 700)

    def test_weight_exactly_20_uses_1_5_multiplier(self):
        cost, date = calculate_delivery_cost(20.0, 100, "обычный")
        self.assertEqual(cost, 1050)

    def test_weight_above_20_uses_1_5_multiplier(self):
        cost, date = calculate_delivery_cost(30.0, 100, "обычный")
        self.assertEqual(cost, 1050)


class TestDeliveryPackageSurcharges(unittest.TestCase):

    def test_fragile_surcharge_is_300(self):
        # обычный: 700, хрупкий: 700+300=1000
        cost, date = calculate_delivery_cost(1.0, 100, "хрупкий")
        self.assertEqual(cost, 1000)

    def test_dangerous_surcharge_is_1000(self):
        # обычный: 700, опасный: 700+1000=1700
        cost, date = calculate_delivery_cost(1.0, 100, "опасный")
        self.assertEqual(cost, 1700)


class TestDeliveryExpress(unittest.TestCase):
    """
    Бизнес-логика: экспресс-доставка должна УДОРОЖАТЬ заказ,
    потому что это дополнительная услуга.
    В коде стоит '*0.5', что УДЕШЕВЛЯЕТ — это баг.
    """

    def test_express_should_be_more_expensive_than_regular(self):
        regular, _ = calculate_delivery_cost(1.0, 100, "обычный", is_express=False)
        express, _ = calculate_delivery_cost(1.0, 100, "обычный", is_express=True)
        self.assertGreater(express, regular)

    def test_express_cost_is_expected_value(self):
        # Ожидаемое поведение: экспресс дороже, например x1.5.
        # При distance=100: 700 * 1.5 = 1050
        cost, date = calculate_delivery_cost(1.0, 100, "обычный", is_express=True)
        self.assertEqual(cost, 1050)

    def test_express_does_not_make_delivery_cheaper(self):
        regular, _ = calculate_delivery_cost(10.0, 500, "хрупкий", is_express=False)
        express, _ = calculate_delivery_cost(10.0, 500, "хрупкий", is_express=True)
        self.assertGreaterEqual(express, regular)


class TestDeliveryDates(unittest.TestCase):

    def test_delivery_date_short_distance(self):
        # distance=100 -> max(1, 0) = 1 -> 2026-09-04
        cost, date = calculate_delivery_cost(1.0, 100, "обычный")
        self.assertEqual(date, "2026-09-04")

    def test_delivery_date_medium_distance(self):
        # distance=1000 -> 1000//500 = 2 -> 2026-09-05
        cost, date = calculate_delivery_cost(1.0, 1000, "обычный")
        self.assertEqual(date, "2026-09-05")

    def test_delivery_date_long_distance(self):
        # distance=5000 -> 5000//500 = 10 -> 2026-09-13
        cost, date = calculate_delivery_cost(1.0, 5000, "обычный")
        self.assertEqual(date, "2026-09-13")

    def test_express_delivery_is_faster(self):
        # Ожидаемое поведение: экспресс должен уменьшать срок доставки.
        # При distance=1000: обычный = 2 дня -> 2026-09-05,
        # экспресс должен быть 1 день -> 2026-09-04.
        # В коде: 2 // 2 = 1 -> 2026-09-04. Тест ПРОХОДИТ.
        _, regular_date = calculate_delivery_cost(1.0, 1000, "обычный", is_express=False)
        _, express_date = calculate_delivery_cost(1.0, 1000, "обычный", is_express=True)
        self.assertLess(express_date, regular_date)


if __name__ == "__main__":
    unittest.main()