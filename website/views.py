from django.shortcuts import render, redirect
from datetime import datetime, timedelta
import re

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

import oscn, requests, json


from alerts.models import Alert


def index(request):
    # """View function for home page of site."""

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html')

def check_valid_case(case_num, year, county):
    # Process form data and requests arraignment data form api/case
    resp = requests.get(
        #f"http://127.0.0.1:8000/api/case?year={year}&county={county}&case_num={case_num}"
        f"https://courtbot-python.herokuapp.com/api/case?year={year}&county={county}&case_num={case_num}"
    )
    resp_json = json.loads(resp.content)
    if resp_json.get('error', None):
      return resp_json['error'], None
    return '', resp_json.get('arraignment_datetime', None)


def set_case_reminder(arraignment_datetime, case_num, phone_num):
    #reminder_request = requests.post('http://127.0.0.1:8000/api/reminders', {
    reminder_request = requests.post('https://courtbot-python.herokuapp.com/api/reminders', {
        "arraignment_datetime": arraignment_datetime,
        "case_num": case_num,
        "phone_num": f"+1-{phone_num}"
    })
    resp = json.loads(reminder_request.content)
    if resp.get('error', None):
        return False, resp['error']
    message = f'Text reminder for case {case_num} occuring on {arraignment_datetime} was scheduled under {phone_num}.'
    return True, message


@csrf_exempt
def schedule_reminders(request):
    # If valid case and arraignment time, posts reminder data to api/reminder
    # Includes option for extra phone number for additional recipient
    case_num_list = [ 
            value for key, value in request.POST.items() 
            if key.find("case_num") > -1 and value
        ]
    year = request.POST['year']
    county = request.POST['county']
    phone_num = request.POST['phone_num']
    add_num = request.POST.get('add_phone_num', None)
    for i, case_num in enumerate(case_num_list):
        valid_case_message, arraignment_datetime = check_valid_case(case_num, year, county)
        if not arraignment_datetime:
            messages.error(request, valid_case_message)
            faq_message = (
                f'Please check the case for further information using steps provided at http://court.bot/#faq'
            )
            messages.error(request, faq_message)
        else:
            reminder_set, reminder_message = set_case_reminder(arraignment_datetime, case_num, phone_num)
            # messages.error(request, message)          
            messages.info(request, reminder_message)
            if len(case_num_list)-1 == i and not reminder_set:
                return redirect('/#form')
            if add_num:
                _, another_reminder_message = set_case_reminder(arraignment_datetime, case_num, add_num)
                messages.info(request, another_reminder_message)
    return redirect('/#form')

