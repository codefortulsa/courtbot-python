from datetime import datetime, timedelta
import json

from django.test import RequestFactory, TestCase

from .views import reminders, eligible_jurisdiction, unsubscribe
from alerts.models import Alert
from decouple import config


class testReminders(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _post(self, url, params):
        return self.factory.post(url, params)

    def _get(self, url, params):
        return self.factory.get(url, params)

    # def _delete(self, url):
    #     return self.factory.delete(url)    

    def testReminderWithArraignmentIn8Days(self):
        arraignment_datetime = (datetime.today() + timedelta(days=8)).strftime('%Y-%m-%dT%H:%M:%S')
        request = self._post('/api/reminders', {
            "arraignment_datetime": arraignment_datetime,
            "case_num": 1,
            "phone_num": "+1-918-555-5555",
        })
        response = reminders(request)
        resp_json = json.loads(response.content)
        self.assertEqual(Alert.objects.all().count(), 2)
        self.assertEqual(resp_json['status'], '201 Created')

    def testReminderWithArraignmentIn2Days(self):
        arraignment_datetime = (datetime.today() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%S')
        request = self._post('/api/reminders', {
            "arraignment_datetime": arraignment_datetime,
            "case_num": 2,
            "phone_num": "+1-918-555-5555",
        })
        response = reminders(request)
        resp_json = json.loads(response.content)
        self.assertEqual(Alert.objects.all().count(), 1)
        self.assertEqual(resp_json['status'], '201 Created')

    def testReminderWithArraignmentToday(self):
        arraignment_datetime = datetime.today().strftime('%Y-%m-%dT%H:%M:%S')
        request = self._post('/api/reminders', {
            "arraignment_datetime": arraignment_datetime,
            "case_num": 3,
            "phone_num": "+1-918-555-5555",
        })
        response = reminders(request)
        resp_json = json.loads(response.content)
        self.assertEqual(Alert.objects.all().count(), 0)
        self.assertEqual(resp_json['status'], '410 Gone')

    def testPreventDuplicateReminder(self):
        arraignment_datetime = (datetime.today() + timedelta(days=8)).strftime('%Y-%m-%dT%H:%M:%S')
        request = self._post('/api/reminders', {
            "arraignment_datetime": arraignment_datetime,
            "case_num": 1,
            "phone_num": "+1-918-555-5555",
        })
        response = reminders(request)
        resp_json = json.loads(response.content)
        self.assertEqual(Alert.objects.all().count(), 2)
        self.assertEqual(resp_json['status'], '201 Created')
        reminders(request) # Submitting a duplicate reminder
        self.assertEqual(Alert.objects.all().count(), 2)
        self.assertEqual(resp_json['status'], '201 Created')

    def testEligibleJurisdictions(self):
        request = self._get('/api/eligible_jurisdiction', {
            "state": 'OK'
        })
        response = eligible_jurisdiction(request)
        resp_json = json.loads(response.content)
        print(resp_json)
        self.assertEqual(resp_json, {
            'jurisdiction_type': 'county',
            'eligible_jurisdictions': [
                'adair', 'alfalfa', 'appellate', 'atoka', 'beaver', 'beckham',
                'blaine', 'bryan', 'caddo', 'canadian', 'carter', 'cherokee',
                'choctaw', 'cimarron', 'cleveland', 'coal', 'comanche',
                'cotton', 'craig', 'creek', 'bristow', 'drumright', 'custer',
                'delaware', 'dewey', 'ellis', 'garfield', 'garvin', 'grady',
                'grant', 'greer', 'harmon', 'harper', 'haskell', 'hughes',
                'jackson', 'jefferson', 'johnston', 'kay', 'poncacity',
                'kingfisher', 'kiowa', 'latimer', 'leflore', 'lincoln',
                'logan', 'love', 'major', 'marshall', 'mayes', 'mcclain',
                'mccurtain', 'mcintosh', 'murray', 'muskogee', 'noble',
                'nowata', 'okfuskee', 'oklahoma', 'okmulgee', 'henryetta',
                'osage', 'ottawa', 'payne', 'pawnee', 'pittsburg', 'pontotoc',
                'pottawatomie', 'pushmataha', 'rogermills', 'rogers',
                'seminole', 'sequoyah', 'stephens', 'texas', 'tillman',
                'tulsa', 'wagoner', 'washington', 'washita', 'woods',
                'woodward']})

    def testUnsubscribe(self):
        alert = Alert(
                    when='2020-07-27',
                    to="+1-000-001-0002",
                    what="test reminder"
                )
        alert.save()
        self.assertEqual(Alert.objects.filter(to='+1-000-001-0002').count(), 1)

        request = self._post('api/unsubscribe/000-001-0002', {
            'key': config('SECRET_KEY')
        })
        response = unsubscribe(request, '000-001-0002')
        resp_json = json.loads(response.content)
        message = resp_json.get('message', None)
        self.assertEqual(message, 'Reminders for 000-001-0002 deleted.')
        self.assertEqual(Alert.objects.filter(to='+1-000-001-0002').count(), 0)

    def testUnsubsribeNotExists(self):
        request = self._post('api/unsubscribe/000-001-0003', {
            'key': config('SECRET_KEY')
        })
        response = unsubscribe(request, '000-001-0003')
        resp_json = json.loads(response.content)
        message = resp_json.get('message', None)
        self.assertEqual(message, 'There are no reminders set for 000-001-0003.')
        self.assertEqual(Alert.objects.filter(to='+1-000-001-0003').count(), 0)
