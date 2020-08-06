from django.test import TestCase, RequestFactory, Client
import unittest
from unittest.mock import patch
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
                "phone_num": "000-000-0000",
                "add_phone_num": "000-000-0001"
        }
        resp = self.client.post("https://courtbot-python.herokuapp.com/schedule_reminders", data=data, follow=True)

        self.assertIn(str.encode("Arraignment for case CF-2020-1648 has already passed"), resp.content)

    def test_form_data_view_not_found(self):
        data = {
                "case_num": "1000000000",
                "year": 2020,
                "county": "Tulsa",
                "phone_num": "000-000-0000",
                "add_phone_num": "000-000-0001"
        }
        resp = self.client.post("https://courtbot-python.herokuapp.com/schedule_reminders", data=data, follow=True)

        self.assertIn(str.encode("Unable to find arraignment event with the following year 2020, county Tulsa, case number 1000000000"), resp.content)

    @patch('website.views.check_valid_case')
    def test_form_data_view_scheduled(self, mock_arraignment):
       
        mock_arraignment.return_value = '','2020-08-13T09:00:00'
        data = {
                "case_num": "CF-0000-0001",
                "year": 2020,
                "county": "Tulsa",
                "phone_num": "000-000-0000",
                "add_phone_num": "000-000-0001"
        }
        resp = self.client.post("https://courtbot-python.herokuapp.com/schedule_reminders", data=data, follow=True)

        self.assertIn(str.encode("Text reminder for case CF-0000-0001 occuring on 2020-08-13T09:00:00 was scheduled under 000-000-0000."), resp.content)