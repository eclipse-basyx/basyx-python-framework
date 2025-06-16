import os
import unittest
import json

from fastapi.testclient import TestClient

from server import app

client = TestClient(app)
BASE_URL = "/api/v3.0/"


class TestSubmodelService(unittest.TestCase):
    def setUp(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.client = TestClient(app)

        with open(os.path.join(base_path, "examples/submodel", "submodel.json"), encoding="utf-8") as f:
            self.submodel_example = json.load(f)
        with open(os.path.join(base_path, "examples/submodel", "submodel_modified.json"), encoding="utf-8") as f:
            self.test_submodel_modified = json.load(f)
        with open(os.path.join(base_path, "examples/submodel", "submodel_element.json"), encoding="utf-8") as f:
            self.submodel_element = json.load(f)
        with open(os.path.join(base_path, "examples/submodel", "submodel_element_new.json"), encoding="utf-8") as f:
            self.submodel_element_new = json.load(f)
        with open(os.path.join(base_path, "examples/submodel", "submodel_with_new_element.json"), encoding="utf-8") as f:
            self.submodel_with_new_element = json.load(f)

        self.submodel_example_id = self.submodel_example["id"]
        self.invalid_submodel_id = "some_id"
        self.invalid_submodel_element_id = "some_unknown_element_id"

    # Test submodel items
    def test_get_all_submodels(self):
        response = self.client.get(BASE_URL + "submodels")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

        # Setup
        self.client.post(BASE_URL + "submodels", json=self.submodel_example)

        response = self.client.get(BASE_URL + "submodels")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [self.submodel_example])

        # Teardown
        self.client.delete(BASE_URL + "submodels/" + self.submodel_example_id)

    def test_post_submodel(self):
        response = self.client.post(BASE_URL + "submodels", json=self.submodel_example)
        self.assertEqual(response.status_code, 200)
        self.client.delete(BASE_URL + "submodels/" + self.submodel_example_id)

    def test_get_specific_submodel(self):
        # Setup
        self.client.post(BASE_URL + "submodels", json=self.submodel_example)

        response_test_undefined = self.client.get(BASE_URL + "submodels/" + self.invalid_submodel_id)
        response_test_entry = self.client.get(BASE_URL + "submodels/" + self.submodel_example_id)

        self.assertEqual(response_test_undefined.status_code, 404)
        self.assertEqual(response_test_entry.status_code, 200)
        self.assertEqual(response_test_entry.json(), self.submodel_example)

        # Teardown
        self.client.delete(BASE_URL + "submodels/" + self.submodel_example_id + "/")

    def test_get_specific_submodel_element(self):
        # Setup
        self.client.post(BASE_URL + "submodels", json=self.submodel_example)

        response = self.client.get(
            BASE_URL + "submodels/" + self.submodel_example_id + "/submodel-elements/" + "list_1")
        self.assertEqual(response.status_code, 200)

        response_none = self.client.get(BASE_URL + "submodels/" + self.submodel_example_id + "/submodel-elements/"
                                        + "list_undefined")
        self.assertEqual(response_none.status_code, 404)

        # Teardown
        self.client.delete(BASE_URL + "submodels/" + self.submodel_example_id + "/")

    def test_post_submodel_element(self):
        # Setup
        self.client.post(BASE_URL + "submodels", json=self.submodel_example)

        response = self.client.post(BASE_URL + "submodels/" + self.submodel_example_id + "/submodel-elements",
                                    json=self.submodel_element_new)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.submodel_element_new)


        response_already_exists = self.client.post(BASE_URL + "submodels/" + self.submodel_example_id + "/submodel-elements",
                                    json=self.submodel_element_new)
        self.assertEqual(response_already_exists.status_code, 400)

        new_submodel = self.client.get(BASE_URL + "submodels/" + self.submodel_example_id)
        self.assertEqual(new_submodel.status_code, 200)
        self.assertEqual(new_submodel.json(), self.submodel_with_new_element)

    def test_delete_submodel_element(self):
        # Setup
        self.client.post(BASE_URL + "submodels", json=self.submodel_example)
        self.client.post(BASE_URL + "submodels/" + self.submodel_example_id + "/submodel-elements",
                                    json=self.submodel_element_new)


        response = self.client.delete(
            BASE_URL + "submodels/" + self.submodel_example_id + "/submodel-elements/" + "some_property_123")
        self.assertEqual(response.status_code, 200)

        response_not_found = self.client.delete(
            BASE_URL + "submodels/" + self.submodel_example_id + "/submodel-elements/" + "some_property_unknown")
        self.assertEqual(response_not_found.status_code, 404)

        new_submodel = self.client.get(BASE_URL + "submodels/" + self.submodel_example_id)
        self.assertEqual(new_submodel.status_code, 200)
        self.assertEqual(new_submodel.json(), self.submodel_example)

        # Teardown
        self.client.delete(BASE_URL + "submodels/" + self.submodel_example_id + "/")



if __name__ == "__main__":
    unittest.main()
