from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from ...models import Alert


class Command(BaseCommand):
    help = 'Sends un-sent alerts for the current hour'

    def handle(self, *args, **options):
        unsent_alerts = Alert.objects.filter(sent=False,when=datetime.today())
        for unsent_alert in unsent_alerts:
            pass
