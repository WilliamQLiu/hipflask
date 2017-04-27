"""
Example use: run the below unit tests from parent directory with
$python -m unittest discover tests
"""
from __future__ import absolute_import
import unittest

import json

from hipflask import application


class APIBasicTestCase(unittest.TestCase):

    def setUp(self):
        self.app = application
        self.client = self.app.test_client()
        self.client.testing = True

    def tearDown(self):
        del self.app
        del self.client

    def test_can_pass(self):
        self.assertEqual(2, 2)

    def test_simple_route(self):
        response = self.client.get("/buzz/simple/")
        self.assertEqual(response.status_code, 200)

    def test_get_specific_buzz_item(self):
        # Handle existent item
        response = self.client.get("/buzz/1/")
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data["id"], 1)
        self.assertIsNotNone(json_data["url"])
        self.assertIsNotNone(json_data["pub_date"])

        # Handle non-existent item
        response = self.client.get("/buzz/0/")
        self.assertEqual(response.status_code, 404)
        json_data = json.loads(response.data)
        self.assertRaises(KeyError, lambda: json_data["id"])

    def test_get_list_buzz_items(self):
        # Handle existent items
        response = self.client.get("/buzz/")
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(len(json_data), 3)

        # Search by argument 'urltext' works
        arguments = {"urltext": "google"}
        response = self.client.get("/buzz/", query_string=arguments)
        json_data = json.loads(response.data)
        self.assertIn("google", json_data[0]["url"])
        self.assertEqual(len(json_data), 1)

        # Search by argument 'limit' works
        arguments = {"limit": 2}
        response = self.client.get("/buzz/", query_string=arguments)
        json_data = json.loads(response.data)
        self.assertEqual(len(json_data), 2)

        # Search by arguments 'urltext' and 'limit' works
        arguments = {"urltext": "www", "limit": 1}
        response = self.client.get("/buzz/", query_string=arguments)
        json_data = json.loads(response.data)
        self.assertEqual(len(json_data), 1)
        self.assertIn("www", json_data[0]["url"])


if __name__ == "__main__":
    print("Running unit tests")
    unittest.main()
