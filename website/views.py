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

def unsubscribe(request):
    return render(request, )    

def check_valid_case(request):
    # Process form data and requests arraignment data form api/case
    case_num = request.POST['case_num']
    year = request.POST['year']
    county = request.POST['county']
    phone_num = request.POST['phone_num']
    add_num = request.POST['add_phone_num']
    resp = requests.get(
        f"https://courtbot-python.herokuapp.com/api/case?year={year}&county={county}&case_num={case_num}"
    )
    resp_json = json.loads(resp.content)
    if resp_json.get('error', None):
      return resp_json['error'], None
    return '', resp_json.get('arraignment_datetime', None)


def set_case_reminder(arraignment_datetime, case_num, phone_num):
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
    case_num = request.POST['case_num']
    phone_num = request.POST['phone_num']
    add_num = request.POST.get('add_phone_num', None)

    valid_case_message, arraignment_datetime = check_valid_case(request)
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
        if not reminder_set:
        	return redirect('/#form')
        if add_num:
          _, another_reminder_message = set_case_reminder(arraignment_datetime, case_num, add_num)
          messages.info(request, another_reminder_message)
 
    return redirect('/#form')

@csrf_exempt
def unsubscribe_reminders(request):
    # Remove reminders associated with phone number
    phone = request.POST['remove_phone_num']
    remove_request = requests.delete(f"http://localhost:8000/api/unsubscribe/{phone}")
    resp = json.loads(remove_request.content)
    messages.info(request, resp.get('message', None), extra_tags='unsubscribe')
    return redirect('/')