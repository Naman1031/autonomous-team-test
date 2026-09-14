import unittest
from fastapi.testclient import TestClient
from src.api.coupons import app, coupon_service

class TestCouponAPI(unittest.TestCase):
    def setUp(self):
        coupon_service._coupons.clear()
        self.client = TestClient(app)

    def test_create_fixed_discount_coupon_success(self):
        payload = {
            "code": "SAVE10",
            "discount_type": "FIXED",
            "discount_value": 10.0,
            "expiration_date": "2026-12-31T23:59:59"
        }
        response = self.client.post("/api/v1/coupons", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["code"], "SAVE10")
        self.assertEqual(data["discount_type"], "FIXED")
        self.assertEqual(data["discount_value"], 10.0)
        self.assertTrue(data["is_active"])
        self.assertIsNotNone(data["id"])

    def test_create_duplicate_coupon_code_fails(self):
        payload = {
            "code": "SAVE10",
            "discount_type": "FIXED",
            "discount_value": 10.0,
            "expiration_date": "2026-12-31T23:59:59"
        }
        res1 = self.client.post("/api/v1/coupons", json=payload)
        self.assertEqual(res1.status_code, 201)

        res2 = self.client.post("/api/v1/coupons", json=payload)
        self.assertEqual(res2.status_code, 409)
        self.assertIn("Duplicate code error", res2.json()["detail"])

if __name__ == "__main__":
    unittest.main()
