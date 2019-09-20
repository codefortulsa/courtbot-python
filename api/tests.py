from django.test import TestCase
from api.views import reminders
from ast import literal_eval
from datetime import datetime, timedelta
from alerts.models import Alert

class testReminders(TestCase):
    class Req():
        def __init__(self, arraignment_datetime, case_num, phone_num):
            self.POST = {
                "arraignment_datetime": arraignment_datetime,
                "case_num": case_num,
                "phone_num": phone_num
            }


    def testReminderWithArraignmentIn8Days(self):
        arraignment_datetime = (datetime.today() + timedelta(days=8)).strftime('%Y-%m-%dT%H:%M:%S')
        request = self.Req(
            arraignment_datetime,
            1,
            "+1-918-555-5555"
        )
        result = reminders(request)
        response = literal_eval(result.content.decode('utf-8'))
        self.assertEqual(Alert.objects.all().count(), 2)
        self.assertEqual(response['status'], '201 Created') 


    def testReminderWithArraignmentIn2Days(self):
        arraignment_datetime = (datetime.today() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%S')
        request = self.Req(
            arraignment_datetime,
            2,
            "+1-918-555-5555"
        )
        result = reminders(request)
        response = literal_eval(result.content.decode('utf-8'))
        self.assertEqual(Alert.objects.all().count(), 1)
        self.assertEqual(response['status'], '201 Created') 


    def testReminderWithArraignmentToday(self):
        arraignment_datetime = datetime.today().strftime('%Y-%m-%dT%H:%M:%S')
        request = self.Req(
            arraignment_datetime,
            3,
            "+1-918-555-5555"
        )
        result = reminders(request)
        response = literal_eval(result.content.decode('utf-8'))
        self.assertEqual(Alert.objects.all().count(), 0)
        self.assertEqual(response['status'], '410 Gone') 
        