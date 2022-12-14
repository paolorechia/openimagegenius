import logging

import boto3
import pydantic
import pydash as _

from openimage_backend_lib import database_models as models
from openimage_backend_lib import repository as repo_module
from openimage_backend_lib.rate_limiter import get_limiter
from openimage_backend_lib.request_helper import build_rate_limited_response

dynamodb_client = boto3.client("dynamodb")
environment = repo_module.EnvironmentInfo()
repository = repo_module.Repository(dynamodb_client, environment)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def connect_handler(event, context):
    """"
    example_request = {
        'headers': {
            'Authorization': 'AAAAA',
            'Host': 'dev.ws-api.openimagegenius.com',
            'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
            'Sec-WebSocket-Key': 'WkQgPq2aaLgLt09qzhmA8g==',
            'Sec-WebSocket-Version': '13',
            'User-Agent': 'Python/3.8 websockets/10.3',
            'X-Amzn-Trace-Id': 'Root=1-630f637c-74d9e0581d71eb9d0ca0b056',
            'X-Forwarded-For': '93.193.144.114',
            'X-Forwarded-Port': '443',
            'X-Forwarded-Proto': 'https'
        },
        'multiValueHeaders': {
            'Authorization': ['AAAAA'],
            'Host': ['dev.ws-api.openimagegenius.com'],
            'Sec-WebSocket-Extensions': ['permessage-deflate; client_max_window_bits'],
            'Sec-WebSocket-Key': ['WkQgPq2aaLgLt09qzhmA8g=='],
            'Sec-WebSocket-Version': ['13'],
            'User-Agent': ['Python/3.8 websockets/10.3'],
            'X-Amzn-Trace-Id': ['Root=1-630f637c-74d9e0581d71eb9d0ca0b056'],
            'X-Forwarded-For': ['93.193.144.114'],
            'X-Forwarded-Port': ['443'],
            'X-Forwarded-Proto': ['https']
        },
        'requestContext': {
            'routeKey': '$connect',
            'authorizer': {
                'unique_user_id': '17b86c9e-9bac-4f2f-b10a-68619baba577',
                'google_user_id': '123',
                'user_google_email': 'developer@gmail.com',
                'principalId': 'user',
                'integrationLatency': 111
            },
            'eventType': 'CONNECT',
            'extendedRequestId': 'Xux7aHf-FiAFqTg=',    logger.info("Connection request received.")

            'connectedAt': 1661952892072,
            'requestTimeEpoch': 1661952892073,
            'identity': {'userAgent': 'Python/3.8 websockets/10.3', 'sourceIp': '93.193.144.114'},
            'requestId': 'Xux7aHf-FiAFqTg=',
            'domainName': 'dev.ws-api.openimagegenius.com',
            'connectionId': 'Xux7aeaAFiACHZQ=',
            'apiId': '20kmit0mc5'
        },
        'isBase64Encoded': False
    }
    """
    logger.info("Event: %s", event)
    connection_id = _.get(event, "requestContext.connectionId")
    ip_address = _.get(event, "requestContext.identity.sourceIp")

    if not ip_address:
        logger.warn("IP Address not found!")
        return build_rate_limited_response()
    rate_limiter = get_limiter()

    if not rate_limiter.should_allow(ip_address):
        return build_rate_limited_response()

    repository.add_connection(connection_id, ip_address)
    logger.info("Connection request received.")
    return {"statusCode": 200, "body": "You're connected, but not authorized."}
