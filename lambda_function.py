"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages orders for flowers.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'OrderFlowers' template.

For instructions on how to set up and test this bot, as well as additional samples,
visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.

20190604 : seyeon : Initial validations for year, county, and case number
"""
import dateutil.parser
import time
import os
import logging

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
    counties = ['Tulsa', 'Rogers', 'Muskogee']
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
    year_range = 5
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

def validate_case_number(case_number):
    # call the endpoint for validating case number
    message = None
    return True, None, message


def validate_case_info(county, year, case_number):
    is_valid, slot, message = validate_eligible_county(county)
    if not is_valid:
        return build_validation_result(is_valid, slot, message)

    if year is not None:
        is_valid, slot, message = validate_year(year)
        if not is_valid:
            return build_validation_result(is_valid, slot, message)

    if case_number is not None:
        is_valid, slot, message = validate_case_number(case_number)
        if not is_valid:
            return build_validation_result(is_valid, slot, message)

    return build_validation_result(True, None, None)


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
    source = intent_request['invocationSource']

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)

        validation_result = validate_case_info(county, year, case_number)
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
        if case_number is not None:
            output_session_attributes['CaseID'] = case_number

        return delegate(output_session_attributes, get_slots(intent_request))

    # Order the flowers, and rely on the goodbye message of the bot to define the message to the end user.
    # In a real bot, this would likely involve a call to a backend service.
    success_message = ('Thank you for using Courtbot. '
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
