import json
import logging
import sys
from os import getenv

import boto3
from botocore import exceptions
from dotenv import load_dotenv
from flask import Blueprint, request
from pydantic import ValidationError

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

router = Blueprint("messages", __name__, url_prefix="/api")

error_in = "Error in field"

def set_logger(mode):
    if mode == "error":
        logger.setLevel(logging.ERROR)
    elif mode == "debug":
        logger.setLevel(logging.DEBUG)


@router.post("/")
def post_message():
    message = request.json
    try:
        Message.model_validate(message)
    except ValidationError as ex:
        error_string = "Errors in Json:\n"
        for error in ex.errors():
            location = error['loc'][0]
            error_string += (f"\t{error_in} {location}: {error['msg']}.\n"
                             f"\tGot '{error['input']}'.\n\n")

        return error_string, 400
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
            return json.dumps({"Unrecognised priority level - should be either low, mid, or high"}), 400

    try:
        logger.debug("Sending...")
        response = sqs.send_message(QueueUrl=queue_url,
                         DelaySeconds=30,
                         MessageBody=json.dumps(message))
        message_id = response["MessageId"]
        logger.debug(message_id + " sent")
    except exceptions.ClientError as ex :
        logger.error(f"Issue with client configuration:\n{ex}")
        return json.dumps({"message":"Failed to send - internal server error"}), 500

    except TypeError as ex:
        logger.error(f"Environment likely not initialised\n{ex}")
        return json.dumps({"message": "Failed to send - internal server error"}), 500

    return (json.dumps({'message': 'Message sent',
            'message_id': message_id})), 200

@router.get("/")
def get_options():
    return json.dumps({"message":("To send a report: POST a JSON formatted:"
            "<p>{'priority': 'low' | 'medium' | 'high',</p>"
            "<p>'title': string,</p>"
            "<p>'message': string}</p>")}), 200

@router.get("/health")
def health_check():
    return json.dumps({"message":"Ok"}), 200
