from datetime import datetime, timedelta

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import oscn
from twilio.twiml.messaging_response import MessagingResponse

from alerts.models import Alert


@csrf_exempt
def twilio(request):
    resp = MessagingResponse()
    case_num = request.POST['Body']
    from_phone = request.POST['From']
    # FIXME: no county defaults to Tulsa
    case = oscn.request.Case(year='2018', number=case_num)
    arraignment_event = find_arraignment_or_return_False(case.events)
    if not arraignment_event:
        resp.message(f'Could not find arraignment for case {case_num}')
    else:
        arraignment_datetime = parse_datetime_from_oscn_event_string(
            arraignment_event.Event
        )
        week_alert_datetime = arraignment_datetime - timedelta(days=7)
        day_alert_datetime = arraignment_datetime - timedelta(days=1)
        Alert.objects.create(
            when=week_alert_datetime,
            what=f'Arraignment for case {case_num} in 1 week at {arraignment_datetime}',
            to=from_phone
        )
        Alert.objects.create(
            when=day_alert_datetime,
            what=f'Arraignment for case {case_num} in 1 day at {arraignment_datetime}',
            to=from_phone
        )
        resp.message(f'I will send you a reminder on {week_alert_datetime} and on {day_alert_datetime}')
    return HttpResponse(resp)


def find_arraignment_or_return_False(events):
    for event in events:
        if "arraignment" in event.Docket.lower():
            return event
    return False


def parse_datetime_from_oscn_event_string(event):
    event = event.replace('ARRAIGNMENT', '').rstrip()
    return datetime.strptime(event, "%A, %B %d, %Y at %I:%M %p")
