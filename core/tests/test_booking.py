from core.models import Booking, PricingRule, Property
from django.test import TestCase
from rest_framework.test import APIClient


class TestBooking(TestCase):
    @classmethod
    def setUp(self):
        case1_property = Property.objects.create(name="Mock Property", base_price=10)
        case1_property.save()

        case2_property = Property.objects.create(name="Mock Property", base_price=10)
        case2_property.save()

        case3_property = Property.objects.create(name="Mock Property", base_price=10)
        case3_property.save()

        case1_pricing_rule = PricingRule.objects.create(
            property=case1_property, price_modifier=0.9, min_stay_length=7
        )
        case1_pricing_rule.save()

        case2_pricing_rule_1 = PricingRule.objects.create(
            property=case2_property, price_modifier=0.8, min_stay_length=30
        )

        case2_pricing_rule_2 = PricingRule.objects.create(
            property=case2_property, price_modifier=0.9, min_stay_length=7
        )
        case2_pricing_rule_1.save()
        case2_pricing_rule_2.save()

        case3_pricing_rule_1 = PricingRule.objects.create(
            property=case3_property, price_modifier=0.9, min_stay_length=7
        )
        case3_pricing_rule_2 = PricingRule.objects.create(
            property=case3_property, fixed_price=20, specific_day="2022-01-04"
        )
        case3_pricing_rule_1.save()
        case3_pricing_rule_2.save()

    def test_booking_case_1(self):
        factory = APIClient()
        request_body = {"property": 1, "date_start": "01-01-2022", "date_end": "01-10-2022"}
        request = factory.post("/booking/", request_body, format="json")
        self.assertEqual(request.status_code, 201)
        self.assertEqual(request.data["final_price"], 90)

    def test_booking_case_2(self):
        factory = APIClient()
        request_body = {"property": 2, "date_start": "01-01-2022", "date_end": "01-10-2022"}
        request = factory.post("/booking/", request_body, format="json")
        self.assertEqual(request.status_code, 201)
        self.assertEqual(request.data["final_price"], 90)

    def test_booking_case_3(self):
        factory = APIClient()
        request_body = {"property": 3, "date_start": "01-01-2022", "date_end": "01-10-2022"}
        request = factory.post("/booking/", request_body, format="json")
        self.assertEqual(request.status_code, 201)
        self.assertEqual(request.data["final_price"], 101)

    def tearDown(self) -> None:
        return super().tearDown()
