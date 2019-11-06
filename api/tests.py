from ast import literal_eval
from datetime import datetime, timedelta

from django.test import RequestFactory, TestCase

from .views import reminders
from alerts.models import Alert


class testReminders(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _post(self, url, params):
        return self.factory.post(url, params)

    def testReminderWithArraignmentIn8Days(self):
        arraignment_datetime = (datetime.today() + timedelta(days=8)).strftime('%Y-%m-%dT%H:%M:%S')
        request = self._post('/api/reminders', {
            "arraignment_datetime": arraignment_datetime,
            "case_num": 1,
            "phone_num": "+1-918-555-5555",
        })
        result = reminders(request)
        response = literal_eval(result.content.decode('utf-8'))
        self.assertEqual(Alert.objects.all().count(), 2)
        self.assertEqual(response['status'], '201 Created')


    def testReminderWithArraignmentIn2Days(self):
        arraignment_datetime = (datetime.today() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%S')
        request = self._post('/api/reminders', {
            "arraignment_datetime": arraignment_datetime,
            "case_num": 2,
            "phone_num": "+1-918-555-5555",
        })
        result = reminders(request)
        response = literal_eval(result.content.decode('utf-8'))
        self.assertEqual(Alert.objects.all().count(), 1)
        self.assertEqual(response['status'], '201 Created')


    def testReminderWithArraignmentToday(self):
        arraignment_datetime = datetime.today().strftime('%Y-%m-%dT%H:%M:%S')
        request = self._post('/api/reminders', {
            "arraignment_datetime": arraignment_datetime,
            "case_num": 3,
            "phone_num": "+1-918-555-5555",
        })
        result = reminders(request)
        response = literal_eval(result.content.decode('utf-8'))
        self.assertEqual(Alert.objects.all().count(), 0)
        self.assertEqual(response['status'], '410 Gone')
