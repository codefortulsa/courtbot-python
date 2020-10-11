from datetime import datetime, timedelta
import re

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import oscn


from alerts.models import Alert


@csrf_exempt
def case(request):
    year_regex = re.compile(r'^[0-9]{4}$')
    this_year = datetime.today().year
    
    if request.method == 'GET':
        year = request.GET.get('year', 'NOT PROVIDED')
        county = request.GET.get('county', 'NOT PROVIDED')
        case_num = request.GET.get('case_num', 'NOT PROVIDED')

        if not year_regex.match(year) or int(year) > this_year or int(year) < 1900:
            err_msg = (
                f'invalid year: {year}')
            return JsonResponse({'error': err_msg})
        try:
            case = oscn.request.Case(year=year, county=county, number=case_num)
        except Exception as exc:
            print(exc)
            err_msg = (
                f'Unable to find case with the following information: '
                f'year {year}, county {county}, case number {case_num}')
            return JsonResponse({'error': err_msg})

        arraignment_event = find_arraignment_or_return_False(case.events)
        if not arraignment_event:
            err_msg = (
                f'Unable to find arraignment event with the following '
                f'year {year}, county {county}, case number {case_num}')
            return JsonResponse({'error': err_msg})
        arraignment_datetime = parse_datetime_from_oscn_event_string(
            arraignment_event.Event
        )

        return JsonResponse({
            'case': {
                'type': case.type,
                'year': case.year,
                'county': case.county,
                'number': case.number,
            },
            'arraignment_datetime': arraignment_datetime
        })
    return HttpResponse(status=405)


@csrf_exempt
def reminders(request):
    case_num = request.POST['case_num']
    phone_num = request.POST['phone_num']
    arraignment_datetime = datetime.strptime(
        request.POST['arraignment_datetime'], "%Y-%m-%dT%H:%M:%S"
    )

    week_alert_datetime = arraignment_datetime - timedelta(days=7)
    day_alert_datetime = arraignment_datetime - timedelta(days=1)
    message = {
        "status":"201 Created"
    }
    if week_alert_datetime > datetime.today():
        Alert.objects.get_or_create(
            when=week_alert_datetime,
            what=f'Arraignment for case {case_num} in 1 week at {arraignment_datetime}',
            to=phone_num
        )
        message['week_before_datetime'] = week_alert_datetime
    if day_alert_datetime > datetime.today():
        Alert.objects.get_or_create(
            when=day_alert_datetime,
            what=f'Arraignment for case {case_num} in 1 day at {arraignment_datetime}',
            to=phone_num
        )
        message['day_before_datetime'] = day_alert_datetime
        return JsonResponse(message, status=201)
    else:
        return JsonResponse({
            "status":"410 Gone", #https://www.codetinkerer.com/2015/12/04/choosing-an-http-status-code.html
            "error":f'Arraignment for case {case_num} has already passed'
        }, status=410)


@csrf_exempt
def eligible_jurisdiction(request):
    if request.method == 'GET':
        state = request.GET.get('state', 'NOT PROVIDED')

        if state == 'OK':
            jurisdiction_type = 'county'
            eligible_jurisdictions = oscn.counties
            return JsonResponse({
                'jurisdiction_type': jurisdiction_type,
                'eligible_jurisdictions': eligible_jurisdictions,
            })
        else:
            err_msg = (
                f'That eligible jurisdiction list is not available  '
                f'at this time.')
            return JsonResponse({'error': err_msg})

    return HttpResponse(status=405)


def find_arraignment_or_return_False(events):
    for event in events:
        if "arraignment" in event.Docket.lower():
            return event
    return False


def parse_datetime_from_oscn_event_string(event):
    event = event.replace('ARRAIGNMENT', '').rstrip()
    return datetime.strptime(event, "%A, %B %d, %Y at %I:%M %p")
