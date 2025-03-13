import json
import logging
import sys
from os import getenv

import boto3
import flask
from botocore import exceptions
from dotenv import load_dotenv
from flask import Blueprint, request
from pydantic import ValidationError

from suggest import my_chatbot

from json_models import Message
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.ERROR)

default_region = "us-east-1"

load_dotenv()
aws_region = getenv("AWS_REGION")
if aws_region is None:
    aws_region = default_region
high_priority = getenv("HIGH_PRIORITY_QUEUE")
mid_priority = getenv("MID_PRIORITY_QUEUE")
low_priority = getenv("LOW_PRIORITY_QUEUE")
access_id = getenv("AWS_ACCESS_KEY_ID")
access_key = getenv("AWS_SECRET_ACCESS_KEY")

sqs = boto3.client("sqs",
                   region_name=aws_region,
                   aws_access_key_id=access_id,
                   aws_secret_access_key=access_key
                   )

router = Blueprint("messages", __name__, url_prefix="/")

error_in = "Error in field"

def set_logger(mode):
    if mode == "error":
        logger.setLevel(logging.ERROR)
    elif mode == "debug":
        logger.setLevel(logging.DEBUG)

@router.route("/")
def index():
    return flask.render_template("index.html")


def suggest(message):
    suggestion = "\nAutomatically generated suggestion:   \n\n" + my_chatbot(message['message'])
    message["message"] += suggestion

@router.post("/api")
def post_message():
    message = request.json
    try:
        Message.model_validate(message)
    except ValidationError as ex:
        error_string = '{"Errors in Json":['
        count = 0
        for error in ex.errors():
            if count > 0:
                error_string += ","
            location = error['loc'][0]
            error_string += ('{"1. location":"' + f"{location}" + '","2. error description":"' + f"{error['msg']}" + '","'
                             '3. actual":"' + f"{error['input']}" + '"}')
            count += 1

        error_string += "]"
        return json.loads(error_string + '}'), 400
    if "message" not in message:
        message.update({"message": ""})

    match message["priority"]:
        case "high":
            queue_url = high_priority
        case "medium":
            queue_url = mid_priority
        case "low":
            queue_url = low_priority
        case _: # Should now be unreachable with above checking
            return json.loads('{"Unrecognised priority level - should be either low, mid, or high"}'), 400

    try:
        logger.debug("Requesting AI suggestion...")
        suggest(message)
        logger.debug("Sending...")
        response = sqs.send_message(QueueUrl=queue_url,
                         DelaySeconds=30,
                         MessageBody=json.dumps(message))
        message_id = response["MessageId"]
        logger.debug(message_id + " sent")
    except exceptions.ClientError as ex :
        logger.error(f"Issue with client configuration:\n{ex}")
        return json.loads('{"message":"Failed to send - internal server error"}'), 500

    except TypeError as ex:
        logger.error(f"Environment likely not initialised\n{ex}")
        return json.loads('{"message": "Failed to send - internal server error"}'), 500

    return (json.loads('{"message": "Message sent",'
            '"message_id":"' + message_id+ '"}')), 200

@router.get("/api")
def get_options():
    return json.loads('{"message":"To send a report: POST a JSON formatted: '
                      '{priority: low | medium | high, '
                      'title: string, '
                      'message: string}"}'), 200

@router.get("/health")
def health_check():
    return json.loads('{"message":"Ok"}'), 200
