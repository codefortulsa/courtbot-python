from datetime import datetime

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
    # FIXME: no county defaults to Tulsa
    case = oscn.request.Case(year='2018', number=case_num)
    arraignment_event = find_arraignment_or_return_False(case.events)
    if not arraignment_event:
        resp.message(f'Could not find arraignment for case {case_num}')
    else:
        arraignment_datetime = parse_datetime_from_oscn_event_string(
            arraignment_event.Event
        )
        # Alert.objects.create()
        resp.message(f'The arraignment is {arraignment_event.Event}')
    return HttpResponse(resp)


def find_arraignment_or_return_False(events):
    for event in events:
        if "arraignment" in event.Docket.lower():
            return event
    return False


def parse_datetime_from_oscn_event_string(event):
    event = event.replace('ARRAIGNMENT', '').rstrip()
    return datetime.strptime(event, "%A, %B %d, %Y at %I:%M %p")
