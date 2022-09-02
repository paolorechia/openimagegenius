import logging
import os

import boto3
import pydantic
import pydash as _
import json

from openimage_backend_lib import repository as repo_module

environment = repo_module.EnvironmentInfo()

API_ID = os.environ["API_ID"]
STAGE = os.environ["AUTHORIZER_STAGE"]
REGION = os.environ["AWS_REGION"]

api_endpoint = f"https://{API_ID}.execute-api.{REGION}.amazonaws.com/{STAGE}"
api_client = boto3.client("apigatewaymanagementapi",
                          endpoint_url=api_endpoint)

dynamodb_client = boto3.client("dynamodb")
environment = repo_module.EnvironmentInfo()
repository = repo_module.Repository(dynamodb_client, environment)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DynamoDBRecordReader:
    def __init__(self, record):
        self.record = record

    def get(self, attr):
        return _.get(self.record, f"dynamodb.NewImage.{attr}.S")


def update_handler(event, context):
    """ Example record:
    {
        'eventID': '0f1183e06ed2c000b9636951f7fbb385',
        'eventName': 'MODIFY',
        'eventVersion': '1.1',
        'eventSource': 'aws:dynamodb',
        'awsRegion': 'eu-central-1',
        'dynamodb': {
            'ApproximateCreationDateTime': 1662154836.0,
            'Keys': {
                'request_id': {'S': 'e67f73f2-fc78-4c56-9442-b8d6c75ead56'}
            },
            'NewImage': {
                'request_status': {'S': 'completed'},
                'data': {'S': 'A cowboy cat'},
                'request_type': {'S': 'prompt'},
                'medium_thumbnail_s3_path': {'S': ''},
                's3_url': {'S': 'https://open-image-genius-generated-images-dev.s3.eu-central-1.amazonaws.com/17b86c9e-9bac-4f2f-b10a-68619baba576/e67f73f2-fc78-4c56-9442-b8d6c75ead56.jpg'},
                'small_tumbnail_s3_path': {'S': ''},
                'update_time_iso': {'S': '2022-09-02T21:40:36.378130+00:00'},
                'gpu_user_id': {'S': '17b86c9e-9bac-4f2f-b10a-68619baba576'},
                'requester_unique_user_id': {'S': '17b86c9e-9bac-4f2f-b10a-68619baba576'},
                'creation_time_timestamp': {'S': '1662154830.524465'},
                'creation_time_iso': {'S': '2022-09-02T21:40:30.524465+00:00'},
                'update_time_timestamp': {'S': '1662154836.37813'},
                'request_id': {'S': 'e67f73f2-fc78-4c56-9442-b8d6c75ead56'}},
            'SequenceNumber': '14668500000000008848010472',
            'SizeBytes': 635,
            'StreamViewType': 'NEW_IMAGE'
        },
        'eventSourceARN': 'arn:aws:dynamodb:eu-central-1:787492735804:table/request-table-name-dev/stream/2022-09-01T22:34:12.259'
    }

    """
    logger.info("Event: %s", event)
    records = event["Records"]
    for record in records:
        logger.info("Record: %s", record)
        reader = DynamoDBRecordReader(record)
        request_status = reader.get("request_status")
        logger.info("Request status: %s", request_status)
        if request_status == "completed":
            s3_url = reader.get("s3_url")
            unique_user_id = reader.get("requester_unique_user_id")
            user = repository.get_user_by_unique_id(unique_user_id)
            if user.connection_status == "connected":
                payload = json.dumps({
                    "message_type": "job_complete",
                    "data": {
                        "s3_url": s3_url,
                        "prompt": reader.get("data"),
                        "update_time_iso": reader.get("update_time_iso"),
                        "request_id": reader.get("request_id"),
                    }
                })

                api_client.post_to_connection(
                    Data=payload,
                    ConnectionId=user.connection_id
                )
