"""
Example use: run the below unit tests from parent directory with
$python -m unittest discover tests
"""
from __future__ import absolute_import
from io import BytesIO
import datetime

import unittest
import json
import pandas

from hipflask import (
    application, transform_companies_data
)


class APIBasicTest(unittest.TestCase):

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

    def test_post_buzz_simple_increments_redis_counter(self):
        response = self.client.post("/buzz/simple/", data=dict(foo="bar"))
        json_data = json.loads(response.data)
        self.assertGreater(json_data["counter"], 1)


class Request():
    """ For fake request """
    def __init__(self):
        self.form = {}


class CompaniesTest(unittest.TestCase):
    """ Test daily companies """
    def setUp(self):
        self.app = application
        self.client = self.app.test_client()
        self.client.testing = True


    def tearDown(self):
        del self.app
        del self.client

    def test_get_transform_daily_company_files_route(self):
        response = self.client.get("/companies/")
        self.assertEqual(response.status_code, 200)

    def test_transform_file_upload_with_no_files_reroutes_correctly(self):
        response = self.client.post(
            "/companies/", content_type="multipart/form-data", data={}
        )
        self.assertEqual(response.status_code, 302)

    def test_validate_file_upload_one_file_redirects(self):
        response = self.client.post(
            "/companies/", data = {
                "file": (BytesIO("stuff in file"), "daily.csv"),
            }
        )
        self.assertEqual(response.status_code, 302)

    def test_transform_companies_data_success(self):
        mock_companies_data = pandas.read_csv("static/test_files/companies.csv")
        mock_daily_data = pandas.read_csv("static/test_files/daily.csv")
        mock_data = {
            "error": False,
            "message": None,
            "dfs": {
                "companies": mock_companies_data,
                "daily": mock_daily_data
            }
        }
        mock_form = {
            "start_date": "",
            "end_date": "",
            "n":""
        }
        fake_request = Request()
        fake_request.form = mock_form
        response = transform_companies_data(fake_request, mock_data)
        self.assertIsNotNone(response["dfs"]["merged"])
        self.assertEqual(len(response["dfs"]["merged"]), 30) # all records

        #filtering by start and end date works
        mock_form = {
            "start_date": "2017-1-3",
            "end_date": "2017-1-8",
            "n":""
        }
        fake_request.form = mock_form
        response = transform_companies_data(fake_request, mock_data)
        self.assertEqual(min(response["dfs"]["merged"]["date"]),
                         datetime.datetime(2017, 1, 3))
        self.assertEqual(max(response["dfs"]["merged"]["date"]),
                         datetime.datetime(2017, 1, 8))


if __name__ == "__main__":
    print("Running unit tests")
    unittest.main()
