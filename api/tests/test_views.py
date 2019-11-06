from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse

from api.views import reminders, case


class caseViewTest(TestCase):
    def setUp(self):
        self.url = reverse('case')
        self.factory = RequestFactory()

    def test_case(self):
        params = {
            "year": "2014",
            "county":"tulsa",
            "case_num": "5203"
        }
        request = self.factory.get(self.url, params)
        response = case(request)
        self.assertEqual(response.status_code, 200)


class remindersViewTest(TestCase):
    def setUp(self):
        self.url = reverse('reminders')
        self.factory = RequestFactory()

    def test_reminders(self):
        params = {
            "case_num": "CF-2014-5203",
            "phone_num":"19182615259",
            "arraignment_datetime": "2019-09-17T08:00:00"
        }
        request = self.factory.post(self.url, params)
        response = reminders(request)
        self.assertEqual(response.status_code, 201)
