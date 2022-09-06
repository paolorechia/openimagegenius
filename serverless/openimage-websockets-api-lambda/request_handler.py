import json
import logging
import os
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
import time

import boto3
import pydash as _

from openimage_backend_lib import database_models as models
from openimage_backend_lib import repository as repo_module
from pydantic import BaseModel, ValidationError, validator

dynamodb_client = boto3.client("dynamodb")
sqs_client = boto3.client("sqs")
sqs_queue_url = os.environ["SQS_REQUEST_URL"]
environment = repo_module.EnvironmentInfo()
repository = repo_module.Repository(dynamodb_client, environment)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Request(BaseModel):
    data: str
    request_type: str
    unique_user_id: str

    @validator('data')
    def max_length_1024(cls, v):
        if len(v) > 1024:
            raise ValueError("data exceeds the limit of 1024 characters.")
        return v

    @validator('request_type')
    def request_type_validator(cls, v):
        if v.lower() not in models.REQUEST_TYPES:
            raise ValueError(f"Request type {v} is not recognized.")
        return v

    @validator('unique_user_id')
    def check_if_valid_uuid_v4(cls, v):
        UUID(v, version=4)
        return v


def build_error_message_body(error):
    return json.dumps({
        "message_type": "error",
        "data": error
    })


def request_handler(event, context):
    """Example request
    {
        'requestContext': {
            'routeKey': 'request',
            'authorizer': {
                'unique_user_id': '17b86c9e-9bac-4f2f-b10a-68619baba577',
                'google_user_id': '123',
                'user_google_email': 'developer@gmail.com',
                'principalId': 'user'
            },
            'messageId': 'Xux7ceaBliACHZQ=',
            'eventType': 'MESSAGE',
            'extendedRequestId': 'Xux7cExqliAFojw=',
            'requestTime': '31/Aug/2022:13:34:52 +0000',
            'messageDirection': 'IN',
            'stage': 'dev',
            'connectedAt': 1661952892072,
            'requestTimeEpoch': 1661952892224,
            'identity': {
                'userAgent': 'Python/3.8 websockets/10.3',
                'sourceIp': '93.193.144.114'
            },
            'requestId': 'Xux7cExqliAFojw=',
            'domainName': 'dev.ws-api.openimagegenius.com',
            'connectionId': 'Xux7aeaAFiACHZQ=',
            'apiId': '20kmit0mc5'
        },
        'body': '{"action": "request", "request_type": "prompt", "data": "As astronaut cat"}', 'isBase64Encoded': False
    }
    """
    logger.info(event)
    try:
        json_body = json.loads(event["body"])
    except json.JSONDecodeError:
        return {"statusCode": 400, "body": build_error_message_body("mal-formed JSON")}

    connection_id = _.get(event, "requestContext.connectionId")

    connection: Optional[models.ConnectionModel] = repository.get_connection_by_id(
        connection_id)

    if not connection or connection.authorized != "authorized":
        return {"statusCode": 401, "body": build_error_message_body("You're not authorized. Please send your valid token first.")}

    try:
        request = Request(
            unique_user_id=connection.unique_user_id,
            request_type=_.get(json_body, "request_type"),
            data=_.get(json_body, "data")
        )
    except ValidationError as excp:
        logger.info("Bad request")
        return {"statusCode": 400, "body": build_error_message_body(str(excp))}

    request_id = str(uuid4())
    maybe_existing_request = repository.get_request(request_id)
    if maybe_existing_request:
        logger.info("Conflict")
        return {"statusCode": 409, "body": build_error_message_body("Request ID conflict, try again.")}

    creation_time = datetime.now(tz=timezone.utc)
    creation_time_iso = creation_time.isoformat()
    creation_time_ts = creation_time.timestamp()

    request_status = "requested"

    new_request = models.RequestModel(
        requester_unique_user_id=request.unique_user_id,
        request_id=request_id,
        request_type=request.request_type,
        data=request.data,
        request_status=request_status,
        creation_time_iso=creation_time_iso,
        creation_time_timestamp=creation_time_ts,
        update_time_iso=creation_time_iso,
        update_time_timestamp=creation_time_ts,
    )

    repository.save_new_request(new_request)

    sqs_client.send_message(
        QueueUrl=sqs_queue_url,
        MessageBody=json.dumps({
            "request_type": request.request_type,
            "data": request.data,
            "unique_request_id": request_id,
            "requester_unique_user_id": request.unique_user_id,
        }),
    )
    logger.info("Success")
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message_type": "request_accepted",
            "data": {
                "request_id": request_id,
                "prompt": request.data,
                "status": request_status
            }
        })}
