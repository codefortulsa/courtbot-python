# courtbot-python
This is an experimental reimplementation of courtbot using python. It uses the
[oscn](https://pypi.org/project/oscn/) PyPI library and twilio.

## Development
### Requirements
* python
* A twilio account
* PostgreSQL

### Install & Set up locally
1. `pip install -r requirements.txt` (if you get an error, make sure `postgresql` is installed, then add the folder containing pg_config to your path `export PATH=”/usr/local/bin:/Library/PostgreSQL/9.6/bin:$PATH”`)
2. `cp .env-dist .env` and put your own values into `.env`
3. `python manage.py runserver`


### Use ngrok to test twilio callbacks
To test twilio callbacks, run ngrok to set up a public domain for your
localhost:8000 ...

`ngrok http 8000`

... then use the public domain url for your number's Messaging "a messages
comes in" webhook. E.g., http://34ae567a.ngrok.io/sms/twilio

Note: super annoying, but every time you restart ngrok you'll have to update
your twilio number's messaging webhook again, and you'll need to change your
`ALLOWED_HOSTS` to include the new ngrok host.  Unless you pay for ngrok.
