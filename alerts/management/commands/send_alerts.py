from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from ...models import Alert

from twilio.rest import Client
from decouple import config

TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN')
TWILIO_FROM_NUMBER = config('TWILIO_FROM_NUMBER')


class Command(BaseCommand):
    help = 'Sends un-sent alerts for the current hour'

    def handle(self, *args, **options):
        unsent_alerts = Alert.objects.filter(sent=False, when=datetime.today())
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        for unsent_alert in unsent_alerts:
            message = client.messages.create(
                    to=str(unsent_alert.to),
                    from_="+19189134069",
                    body=unsent_alert.what)
            unsent_alert.sent = True
            unsent_alert.save()
