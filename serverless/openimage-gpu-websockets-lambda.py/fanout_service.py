import json
import logging
import os
import sys
import traceback
from time import sleep

import boto3
import pydantic
from requests import Session

from openimage_backend_lib import database_models as models
from openimage_backend_lib import repository as repo_module
from openimage_backend_lib import telegram

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
telegram_client = telegram.get_telegram(Session())


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
    has_job_started = False
    found_gpu_node = False
    excp = ""
    if json_body["request_type"] == "prompt":
        # Find an available node
        # Presign an S3 post URL
        # Send to node as a job
        nodes = repository.scan_api_tokens()
        for node in nodes:
            if node.node_status == "ready":
                found_gpu_node = True
                # Found a node to use
                try:
                    s3_upload_details = s3_client.generate_presigned_post(
                        Bucket=s3_bucket,
                        Key=f"{user_unique_id}/{request_id}.jpg"
                    )
                    payload = json.dumps({
                        "message_type": "request_prompt",
                        "prompt": data,
                        "request_id": request_id,
                        "s3_url": s3_upload_details["url"],
                        "s3_fields": s3_upload_details["fields"]
                    })
                    api_client.post_to_connection(
                        Data=payload,
                        ConnectionId=node.connection_id
                    )
                    has_job_started = True
                    repository.set_unique_user_id_for_request(
                        request_id=request_id, unique_user_id=node.unique_user_id)
                except Exception as excp:
                    logger.error("Exception: %s", str(excp))
                    traceback.print_exc(file=sys.stdout)
                finally:
                    sleep(1.0)
                    repository.set_status_for_token(
                        api_token=node.api_token, status="ready")

        if not found_gpu_node or not has_job_started:
            repository.set_failed_status_for_request(request_id)
        if not found_gpu_node:
            telegram_client.send_message(
                f"Job {request_id} has failed. Reason: no GPU nodes are in ready state.")
        if not has_job_started:
            telegram_client.send_message(
                f"Job {request_id} has failed. Exception: {excp}")
            raise ValueError(
                f"Failed to run job for request_id: {request_id}")
    else:
        raise TypeError(
            f"request_type of type {request_type} is not supported by the fanout service")
