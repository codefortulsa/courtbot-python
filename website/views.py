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

@csrf_exempt
def form_data(request):
    # Processes form data, requests arraignment data from api/case, and posts reminder data to api/reminder
    # Includes option for extra phone number for additional recipient
    case_num = request.POST['case_num']
    year = request.POST['year']
    county = request.POST['county']
    phone_num = request.POST['phone_num']
    add_num = request.POST['add_phone_num']
    response = requests.get(
        f"https://courtbot-python.herokuapp.com/api/case?year={year}&county={county}&case_num={case_num}"
    )
    resp_json = json.loads(response.content)

    if resp_json.get('error', None):
        message = resp_json['error']
        messages.error(request, message)
    else:
        arraignment_datetime = resp_json.get('arraignment_datetime', None)
        reminder_request = requests.post('https://courtbot-python.herokuapp.com/api/reminders', {
            "arraignment_datetime": arraignment_datetime,
            "case_num": case_num,
            "phone_num": f"+1-{phone_num}"
        })
        resp_json = json.loads(reminder_request.content)
        if resp_json.get('error', None):
            message = resp_json['error']
            messages.error(request, message)
        else:
            message = "Reminder scheduled!"
            messages.success(request, message)
        if add_num:
            additional_request = requests.post('https://courtbot-python.herokuapp.com/api/reminders', {
                "arraignment_datetime": arraignment_datetime,
                "case_num": case_num,
                "phone_num": f"+1-{add_num}"
        })

    return redirect('index')
