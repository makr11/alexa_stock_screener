import logging

import boto3

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model.dialog import ConfirmIntentDirective, ElicitSlotDirective
from ask_sdk_model import Response, IntentConfirmationStatus

from api_requests import search_quote, get_quote_data
sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def make_currency(value):
    return round(float(value), 2)


@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    """Handler for Skill Launch."""
    # type: (HandlerInput) -> Response
    speech_text = "Welcome to the Alexa Stock Screener!"

    return handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("Hello World", speech_text)).set_should_end_session(
        False).response


@sb.request_handler(can_handle_func=is_intent_name("PricesIntent"))
def launch_request_handler(handler_input):
    request = handler_input.request_envelope.request
    session_attributes = handler_input.attributes_manager.session_attributes
    stock = request.intent.slots["stock"].value
    
    if request.intent.confirmation_status==IntentConfirmationStatus.CONFIRMED:
        quote_data = session_attributes["quote_data"]
        quote_info = session_attributes["quote_info"]
        currency = quote_info['8. currency']
        speech_text = (f"{quote_info['2. name']} "
                        f"opening price is {make_currency(quote_data['02. open'])} {currency}, "
                        f"highest price is {make_currency(quote_data['03. high'])} {currency}")
        
        return handler_input.response_builder.speak(speech_text).response
    
    elif request.intent.confirmation_status==IntentConfirmationStatus.DENIED:
        return handler_input.response_builder.set_should_end_session(False).response
    
    matches = search_quote(stock.lower())
    
    if not matches:
        speech_text = f"I haven't found any information for {stock}. Please repeat or try with another stock."
        
        return handler_input.response_builder.speak(speech_text).add_directive(ElicitSlotDirective(slot_to_elicit="stock")).response
        
    elif matches and request.intent.confirmation_status==IntentConfirmationStatus.NONE:
        print("before")
        client = boto3.client('ssm')
        response = client.send_command(
            InstanceIds=['i-0ebdd2b77dacea11f'],
            DocumentName="AWS-RunShellScript",
            Parameters={
                'commands': [
                    "#!/bin/bash",
                    "cd /home/ubuntu/stock_screener/bin",
                    "source ./activate",
                    "cd ./stock_screener_script",
                    "echo $(ls)",
                    "python alpha_vantage_api.py create-table AMZN",
                    "deactivate"
                ]
            }
        )
        print(after)
        quote_data = get_quote_data(matches[0]['1. symbol'])
        quote_info = matches[0]
        if not quote_data:
            quote_data = get_quote_data(matches[1]['1. symbol'])
            quote_info = matches[1]
        speech_text = (f"Current price of {quote_info['2. name']} "
                        f"is {make_currency(quote_data['05. price'])} {quote_info['8. currency']}, "
                        f"last traded on {quote_data['07. latest trading day']}. "
                        "Would you like more informations?")
        session_attributes["quote_data"] = quote_data
        session_attributes["quote_info"] = quote_info
        
        return handler_input.response_builder.speak(speech_text).add_directive(ConfirmIntentDirective()).response
    

@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    """Handler for Help Intent."""
    # type: (HandlerInput) -> Response
    speech_text = "You can say hello to me!"

    return handler_input.response_builder.speak(speech_text).ask(
        speech_text).set_card(SimpleCard(
            "Hello World", speech_text)).response


@sb.request_handler(
    can_handle_func=lambda handler_input:
        is_intent_name("AMAZON.CancelIntent")(handler_input) or
        is_intent_name("AMAZON.StopIntent")(handler_input))
def cancel_and_stop_intent_handler(handler_input):
    """Single handler for Cancel and Stop Intent."""
    # type: (HandlerInput) -> Response
    speech_text = "Goodbye!"

    return handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("Hello World", speech_text)).response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallbackIntent"))
def fallback_handler(handler_input):
    """AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    # type: (HandlerInput) -> Response
    speech = (
        "The Hello World skill can't help you with that.  "
        "You can say hello!!")
    reprompt = "You can say hello!!"
    handler_input.response_builder.speak(speech).ask(reprompt)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_request_handler(handler_input):
    """Handler for Session End."""
    # type: (HandlerInput) -> Response
    return handler_input.response_builder.response


@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    # type: (HandlerInput, Exception) -> Response
    logger.error(exception, exc_info=True)

    speech = "Sorry, there was some problem. Please try again!!"
    handler_input.response_builder.speak(speech).ask(speech)

    return handler_input.response_builder.response


handler = sb.lambda_handler()
