import unittest
from fastapi.testclient import TestClient
from app.main import app


class TestLookupEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_lookup(self):
        # Convert 39°11'58.9"N 106°49'31.3"W to approximate decimal degrees
        lat = 39.1997
        lon = -106.8253

        response = self.client.get(f"/lookup?lat={lat}&lon={lon}")
        self.assertEqual(response.status_code, 200, "Endpoint did not return a 200 OK status")

        data = response.json()
        self.assertIn("name", data, "Response does not contain 'name'")
        self.assertIn("info", data, "Response does not contain 'info'")


if __name__ == "__main__":
    unittest.main()