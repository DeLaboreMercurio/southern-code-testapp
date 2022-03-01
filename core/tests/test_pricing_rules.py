from core.models import PricingRule, Property
from django.test import TestCase
from rest_framework.test import APIClient


class TestPricingRules(TestCase):
    @classmethod
    def setUp(self):
        mock_property = Property.objects.create(name="Mock Property", base_price=1000)
        mock_property.save()

        mock_pricing_rule = PricingRule.objects.create(
            property=mock_property,
            price_modifier=10.0,
            min_stay_length=2,
            specific_day="2022-10-09",
        )
        mock_pricing_rule.save()

    def test_get_all_pricing_rules(self):
        factory = APIClient()
        request = factory.get("/pricing_rule/")
        self.assertEqual(request.status_code, 200)

    def test_get_single_pricing_rule(self):
        factory = APIClient()
        request = factory.get("/pricing_rule/1/")
        self.assertEqual(request.status_code, 200)

    def test_create_pricing_rule(self):
        factory = APIClient()
        request_body = {
            "property": 1,
            "price_modifier": 10,
            "min_stay_length": 2,
            "specific_day": "09-10-2022",
        }

        request = factory.post("/pricing_rule/", request_body, format="json")
        self.assertEqual(request.status_code, 201)
        self.assertIsNotNone(request.data["id"])

    def test_create_pricing_rule_with_invalid_property(self):
        factory = APIClient()
        request_body = {
            "property": 0,
            "price_modifier": 10,
            "min_stay_length": 2,
            "specific_day": "09-10-2022",
        }

        request = factory.post("/pricing_rule/", request_body, format="json")
        self.assertEqual(request.status_code, 400)

    def test_create_pricing_rule_with_invalid_price_modifier(self):
        factory = APIClient()
        request_body = {
            "property": 1,
            "price_modifier": -10,
            "min_stay_length": 2,
            "specific_day": "09-10-2022",
        }

        request = factory.post("/pricing_rule/", request_body, format="json")
        self.assertEqual(request.status_code, 400)

    def test_create_pricing_rule_with_invalid_min_stay_length(self):
        factory = APIClient()
        request_body = {
            "property": 1,
            "price_modifier": 10,
            "min_stay_length": -1,
            "specific_day": "09-10-2022",
        }

        request = factory.post("/pricing_rule/", request_body, format="json")
        self.assertEqual(request.status_code, 400)

    def test_patch_pricing_rule(self):
        factory = APIClient()
        request_body = {
            "property": 1,
            "price_modifier": 10,
            "min_stay_length": 2,
            "specific_day": "09-10-2022",
        }

        request = factory.post("/pricing_rule/", request_body, format="json")
        self.assertEqual(request.status_code, 201)
        self.assertIsNotNone(request.data["id"])

        request = factory.patch(
            "/pricing_rule/{}/".format(request.data["id"]), {"price_modifier": 20}, format="json"
        )
        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["price_modifier"], 20)

    def test_put_pricing_rule(self):
        factory = APIClient()
        request_body = {
            "property": 1,
            "price_modifier": 10,
            "min_stay_length": 2,
            "specific_day": "09-10-2022",
        }

        request = factory.post("/pricing_rule/", request_body, format="json")
        self.assertEqual(request.status_code, 201)
        self.assertIsNotNone(request.data["id"])

        request = factory.put(
            "/pricing_rule/{}/".format(request.data["id"]),
            {
                "property": 1,
                "price_modifier": 20,
                "min_stay_length": 3,
                "specific_day": "09-10-2022",
            },
            format="json",
        )
        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["price_modifier"], 20)

    def delete_pricing_rule(self):
        factory = APIClient()
        request_body = {
            "property": 1,
            "price_modifier": 10,
            "min_stay_length": 2,
            "specific_day": "09-10-2022",
        }

        request = factory.post("/pricing_rule/", request_body, format="json")
        self.assertEqual(request.status_code, 201)
        self.assertIsNotNone(request.data["id"])

        request = factory.delete("/pricing_rule/{}/".format(request.data["id"]), format="json")
        self.assertEqual(request.status_code, 204)

    def test_get_pricing_rule_with_invalid_id(self):
        factory = APIClient()
        request = factory.get("/pricing_rule/0/")
        self.assertEqual(request.status_code, 404)

    def test_patch_pricing_rule_with_invalid_id(self):
        factory = APIClient()
        request = factory.patch("/pricing_rule/0/", {"price_modifier": 10}, format="json")
        self.assertEqual(request.status_code, 404)

    def test_put_pricing_rule_with_invalid_id(self):
        factory = APIClient()
        request = factory.put(
            "/pricing_rule/0/",
            {
                "property": 1,
                "price_modifier": 20,
                "min_stay_length": 3,
                "specific_day": "09-10-2022",
            },
            format="json",
        )
        self.assertEqual(request.status_code, 404)

    def test_delete_pricing_rule_with_invalid_id(self):
        factory = APIClient()
        request = factory.delete("/pricing_rule/0/", format="json")
        self.assertEqual(request.status_code, 404)

    def tearDown(self) -> None:
        return super().tearDown()
