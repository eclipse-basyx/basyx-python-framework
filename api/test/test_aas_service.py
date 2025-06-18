import os
import json
import unittest
from fastapi.testclient import TestClient

from server import app

from test import wrap_paginated

BASE_URL = "/api/v3.0/"


class TestAASService(unittest.TestCase):
    def setUp(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.client = TestClient(app)

        with open(os.path.join(base_path, "examples/aas", "aas.json"), encoding="utf-8") as f:
            self.aas_example = json.load(f)

        with open(os.path.join(base_path, "examples/aas", "asset_information.json"), encoding="utf-8") as f:
            self.asset_information_example = json.load(f)

        with open(os.path.join(base_path, "examples/aas", "asset_information_modified.json"), encoding="utf-8") as f:
            self.asset_information_example_modified = json.load(f)

        with open(os.path.join(base_path, "examples/aas", "asset_information_no_thumbnail.json"), encoding="utf-8") as f:
            self.asset_information_example_no_thumbnail = json.load(f)

        with open(os.path.join(base_path, "examples/aas", "thumbnail.json"), encoding="utf-8") as f:
            self.thumbnail_example = json.load(f)

        with open(os.path.join(base_path, "examples/aas", "thumbnail_modified.json"), encoding="utf-8") as f:
            self.thumbnail_example_modified = json.load(f)

        with open(os.path.join(base_path, "examples", "empty_paged_result.json"), encoding="utf-8") as f:
            self.empty_result = json.load(f)

        # FIXME: modified AAS should contain more complex types but deserialization seems to fail
        with open(os.path.join(base_path, "examples/aas", "aas_modified.json"), encoding="utf-8") as f:
            self.aas_example_modified = json.load(f)

        self.shell_example_id = self.aas_example["id"]
        self.invalid_shell_example_id = "some_other_id"

    def test_aas_post(self):
        response = self.client.post(BASE_URL + "aas/shells", json=self.aas_example)
        self.assertEqual(response.status_code, 200)

        # Teardown
        self.client.delete(BASE_URL + "aas/shells/" + self.shell_example_id)

    def test_get_all_shells(self):
        response = self.client.get(BASE_URL + "aas/shells")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.empty_result)

        # Setup
        self.client.post(BASE_URL + "aas/shells", json=self.aas_example)

        response = self.client.get(BASE_URL + "aas/shells")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), wrap_paginated([self.aas_example]))

        # Teardown
        self.client.delete(BASE_URL + "ass/shells/" + self.shell_example_id)

    def test_get_specific_shell(self):
        # Setup
        self.client.post(BASE_URL + "aas/shells", json=self.aas_example)

        response_test_undefined = self.client.get(BASE_URL + "aas/shells/" + self.invalid_shell_example_id)
        response_test_entry = self.client.get(BASE_URL + "aas/shells/" + self.shell_example_id)

        self.assertEqual(response_test_undefined.status_code, 404)
        self.assertEqual(response_test_entry.status_code, 200)
        self.assertEqual(response_test_entry.json(), self.aas_example)

        # Teardown
        self.client.delete(BASE_URL + "aas/shells/" + self.shell_example_id)

    def test_put_shell(self):
        # Setup and Preconditions
        self.assertNotEqual(self.aas_example, self.aas_example_modified)
        self.client.post(BASE_URL + "aas/shells", json=self.aas_example)

        response_normal = self.client.get(BASE_URL + "aas/shells/" + self.shell_example_id)
        self.assertEqual(response_normal.json(), self.aas_example)

        response = self.client.put(BASE_URL + "aas/shells/" + self.shell_example_id, json=self.aas_example_modified)
        self.assertEqual(response.status_code, 200)
        response_overwritten = self.client.get(BASE_URL + "aas/shells/" + self.shell_example_id)
        self.assertEqual(response_overwritten.status_code, 200)
        self.assertEqual(response_overwritten.json(), self.aas_example_modified)

        # Teardown
        self.client.delete(BASE_URL + "aas/shells/" + self.shell_example_id)

    # FIXME: Technically a test_delete_shell would be added here. Is this really necessary? Kinda covered by the rest

    # Asset Information Endpoints

    def test_get_asset_information(self):
        # Setup
        self.client.post(BASE_URL + "aas/shells", json=self.aas_example)

        response = self.client.get(BASE_URL + "aas/shells/" + self.shell_example_id + "/asset-information")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.asset_information_example)

        # Teardown
        self.client.delete(BASE_URL + "aas/shells/" + self.shell_example_id)

    def test_put_asset_information(self):
        # Setup
        self.client.post(BASE_URL + "aas/shells", json=self.aas_example)

        # Replace the asset-information converting aas_example to aas_example_modified
        # FIXME: This should probably have more complex asset-information to test
        response = self.client.put(BASE_URL + "aas/shells/" + self.shell_example_id + "/asset-information",
                                   json=self.asset_information_example_modified)
        self.assertEqual(response.status_code, 200)

        response_modified = self.client.get(BASE_URL + "aas/shells/" + self.shell_example_id + "/asset-information")
        self.assertEqual(response_modified.status_code, 200)
        self.assertEqual(response_modified.json(), self.asset_information_example_modified)

        # Teardown
        self.client.delete(BASE_URL + "aas/shells/" + self.shell_example_id)

    def test_get_asset_information_thumbnail(self):
        # Setup
        self.client.post(BASE_URL + "aas/shells", json=self.aas_example)

        response = self.client.get(BASE_URL + "aas/shells/" + self.shell_example_id + "/asset-information/thumbnail")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.thumbnail_example)

        # Teardown
        self.client.delete(BASE_URL + "aas/shells/" + self.shell_example_id)

    def test_put_asset_information_thumbnail(self):
        # Setup
        self.client.post(BASE_URL + "aas/shells", json=self.aas_example)

        response = self.client.put(BASE_URL + "aas/shells/" + self.shell_example_id + "/asset-information/thumbnail",
                                   json=self.thumbnail_example_modified)
        self.assertEqual(response.status_code, 200)

        response_modified = self.client.get(
            BASE_URL + "aas/shells/" + self.shell_example_id + "/asset-information/thumbnail")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_modified.json(), self.thumbnail_example_modified)

        # Teardown
        self.client.delete(BASE_URL + "aas/shells/" + self.shell_example_id)

    def test_delete_asset_information_thumbnail(self):
        # Setup
        self.client.post(BASE_URL + "aas/shells", json=self.aas_example)

        self.client.delete(BASE_URL + "aas/shells/" + self.shell_example_id + "/asset-information/thumbnail")
        response = self.client.get(BASE_URL + "aas/shells/" + self.shell_example_id + "/asset-information")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.asset_information_example_no_thumbnail)

        # Teardown
        self.client.delete(BASE_URL + "aas/shells/" + self.shell_example_id)

if __name__ == "__main__":
    unittest.main()
