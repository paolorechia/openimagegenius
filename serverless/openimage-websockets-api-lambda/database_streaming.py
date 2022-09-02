import logging
import os

import boto3
import pydantic
import pydash as _

from openimage_backend_lib import repository as repo_module

environment = repo_module.EnvironmentInfo()

API_ID = os.environ["API_ID"]
STAGE = os.environ["AUTHORIZER_STAGE"]
REGION = os.environ["AWS_REGION"]

api_endpoint = f"https://{API_ID}.execute-api.{REGION}.amazonaws.com/{STAGE}"
api_client = boto3.client("apigatewaymanagementapi",
                          endpoint_url=api_endpoint)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def update_handler(event, context):
    """ Example event:
    {
        "Records": [
            {
            "eventID": "c81e728d9d4c2f636f067f89cc14862c",
            "eventName": "MODIFY",
            "eventVersion": "1.1",
            "eventSource": "aws:dynamodb",
            "awsRegion": "us-east-1",
            "dynamodb": {
                "Keys": {
                "Id": {
                    "N": "101"
                }
                },
                "NewImage": {
                "Message": {
                    "S": "This item has changed"
                },
                "Id": {
                    "N": "101"
                }
                },
                "OldImage": {
                "Message": {
                    "S": "New item!"
                },
                "Id": {
                    "N": "101"
                }
                },
                "ApproximateCreationDateTime": 1428537600,
                "SequenceNumber": "4421584500000000017450439092",
                "SizeBytes": 59,
                "StreamViewType": "NEW_AND_OLD_IMAGES"
            },
            "eventSourceARN": "arn:aws:dynamodb:us-east-1:123456789012:table/ExampleTableWithStream/stream/2015-06-27T00:48:05.899"
            },
        ]
    }
    """
    logger.info("Event: %s", event)
    records = event["Records"]
    for record in records:
        logger.info("Record: %s", record)
        # TODO, finish this part
        # payload = "Job completed: %s"
        # api_client.post_to_connection(
        #     Data=payload,
        #     ConnectionId=connection_id
        # )
