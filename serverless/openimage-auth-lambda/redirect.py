from enum import unique
import logging
import os
import urllib.parse as parser
from datetime import datetime, timezone

from uuid import uuid4
import boto3
from google.auth.transport import requests
from google.oauth2 import id_token

from openimage_backend_lib import database_models as models
from openimage_backend_lib import repository as repo_module

dynamodb_client = boto3.client("dynamodb")
environment = repo_module.EnvironmentInfo()
repository = repo_module.Repository(dynamodb_client, environment)

client_ids = {
    "dev": os.environ["GOOGLE_OAUTH_APP_ID"]
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

dynamo_db_client = boto3.client("dynamodb")


html_success_page = """
<html>
    <head>
        <title>openimagegenius</title>
    </head>
    <body>
        <h2> Authentication Successful, Redirecting... </h2>
        <script>
            location.assign("https://{}.app.openimagegenius.com")
        </script>
    </body>
</html>
"""

html_failure_page = """
<html>
    <head>
        <title>openimagegenius</title>
    </head>
    <body>
        <h2> Authentication Failed, Redirecting... </h2>
        <h3> Error: {} </h3>
    </body>
</html>
"""


def handler(event, context):
    logger.info("Event: %s", event)
    try:
        body = event["body"]
        logger.info("Body: %s",  body)
        parameters = parser.parse_qs(
            body, strict_parsing=True, max_num_fields=3)
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

    logger.info("Token is valid.")
    logger.info("Id info: %s", id_info)
    google_user_id = id_info['sub']
    user_google_email = id_info["email"]

    logging.info("Looking for existing user...")
    try:
        user = repository.get_user_by_google_user_id(google_user_id)
    except IndexError:
        logger.info("Multiple users found, something went wrong :(")
        return {
            "statusCode": 409,
            "body": html_failure_page.format("Multiple users found, conflict. Please contact support for help"),
            "headers": {
                "Content-Type": "text/html"
            }
        }
    if user:
        unique_user_id = user.unique_user_id
    else:
        logger.info("User not found, new user should be created :)")
        unique_user_id = str(uuid4())
        clashed_user = "TemporarySentinel"
        attempts = 0
        while clashed_user and attempts <= 3:
            clashed_user = repository.get_user_by_unique_id(
                unique_user_id)

            if clashed_user:
                unique_user_id = str(uuid4())
                attempts += 1

            if attempts > 3:
                return {
                    "statusCode": 503,
                    "body": html_failure_page.format("Could not process your request at this time, please try again later."),
                    "headers": {
                        "Content-Type": "text/html"
                    }
                }

            logger.info("Creating new user :)")
            creation_time = datetime.now(tz=timezone.utc)
            creation_time_iso = creation_time.isoformat()
            creation_time_timestamp = creation_time.timestamp()
            repository.save_user(
                models.UserModel(
                    unique_user_id=unique_user_id,
                    google_user_id=google_user_id,
                    user_google_email=user_google_email,
                    creation_time_iso=creation_time_iso,
                    creation_time_timestamp=creation_time_timestamp,
                )
            )

    body = {
        "message": "Authorized successfully!",
        "unique_user_id": unique_user_id,
        "google_user_id": google_user_id,
        "user_email": user_google_email
    }
    logger.info("Successful, authenticated user: %s", str(body))
    response = {
        "statusCode": 200,
        "body": html_success_page.format(stage),
        "headers": {
            "Set-Cookie": f"token={token}; Domain=openimagegenius.com",
            "Content-Type": "text/html"
        }}
    return response
