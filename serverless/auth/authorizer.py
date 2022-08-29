from typing import List
from copy import deepcopy
from google.oauth2 import id_token
from google.auth.transport import requests
import logging
import os

client_ids = {
    "dev": os.environ["GOOGLE_OAUTH_APP_ID"]
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

base_policy_obj = {
    "Version": "2012-10-17",
    "Statement": []
}

example_resource = "arn:aws:execute-api:us-east-1:123456789012:ivdtdhp7b5/ESTestInvoke-stage/GET/"


def create_policy(base_obj, resources, effect="Deny"):
    policy_obj = deepcopy(base_obj)
    for resource in resources:
        policy_obj.append(
            {
                "Action": "execute-api:Invoke",
                "Effect": effect,
                "Resource": resource
            }
        )
    return policy_obj


def find_resources(event) -> List[str]:
    return []


def hello(event, context):
    logger.info("Event: %s", event)
    resources = find_resources(event)
    try:
        stage = event["requestContext"]["stage"]
        client_id = client_ids[stage]
        logger.info("Stage: %s", stage)

        token = event["headers"]["Authorization"]
        logger.info("Token: %s",  token)

        request = requests.Request()
        id_info = id_token.verify_oauth2_token(
            token, request, client_id)
        logger.info("ID Info: %s", id_info)
    except Exception:
        deny_policy = create_policy(base_policy_obj, resources, "Deny")
        logger.info("Denied policy: %s", str(deny_policy))
        return deny_policy

    allow_policy = create_policy(base_policy_obj, resources, "Allow")
    logger.info("Allowed policy: %s", str(allow_policy))
    return allow_policy
