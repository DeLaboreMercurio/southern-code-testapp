from core.models import Property
from django.test import TestCase
from rest_framework.test import APIClient


class TestProperty(TestCase):
    @classmethod
    def setUp(self):
        mock_property = Property.objects.create(name="Mock Property", base_price=1000)
        mock_property.save()

    def test_property_get_all_properties(self):
        factory = APIClient()
        request = factory.get("/property/")
        self.assertEqual(request.status_code, 200)

    def test_property_get_single_property(self):
        factory = APIClient()
        request = factory.get("/property/1/")
        self.assertEqual(request.status_code, 200)

    def test_property_get_single_property_with_invalid_id(self):
        factory = APIClient()
        request = factory.get("/property/0/")
        self.assertEqual(request.status_code, 404)

    def test_property_creation(self):
        factory = APIClient()
        request_body = {"name": "Test Property", "base_price": 100.00}

        request = factory.post("/property/", request_body, format="json")
        self.assertEqual(request.status_code, 201)
        self.assertIsNotNone(request.data["id"])

    def test_property_creation_with_invalid_base_price(self):
        factory = APIClient()
        request_body = {"name": "Test Property", "base_price": -100.00}

        request = factory.post("/property/", request_body, format="json")
        self.assertEqual(request.status_code, 400)

    def test_property_creation_with_invalid_name(self):
        factory = APIClient()
        request_body = {"name": "", "base_price": 100.00}

        request = factory.post("/property/", request_body, format="json")
        self.assertEqual(request.status_code, 400)

    def test_property_patch(self):
        factory = APIClient()
        request_body = {
            "name": "Test Property for patching",
            "base_price": 100.00,
        }

        request = factory.post("/property/", request_body, format="json")
        self.assertEqual(request.status_code, 201)
        self.assertIsNotNone(request.data["id"])

        request = factory.patch(
            "/property/{}/".format(request.data["id"]),
            {"name": "Test Property patched"},
            format="json",
        )
        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["name"], "Test Property patched")

    def test_property_patch_with_invalid_base_price(self):
        factory = APIClient()
        request_body = {
            "name": "Test Property for patching",
            "base_price": 100.00,
        }

        request = factory.post("/property/", request_body, format="json")
        self.assertEqual(request.status_code, 201)
        self.assertIsNotNone(request.data["id"])

        request = factory.patch(
            "/property/{}/".format(request.data["id"]),
            {"name": "Test Property patched", "base_price": -100.00},
            format="json",
        )
        self.assertEqual(request.status_code, 400)

    def test_property_put(self):
        factory = APIClient()
        request_body = {
            "name": "Test Property for PUT",
            "base_price": 100.00,
        }

        request = factory.post("/property/", request_body, format="json")
        self.assertEqual(request.status_code, 201)
        self.assertIsNotNone(request.data["id"])

        put_request = factory.put(
            "/property/{}/".format(request.data["id"]),
            {"name": "Test Property PUT", "base_price": 150.00},
            format="json",
        )
        self.assertEqual(put_request.status_code, 200)
        self.assertEqual(put_request.data["name"], "Test Property PUT")
        self.assertEqual(put_request.data["base_price"], 150.00)
        self.assertEqual(request.data["id"], put_request.data["id"])

    def test_property_delete(self):
        factory = APIClient()
        request_body = {
            "name": "Test Property for deletion",
            "base_price": 100.00,
        }

        request = factory.post("/property/", request_body, format="json")
        self.assertEqual(request.status_code, 201)
        self.assertIsNotNone(request.data["id"])

        delete_request = factory.delete("/property/{}/".format(request.data["id"]), format="json")
        self.assertEqual(delete_request.status_code, 204)

    def tearDown(self) -> None:
        return super().tearDown()
