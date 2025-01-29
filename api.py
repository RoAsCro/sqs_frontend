import json
from os import getenv
import boto3
from flask import Blueprint, request
from dotenv import load_dotenv

load_dotenv()
high_priority = getenv("HIGH_PRIORITY_QUEUE")
mid_priority = getenv("MID_PRIORITY_QUEUE")
low_priority = getenv("LOW_PRIORITY_QUEUE")
access_id = getenv("AWS_ACCESS_KEY_ID")
access_key = getenv("AWS_SECRET_ACCESS_KEY")

sqs = boto3.client("sqs",
                   region_name='us-east-1',
                   aws_access_key_id=access_id,
                   aws_secret_access_key=access_key
                   )

router = Blueprint("messages", __name__, url_prefix="/api")


@router.post("/")
def post_message():
    message = request.json
    if "title" in message and "message" in message and "priority" in message:
        match message["priority"]:
            case "high":
                print(message)
                print(json.dumps(message))
                queue_url = high_priority
            case "medium":
                queue_url = mid_priority
            case "low":
                queue_url = low_priority
            case _:
                return "Unrecognised priority level - should be either low, mid, or high", 400

        sqs.send_message(QueueUrl=queue_url,
                         DelaySeconds=30,
                         MessageBody=json.dumps(message)
                         )
        return "Message sent", 200
    else:
        return "Failed to send - incorrect formatting", 400

@router.get("/")
def get_options():
    return ("To send a report: POST a JSON formatted:\n"
            "{'priority': 'low' | 'medium' | 'high',\n"
            "'title': string,\n"
            "'message': string}"), 200

@router.get("/health")
def health_check():
    return 'Healthy', 200
