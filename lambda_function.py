
import random
import logging
import boto3
import json
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response

# Presetting Responses for Alexa to give in different Situations
SKILL_NAME = "Turn on Fan"
HELP_MESSAGE = "You can say turn on the fan, or, you can say exit... What can I help you with?"
HELP_REPROMPT = "What can I help you with?"
STOP_MESSAGE = "Goodbye!"
FALLBACK_MESSAGE = "The fan skill can't help you with that.  It can turn on and off your fan. What can I help you with?"
FALLBACK_REPROMPT = 'What can I help you with?'
EXCEPTION_MESSAGE = "Sorry. I cannot help you with that."


sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Handler For Turning On Fan
class TurnOnFanHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_request_type("LaunchRequest")(handler_input) or
                is_intent_name("TurnOnFanIntent")(handler_input))

    def handle(self, handler_input):
        logger.info("In TurnOnFanHandler")

        client = boto3.client('iot-data', region_name='us-east-1')

        response = client.publish(
            topic='esp32/sub',
            qos=1,
            payload=json.dumps({"message":"on"})
        )

        handler_input.response_builder.speak("ok")
        return handler_input.response_builder.response
        
        
# Handler for Turning Off Fan
class TurnOffFanHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_request_type("LaunchRequest")(handler_input) or
                is_intent_name("TurnOffFanIntent")(handler_input))

    def handle(self, handler_input):
        logger.info("In TurnOffFanHandler")

        client = boto3.client('iot-data', region_name='us-east-1')

        response = client.publish(
            topic='esp32/sub',
            qos=1,
            payload=json.dumps({"message":"off"})
        )
        
        handler_input.response_builder.speak("ok")
        return handler_input.response_builder.response

# Handler For Help Intent
class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In HelpIntentHandler")

        handler_input.response_builder.speak(HELP_MESSAGE).ask(
            HELP_REPROMPT).set_card(SimpleCard(
                SKILL_NAME, HELP_MESSAGE))
        return handler_input.response_builder.response

# Handler for Stopping Skill
class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        logger.info("In CancelOrStopIntentHandler")

        handler_input.response_builder.speak(STOP_MESSAGE)
        return handler_input.response_builder.response


# Fallback Intent Handler
class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In FallbackIntentHandler")

        handler_input.response_builder.speak(FALLBACK_MESSAGE).ask(
            FALLBACK_REPROMPT)
        return handler_input.response_builder.response

# End Session Handler
class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        logger.info("In SessionEndedRequestHandler")

        logger.info("Session ended reason: {}".format(
            handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response


# Exception Handler
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.info("In CatchAllExceptionHandler")
        logger.error(exception, exc_info=True)

        handler_input.response_builder.speak(EXCEPTION_MESSAGE).ask(
            HELP_REPROMPT)

        return handler_input.response_builder.response


# Request and Response loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the alexa requests."""
    def process(self, handler_input):
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""
    def process(self, handler_input, response):
        logger.debug("Alexa Response: {}".format(response))


# Register intent handlers
sb.add_request_handler(TurnOnFanHandler())
sb.add_request_handler(TurnOffFanHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# TODO: Uncomment the following lines of code for request, response logs.
# sb.add_global_request_interceptor(RequestLogger())
# sb.add_global_response_interceptor(ResponseLogger())

# Handler name that is used on AWS lambda
lambda_handler = sb.lambda_handler()
