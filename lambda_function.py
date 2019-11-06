"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages orders for flowers.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'OrderFlowers' template.

For instructions on how to set up and test this bot, as well as additional samples,
visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.

20190604 : seyeon : Initial validations for year, county, and case number
20190713 : seyeon : Added GET call to courtbot-python herokuapp
"""
import datetime
import dateutil.parser
import json
import logging
import os
import re
import urllib.request
import time


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }

def confirm_slot(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message
        }
    }

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False

def validate_eligible_county(county):
    counties = ['Tulsa', 'Rogers', 'Muskogee', 'Wagoner']
    normalized_counties = []
    for eligible_county in counties:
        normalized_counties.append(eligible_county.lower())
    if county is not None and county.lower() not in normalized_counties:
        eligible_counties = ', '.join(str(c) for c in counties)
        message = ('We do not have {0} as a serviceable area, '
                   'would you like to look up case from one of our eligible '
                   'counties? Counties we currently service are: {1}'.format(
                        county, eligible_counties))
        return False, 'County', message
    return True, None, None

def validate_year(year):
    message = None
    year_range = 15
    valid_year = 0
    try:
        valid_year = int(year)
    except ValueError:
        message = ('Please enter the year as a 4 digit number, such as 2019. '
                   'What year is the case in?')
        return False, 'Year', message
    if len(year) != 4:
        message = ('Please enter the year as a 4 digit number, such as 2019. '
                   'What year is the case in?')
        return False, 'Year', message
    if abs(valid_year - 2019) > year_range:
        # range in which cases are searchable
        message = ('Unfortunately we cannot look up cases older or later than '
                   '{0} years. Would you like to look up a case between the '
                   '{0} years in the past or future?'.format(year_range))
        return False, 'Year', message
    return True, None, message

def validate_case_number(county, year, case_number, intent_request):
    regex = '\w{2,}-\w{4}-\w{1,}$'
    if not re.match(regex, case_number):
        message = 'Please enter the case number formatted like CF-2019-1234'
        return False, 'CaseID', message

    # call the endpoint for validating case number
    courtbot_url = (f'http://courtbot-python.herokuapp.com/api/case?'
        f'county={county}&year={year}&case_num={case_number}')
    # response = requests.get(url=courtbot_url)
    response = urllib.request.urlopen(courtbot_url)
    case_info = json.load(response)
    message = None
    if 'arraignment_datetime' in case_info:
        event_date = case_info.get('arraignment_datetime')
        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
        output_session_attributes['event_date'] = event_date
        output_session_attributes['case_id'] = case_number
        event_date = datetime.datetime.strptime(
            event_date, '%Y-%m-%dT%H:%M:%S')
        message = f'You have an event coming up at {event_date}. Would you like to set a reminder?'
    else:
        message = case_info.get('error')
        return False, 'CaseID', message
    return True, None, message

def validate_reminder(reminder, intent_request):
    bool_reminder = None
    message = ''
    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    if reminder.lower() in ['y', 'yes']:
        bool_reminder = True
    elif reminder.lower() in ['n', 'no']:
        bool_reminder = False
    else:
        message = 'Please enter "y" or "yes" to setup a reminder.'
        return False, 'Reminder', message

    # if intent_request.get('requestAttributes') and intent_request['requestAttributes'].get('x-amz-lex:user-id'):
    #     phone_num = intent_request['requestAttributes']['x-amz-lex:user-id']
    #     output_session_attributes = intent_request['sessionAttributes']
    #     output_session_attributes['phone_num'] = phone_num
    # else:
    #     message = 'We were unable to get your number.'
    #     phone_num = '1234567890'
        # return False, 'Reminder', message

    return True, None, message

def validate_phone_num(phone_num, intent_request):
    num_list = phone_num.split('-')
    num_str = '1' + ''.join(num_list)
    if len(num_str) != 11:
        message = 'Please enter a phone number formatted like 516-111-2222'
        return False, 'PhoneNumber', message

    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    case_id = output_session_attributes['case_id']
    event_date = output_session_attributes['event_date']
    courtbot_url = f'http://courtbot-python.herokuapp.com/api/reminders'
    reminder_data = (f'case_num={case_id}&phone_num={phone_num}&'
                     f'arraignment_datetime={event_date}'
                    ).encode(encoding='UTF-8')
    response = urllib.request.urlopen(courtbot_url, data=reminder_data)
    reminder_info = json.load(response)
    if 'week_before_datetime' in reminder_info:
        week_before_datetime = reminder_info.get('week_before_datetime')
        day_before_datetime = reminder_info.get('day_before_datetime')
        output_session_attributes['week_before_datetime'] = week_before_datetime
        output_session_attributes['day_before_datetime'] = day_before_datetime
        output_session_attributes['confirm_reminder'] = True
        output_session_attributes['phone_num'] = num_str
        message = (
            f'We will send you a reminder text on {week_before_datetime} '
            f'and {week_before_datetime}.')
        return True, None, message
    message = 'Something was wrong while setting up the reminder.'
    return False, 'PhoneNumber', message

def validate_case_info(
        county, year, case_number, reminder, phone_num, intent_request):
    is_valid, slot, message = validate_eligible_county(county)
    if not is_valid:
        return build_validation_result(is_valid, slot, message)

    if year is not None:
        is_valid, slot, message = validate_year(year)
        if not is_valid:
            return build_validation_result(is_valid, slot, message)

    if case_number is not None:
        is_valid, slot, message = validate_case_number(
            county, year, case_number, intent_request)
        if not is_valid:
            return build_validation_result(is_valid, slot, message)
        # return build_validation_result(is_valid, slot, message)

    if reminder is not None:
        is_valid, slot, message = validate_reminder(reminder, intent_request)
        if not is_valid:
            return build_validation_result(is_valid, slot, message)

    if phone_num is not None:
        is_valid, slot, message = validate_phone_num(phone_num, intent_request)
        if not is_valid:
            return build_validation_result(is_valid, slot, message)
    return build_validation_result(True, None, message)


""" --- Functions that control the bot's behavior --- """


def get_case_info(intent_request):
    """
    Performs dialog management and fulfillment for ordering flowers.
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """

    county = get_slots(intent_request)["County"]
    year = get_slots(intent_request)["Year"]
    case_number = get_slots(intent_request)["CaseID"]
    reminder = get_slots(intent_request)["Reminder"]
    phone_number = get_slots(intent_request)["PhoneNumber"]
    source = intent_request['invocationSource']

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)

        validation_result = validate_case_info(
            county, year, case_number, reminder, phone_number, intent_request)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        # Pass the price of the flowers back through session attributes to be used in various prompts defined
        # on the bot model.
        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
        # if case_number is not None and not output_session_attributes.get('case_id'):
        #     output_session_attributes['case_id'] = case_number
        #     return confirm_slot(intent_request['sessionAttributes'],
        #                        intent_request['currentIntent']['name'],
        #                        slots,
        #                        validation_result['message'])
        return delegate(output_session_attributes, get_slots(intent_request))

    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    week_before_datetime = output_session_attributes['week_before_datetime']
    day_before_datetime = output_session_attributes['day_before_datetime']
    phone_num = output_session_attributes.get('phone_num', 'NO NUMBER FOUND')
    success_message = (f'You will get a text on {week_before_datetime} and {day_before_datetime} on the number {phone_num}. '
                        'Thank you for using Courtbot. '
                        'For any comments or concerns contact us at '
                        'https://www.okcourtbot.com/#faq')
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText', 'content': success_message})


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'GetCaseInfo':
        return get_case_info(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
