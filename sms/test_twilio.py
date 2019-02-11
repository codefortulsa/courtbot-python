from decouple import config
from twilio.rest import Client


TWILIO_ACCOUNT_SID=config('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN=config('TWILIO_AUTH_TOKEN')
TWILIO_FROM_NUMBER=config('TWILIO_FROM_NUMBER')
TWILIO_TO_NUMBER=config('TWILIO_TO_NUMBER')


twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


message = twilio_client.messages.create(
    body='Hello',
    from_=TWILIO_FROM_NUMBER,
    to=TWILIO_TO_NUMBER
)

print(message.sid)
