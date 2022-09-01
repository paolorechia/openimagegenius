import json
import logging
import os

import boto3

import pydantic
from openimage_backend_lib import database_models as models
from openimage_backend_lib import repository as repo_module

import pydash as _

dynamodb_client = boto3.client("dynamodb")

aws_region = os.environ["AWS_REGION"]
environment = repo_module.EnvironmentInfo()
repository = repo_module.Repository(dynamodb_client, environment)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):
    logger.info("Event: %s", event)
    """Sample event:
        {
        "Records": [
            {
            "eventVersion": "2.0",
            "eventSource": "aws:s3",
            "awsRegion": "us-east-1",
            "eventTime": "1970-01-01T00:00:00.000Z",
            "eventName": "ObjectCreated:Put",
            "userIdentity": {
                "principalId": "EXAMPLE"
            },
            "requestParameters": {
                "sourceIPAddress": "127.0.0.1"
            },
            "responseElements": {s
                "x-amz-request-id": "EXAMPLE123456789",
                "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
            },
            "s3": {
                "s3SchemaVersion": "1.0",
                "configurationId": "testConfigRule",
                "bucket": {
                "name": "example-bucket",
                "ownerIdentity": {
                    "principalId": "EXAMPLE"
                },
                "arn": "arn:aws:s3:::example-bucket"
                },
                "object": {
                "key": "test/key",
                "size": 1024,
                "eTag": "0123456789abcdef0123456789abcdef",
                "sequencer": "0A1B2C3D4E5F678901"
                }
            }
            }
        ]
    }
    """
    records = event["Records"]
    for record in records:
        bucket_name = _.get(record, "s3.bucket.name")
        key = _.get(record, "s3.object.key")
        size = _.get(record, "s3.object.size")

        logger.info("bucket_name: %s", bucket_name)
        logger.info("key: %s", key)

        prefix = key.split(".jpg")[0]
        s = prefix.split("/")
        requester_id = s[0]
        request_id = s[1]

        logger.info("request_id: %s", request_id)

        url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/{key}"
        logger.info("s3 url to save: %s", url)
        repository.set_s3_path_for_request(request_id, url)
