import os
from os import getenv
from dotenv import load_dotenv

import boto3
from botocore.exceptions import ClientError
load_dotenv()
region = getenv("AWS_REGION")
key = getenv("AWS_ACCESS_KEY_ID")
key2 = getenv("AWS_SECRET_ACCESS_KEY")
bedrock_client = boto3.client(
    service_name = "bedrock-runtime",
    region_name = region,
aws_access_key_id = key,
aws_secret_access_key = key2
)

model_id = "amazon.titan-text-lite-v1"
def my_chatbot(user_message):

    conversation = [
        {
            "role": "user",
            "content": [{"text":"How do I fix this:" + user_message}],
        }
    ]
    try:
        # Send the message to the model, using a basic inference configuration.
        response = bedrock_client.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9},
        )

        # Extract and print the response text.
        response_text = response["output"]["message"]["content"][0]["text"]
        return response_text
    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")

# if __name__ == "__main__":
#     print(my_chatbot("Test message"))