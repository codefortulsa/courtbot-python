from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


import oscn
from twilio.twiml.messaging_response import MessagingResponse


@csrf_exempt
def twilio(request):
    resp = MessagingResponse()
    case_num = request.POST['Body']
    case = oscn.request.Case(year='2018', number=case_num)
    for event in case.events:
        if "arraignment" in event.Docket.lower():
            resp.message("The arraignment is %s" % event.Event)
            return HttpResponse(resp)
    resp.message("Could not find arraignment for case %s " % case_num)
    return HttpResponse(resp)
