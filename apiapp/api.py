import json
import logging
from os import getenv

import boto3
from botocore import exceptions
from dotenv import load_dotenv
from flask import Blueprint, request
from pydantic import ValidationError

from json_models import Message

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
            return "Unrecognised priority level - should be either low, mid, or high", 400

    try:
        response = sqs.send_message(QueueUrl=queue_url,
                         DelaySeconds=30,
                         MessageBody=json.dumps(message))
    except exceptions.ClientError as ex :
        logging.error(ex)
        return "Failed to send - internal server error", 500

    message_id = response["MessageId"]
    return (json.dumps({'message': 'Message sent',
            'message_id': message_id})), 200

@router.get("/")
def get_options():
    return ("To send a report: POST a JSON formatted:\n"
            "{'priority': 'low' | 'medium' | 'high',\n"
            "'title': string,\n"
            "'message': string}"), 200

@router.get("/health")
def health_check():
    return 'Ok', 200
