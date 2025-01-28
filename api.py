from os import getenv
import boto3
from flask import Blueprint, request
from dotenv import load_dotenv

load_dotenv()
high_priority = getenv("HIGH_PRIORITY_QUEUE")
mid_priority = getenv("MID_PRIORITY_QUEUE")
access_id = getenv("ACCESS_ID")
access_key = getenv("ACCESS_KEY")

sqs = boto3.client("sqs",
                   region_name='us-east-1',
                   aws_access_key_id=access_id,
                   aws_secret_access_key=access_key
                   )


router = Blueprint("messages", __name__, url_prefix="/")


@router.post("/")
def post_message():
    message = request.json
    if "title" in message and "message" in message and "priority" in message:
        match message["priority"]:
            case "high":
                queue_url = high_priority
            case "mid":
                queue_url = mid_priority
            case _:
                raise ValueError("Not yet implemented")

        sqs.send_message(QueueUrl=queue_url,
                         DelaySeconds=30,
                         MessageBody=f"Priority: {message['priority']}\n"
                                     f"{message['title']}: {message['message']}"
                         )
        return "message sent", 200
    else:
        return "failed to send", 500

