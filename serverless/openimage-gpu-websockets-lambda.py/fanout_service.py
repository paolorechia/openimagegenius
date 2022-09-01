import json
import logging
import os

import boto3

import pydantic
from openimage_backend_lib import database_models as models
from openimage_backend_lib import repository as repo_module
import traceback

from time import sleep
import sys

API_ID = os.environ["API_ID"]
STAGE = os.environ["AUTHORIZER_STAGE"]
REGION = os.environ["AWS_REGION"]
s3_bucket = os.environ["S3_BUCKET"]

api_endpoint = f"https://{API_ID}.execute-api.{REGION}.amazonaws.com/{STAGE}"
api_client = boto3.client("apigatewaymanagementapi",
                          endpoint_url=api_endpoint)

dynamodb_client = boto3.client("dynamodb")
s3_client = boto3.client("s3")

environment = repo_module.EnvironmentInfo()
repository = repo_module.Repository(dynamodb_client, environment)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):
    """Sample event:
    {
        "Records": [
            {
            "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
            "receiptHandle": "MessageReceiptHandle",
            "body": "Hello from SQS!",
            "attributes": {
                "ApproximateReceiveCount": "1",
                "SentTimestamp": "1523232000000",
                "SenderId": "123456789012",
                "ApproximateFirstReceiveTimestamp": "1523232000001"
            },
            "messageAttributes": {},
            "md5OfBody": "7b270e59b47ff90a553787216d55d91d",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:MyQueue",
            "awsRegion": "us-east-1"
            }
        ]
    }
    """
    logger.info("Event: %s", event)
    logger.info("Using api endpoint: %s", api_endpoint)
    record = event["Records"][0]
    json_body = json.loads(record["body"])
    """
    This should be the expected format for json_body: {
        "request_type": request.request_type,
        "data": request.data,
        "unique_request_id": request_id,
        "requester_unique_user_id": request.unique_user_id,
    }
    """
    request_type = json_body["request_type"]
    data = json_body["data"]
    request_id = json_body["unique_request_id"]
    user_unique_id = json_body["requester_unique_user_id"]

    if json_body["request_type"] == "prompt":
        # Find an available node
        # Presign an S3 post URL
        # Send to node as a job
        nodes = repository.scan_api_tokens()
        for node in nodes:
            if node.node_status == "ready":
                # Found a node to use
                has_job_started = False
                repository.set_status_for_token(
                    api_token=node.api_token, status="scheduling")
                try:
                    s3_upload_details = s3_client.generate_presigned_post(
                        Bucket=s3_bucket,
                        Key=f"{user_unique_id}/{request_id}.jpg"
                    )
                    payload = json.dumps({
                        "message_type": "request_prompt",
                        "data": data,
                        "request_id": request_id,
                        "s3_url": s3_upload_details["url"],
                        "s3_fields": s3_upload_details["fields"]
                    })
                    api_client.post_to_connection(
                        Data=payload,
                        ConnectionId=node.connection_id
                    )
                    has_job_started = True
                except Exception as excp:
                    logger.error("Exception: %s", str(excp))
                    traceback.print_exc(file=sys.stdout)

                finally:
                    # If something goes wrong, reset node status, so it doesn't get locked out
                    # Sleep a bit to avoid concurrency issues
                    if not has_job_started:
                        sleep(1.0)
                        repository.set_status_for_token(
                            api_token=node.api_token, status="ready")
                        raise ValueError(
                            f"Failed to run job for request_id: {request_id}")
    else:
        raise TypeError(
            f"request_type of type {request_type} is not supported by the fanout service")
