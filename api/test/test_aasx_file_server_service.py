import os
import json
import unittest
from fastapi.testclient import TestClient

from server import app
from aas_core3 import jsonization

client = TestClient(app)
BASE_URL = "/api/v3.0/"


class TestFastAPIEndpoints(unittest.TestCase):
    def setUp(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.client = TestClient(app)

        with open(os.path.join(base_path, "examples/aasx", "aasx.json"), encoding="utf-8") as f:
            self.aasx_json = json.load(f)

        self.test_aasx_id = self.aasx_json["id"]
        self.aasx = jsonization.asset_administration_shell_from_jsonable(self.aasx_json)

    def test_get_all_aasx_package_ids(self):
        # Test empty
        response = self.client.get(BASE_URL + "aasx")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

        # Setup
        self.client.post(BASE_URL + "aasx", json=self.aasx_json)

        response = self.client.get(BASE_URL + "aasx")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [self.test_aasx_id])

        # Teardown
        self.client.delete(BASE_URL + "aasx/" + self.test_aasx_id)

    def test_post_aasx_package(self):
        response = client.post(BASE_URL + "aasx", json=self.aasx_json)
        self.assertEqual(response.status_code, 200)

        # Teardown
        self.client.delete(BASE_URL + "aasx/" + self.test_aasx_id)

    def test_get_aasx_package(self):
        # Setup
        self.client.post(BASE_URL + "aasx", json=self.aasx_json)

        response_test_entry = client.get(BASE_URL + "aasx/" + self.test_aasx_id)
        self.assertEqual(response_test_entry.status_code, 200)
        self.assertEqual(response_test_entry.json(), self.aasx_json)

        # Teardown
        self.client.delete(BASE_URL + "aasx/" + self.test_aasx_id)

    def test_delete_aasx_package(self):
        pass

    def test_put_aasx_package(self):
        pass

# FIXME: Add missing tests

if __name__ == "__main__":
    unittest.main()
