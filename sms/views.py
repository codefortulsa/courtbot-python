from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


from twilio.twiml.messaging_response import MessagingResponse


@csrf_exempt
def twilio(request):
    resp = MessagingResponse()
    resp.message("Thanks for the message")

    return HttpResponse(resp)
