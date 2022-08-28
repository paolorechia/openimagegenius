import json

import logging

from google.oauth2 import id_token
from google.auth.transport import requests
import urllib.parse as parser

client_ids = {
    "dev": "492480302511-89poe5o1iiegi5m7ammksfpduvqq7qsh.apps.googleusercontent.com"
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def hello(event, context):
    logger.info("Event: %s", event)
    try:
        body = event["body"]
        logger.info("Body: %s",  body)
        parameters = parser.parse_qs(body, strict_parsing=True, max_num_fields=3)
        token = parameters["credential"][0]
    except (KeyError, ValueError, IndexError):
        return {
            "statusCode": 400, "body": "Bad Request"
        }

    stage = event["requestContext"]["stage"]
    client_id = client_ids[stage]

    request = requests.Request()
    id_info = id_token.verify_oauth2_token(
        token, request, client_id)

    logger.info("Success!")
    logger.info("Id info: %s", id_info)
    userid = id_info['sub']

    body = {
        "message": "Authorized successfully!",
        "user_id": userid,
    }

    response = {"statusCode": 200, "body": json.dumps(body)}
    return response
