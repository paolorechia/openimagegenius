import logging
import os
from copy import deepcopy
from typing import List

import time
# Let's test the library import
import boto3
from google.auth.transport import requests
from google.oauth2 import id_token
from openimage_backend_lib import database_models as models
from openimage_backend_lib import repository as repo_module
from openimage_backend_lib import authorizer_helper

dynamodb_client = boto3.client("dynamodb")
environment = repo_module.EnvironmentInfo()
repository = repo_module.Repository(dynamodb_client, environment)

client_ids = {
    "dev": os.environ["GOOGLE_OAUTH_APP_ID"]
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

stage = os.environ["AUTHORIZER_STAGE"]
WS_SECRET_PASS = os.getenv("WS_SECRET_PASS", -1)
DEVELOPER_GOOGLE_USER_ID = os.getenv("DEVELOPER_GOOGLE_USER_ID", -1)


def handler(event, context):
    logger.info("Event: %s", event)
    try:
        resources = authorizer_helper.find_resources(event, stage)

        client_id = client_ids[stage]
        logger.info("Stage: %s", stage)

        token = event.get("authorizationToken")
        if not token:
            # In websockets API Gateway, we need to inspect the header
            token = event.get("headers", {}).get("Authorization")
            connection_id = event.get(
                "requestContext", {}).get("connectionId")

        logger.info("Connection ID: %s", connection_id)

        logger.info("Token: %s",  token)
        logger.info("Token type: %s", type(token))
        logger.info("Token length: %s", len(token))

        logger.info("WS SECRET PASS: %s", WS_SECRET_PASS)
        logger.info("WS SECRET PASS TYPE: %s", type(WS_SECRET_PASS))
        logger.info("WS SECRET PASS LENGTH: %s", len(WS_SECRET_PASS))

        if token == WS_SECRET_PASS:
            google_user_id = DEVELOPER_GOOGLE_USER_ID
            email = ""
        else:
            request = requests.Request()
            id_info = id_token.verify_oauth2_token(
                token, request, client_id)
            logger.info("ID Info: %s", id_info)
            google_user_id = id_info["sub"]
            email = id_info["email"]
        user: models.UserModel = repository.get_user_by_google_user_id(
            google_user_id)
        if not user:
            # Sleep a couple seconds and try again
            # To make sure index is not offsync
            time.sleep(2)
            user = repository.get_user_by_google_user_id(google_user_id)
        if not user:
            raise IndexError(
                f"User by google user id {google_user_id} not found.")
        if connection_id:
            repository.set_connection_id_for_user(
                user.unique_user_id, connection_id)

    except Exception as excp:
        logger.info("Caught exception: %s", str(excp))
        deny_policy = authorizer_helper.create_policy(
            event["methodArn"], "Deny")
        logger.info("Denied policy: %s", str(deny_policy))
        return deny_policy

    allow_policy = authorizer_helper.create_policy(resources, "Allow")
    allow_policy["context"] = {
        "unique_user_id": user.unique_user_id,
        "google_user_id": user.google_user_id,
        "user_google_email": user.user_google_email
    }
    logger.info("Allowed policy: %s", str(allow_policy))
    return allow_policy
