from os import getenv
import boto3
from flask import Blueprint, request
from dotenv import load_dotenv

load_dotenv()
sqs = boto3.client("sqs", region_name='us-east-1')
high_priority = getenv("HIGH_PRIORITY_QUEUE")
access_id = getenv("ACCESS_ID")
access_key = getenv("ACCESS_KEY")

router = Blueprint("messages", __name__, url_prefix="/")


@router.post("/")
def post_message():
    print(high_priority)
    message = request.json
    if "title" in message and "message" in message and "priority" in message:
        match message["priority"]:
            case "high":
                queue_url = high_priority
            case _:
                raise ValueError("Not yet implemented")

        sqs.send_message(QueueUrl=queue_url,
                         DelaySeconds=30,
                         MessageBody=f"Priority: {message['priority']}"
                                     f"{message['title']}: {message['message']}"
                         )
        test_message()


def test_message():
    message = sqs.receive_message(QueueUrl=high_priority,
    MaxNumberOfMessages=1,
    VisibilityTimeout=0,
    WaitTimeSeconds=0)
    print(message['Messages'][0])
    sqs.delete_message(
        QueueUrl=high_priority,
        ReceiptHandle=message['Messages'][0]['ReceiptHandle']
    )

