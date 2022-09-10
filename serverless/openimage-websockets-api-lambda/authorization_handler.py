import json
import logging
import os

import boto3
import pydash as _
from openimage_backend_lib import authorizer
from openimage_backend_lib import database_models as models
from openimage_backend_lib import repository as repo_module
from openimage_backend_lib.request_helper import build_rate_limited_response
from openimage_backend_lib.rate_limiter import get_limiter

import time

dynamodb_client = boto3.client("dynamodb")
sqs_client = boto3.client("sqs")
sqs_queue_url = os.environ["SQS_REQUEST_URL"]
environment = repo_module.EnvironmentInfo()
repository = repo_module.Repository(dynamodb_client, environment)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def authorization_handler(event, context):
    logger.info("Event: %s", event)
    connection_id = _.get(event, "requestContext.connectionId")
    logger.info("Connection ID: %s", connection_id)
    logger.info("Invoking authorizer from library")

    rate_limiter = get_limiter()

    if not rate_limiter.should_allow(connection_id):
        logger.info("Rate limited, returning 429")
        return build_rate_limited_response()

    policy = authorizer.handler(event, context)
    logger.info("Policy: %s", policy)
    unique_user_id = _.get(policy, "context.unique_user_id")
    if not unique_user_id:
        logger.info("Sorry, could not find your user ID")
        repository.update_connection(
            connection_id, authorized="unauthorized", unique_user_id="anonymous")
        return {
            "statusCode": 401,
            "body": json.dumps({
                "message_type": "authorization",
                "data": "unauthorized"
            })
        }
    else:
        time.sleep(1.0)
        repository.update_connection(
            connection_id, authorized="authorized", unique_user_id=unique_user_id)

        logger.info("Welcome user %s", unique_user_id)
        logger.info("Connection is now upgraded to authorized ;)")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message_type": "authorization",
                "data": "authorized"
            })
        }
