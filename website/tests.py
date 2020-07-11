from django.test import TestCase, RequestFactory, Client
import json

class testFormViews(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

    def test_form_data_view_passed(self):
        data = {
                "case_num": "CF-2020-1648",
                "year": 2020,
                "county": "Tulsa",
                "phone_num": 918-555-5555,
                "add_phone_num": 918-111-1111
        }
        resp = self.client.post("https://courtbot-python.herokuapp.com/form_data", data=data, follow=True)

        self.assertIn(str.encode("Arraignment for case CF-2020-1648 has already passed"), resp.content)

    def test_form_data_view_not_found(self):
        data = {
                "case_num": "1000000000",
                "year": 2020,
                "county": "Tulsa",
                "phone_num": 918-555-5555,
                "add_phone_num": 918-111-1111
        }
        resp = self.client.post("https://courtbot-python.herokuapp.com/form_data", data=data, follow=True)

        self.assertIn(str.encode("Unable to find arraignment event with the following year 2020, county Tulsa, case number 1000000000"), resp.content)

    def test_form_data_view_scheduled(self):
        data = {
                "case_num": "CF-2020-2803",
                "year": 2020,
                "county": "Tulsa",
                "phone_num": 918-555-5555,
                "add_phone_num": 918-111-1111
        }
        resp = self.client.post("https://courtbot-python.herokuapp.com/form_data", data=data, follow=True)

        self.assertIn(str.encode("Reminder scheduled"), resp.content)

