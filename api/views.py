from datetime import datetime, timedelta
import re

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import oscn


@csrf_exempt
def case(request):
    year = request.POST['year']
    county = request.POST['county']
    case_num = request.POST['case_num']

    case = oscn.request.Case(year=year, county=county, number=case_num)
    arraignment_event = find_arraignment_or_return_False(case.events)
    arraignment_datetime = parse_datetime_from_oscn_event_string(
        arraignment_event.Event
    )
    import ipdb; ipdb.set_trace()
    return JsonResponse({
        'case': {
            'type': case.type,
            'year': case.year,
            'county': case.county,
            'number': case.number,
        },
        'arraignment_datetime': arraignment_datetime
    })


@csrf_exempt
def reminders(request):
    case_num = request.POST['case_num']
    phone_num = request.POST['phone_num']
    arraignment_datetime = request.POST['arraignment_datetime']

    week_alert_datetime = arraignment_datetime - timedelta(days=7)
    day_alert_datetime = arraignment_datetime - timedelta(days=1)
    Alert.objects.create(
        when=week_alert_datetime,
        what=f'Arraignment for case {case_num} in 1 week at {arraignment_datetime}',
        to=phone_num
    )
    Alert.objects.create(
        when=day_alert_datetime,
        what=f'Arraignment for case {case_num} in 1 day at {arraignment_datetime}',
        to=phone_num
    )
    return JsonResponse("OK")


def find_arraignment_or_return_False(events):
    for event in events:
        if "arraignment" in event.Docket.lower():
            return event
    return False


def parse_datetime_from_oscn_event_string(event):
    event = event.replace('ARRAIGNMENT', '').rstrip()
    return datetime.strptime(event, "%A, %B %d, %Y at %I:%M %p")
