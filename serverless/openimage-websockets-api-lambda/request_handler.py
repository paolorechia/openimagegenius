import json
import logging
import os
from typing import Optional

import boto3
import pydash as _

from openimage_backend_lib import database_models as models
from openimage_backend_lib import repository as repo_module
from openimage_backend_lib import request_models
from openimage_backend_lib.request_helper import build_error_message_body
from openimage_backend_lib.request_helper import build_rate_limited_response
from openimage_backend_lib.rate_limiter import get_limiter

from pydantic import ValidationError
from prompt_handler import prompt_request_handler
from get_requests_handler import get_requests_handler

dynamodb_client = boto3.client("dynamodb")
sqs_client = boto3.client("sqs")
sqs_queue_url = os.environ["SQS_REQUEST_URL"]
environment = repo_module.EnvironmentInfo()
repository = repo_module.Repository(dynamodb_client, environment)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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

    rate_limiter = get_limiter()

    if not rate_limiter.should_allow(connection_id):
        return build_rate_limited_response()

    connection: Optional[models.ConnectionModel] = repository.get_connection_by_id(
        connection_id)

    if not connection or connection.authorized != "authorized":
        return {"statusCode": 401, "body": build_error_message_body("You're not authorized. Please send your valid token first.")}
    request_type = _.get(json_body, "request_type")

    logger.info("Request type: %s", request_type)
    try:
        if request_type == "prompt":
            request = request_models.PromptRequest(
                unique_user_id=connection.unique_user_id,
                data=_.get(json_body, "data"),
            )
            logger.info("Calling handler: %s", prompt_request_handler)
            return prompt_request_handler(request, repository, sqs_client, sqs_queue_url)
        elif request_type == "get_requests":
            request = request_models.GetRequestsForUser(
                unique_user_id=connection.unique_user_id,
                data=_.get(json_body, "data"),
            )
            logger.info("Calling handler: %s", get_requests_handler)
            return get_requests_handler(request, repository)
    except ValidationError as excp:
        logger.info("Bad request")
        return {"statusCode": 400, "body": build_error_message_body(str(excp))}
    return {"statusCode": 400, "body": build_error_message_body(f"Could not handle request type: {request_type}")}
