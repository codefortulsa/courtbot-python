from datetime import datetime
from django.test import TestCase
from sms.views import twilio
from .views import (
    find_arraignment_or_return_False, parse_datetime_from_oscn_event_string
)


class SmsTestCase(TestCase):
    class Req():
        def __init__(self, case_num, phone_num):
            self.POST = {
                "Body": case_num,
                "From": phone_num
            }


    def testSMSReminder(self):
        request = self.Req(
            "CF-2019-10",
            "+1-405-555-1234"
        )
        result = twilio(request)
        self.assertEqual(result.status_code, 200) 


    def test_parse_datetime_from_oscn_event_string(self):
        test_string = "Monday, June 4, 2018 at 9:00 AM ARRAIGNMENT"
        parsed_datetime = parse_datetime_from_oscn_event_string(test_string)
        self.assertEqual(parsed_datetime, datetime(2018, 6, 4, 9, 0))

        test_string = "Tuesday, June 5, 2018 at 02:00 PM ARRAIGNMENT"
        parsed_datetime = parse_datetime_from_oscn_event_string(test_string)
        self.assertEqual(parsed_datetime, datetime(2018, 6, 5, 14, 0))
