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
    "principalId": "user",
    "policyDocument": {
        "Version": "2012-10-17",
        "Statement": []
    },
    "context": {},
}

stage = os.environ["AUTHORIZER_STAGE"]


def create_policy(base_obj, resource, effect="Deny"):
    policy_obj = deepcopy(base_obj)
    policy_obj["policyDocument"]["Statement"].append(
        {
            "Action": "execute-api:Invoke",
            "Effect": effect,
            "Resource": resource
        }
    )
    return policy_obj


def find_resources(event, stage) -> List[str]:
    requested_resource = event.get("methodArn")
    resource_wildcard = requested_resource.split(f"/{stage}")[0] + "/*"
    logger.info("Base resource URL: %s", resource_wildcard)
    return resource_wildcard


def handler(event, context):
    logger.info("Event: %s", event)
    try:

        resources = find_resources(event, stage)

        client_id = client_ids[stage]
        logger.info("Stage: %s", stage)

        token = event["authorizationToken"]
        logger.info("Token: %s",  token)

        request = requests.Request()
        id_info = id_token.verify_oauth2_token(
            token, request, client_id)
        logger.info("ID Info: %s", id_info)
    except Exception as excp:
        logger.info("Caught exception: %s", str(excp))
        deny_policy = create_policy(
            base_policy_obj, event["methodArn"], "Deny")
        logger.info("Denied policy: %s", str(deny_policy))
        return deny_policy

    allow_policy = create_policy(base_policy_obj, resources, "Allow")
    allow_policy["context"] = {
        "google_user_id": id_info['sub'],
        "user_google_email": id_info["email"]
    }
    logger.info("Allowed policy: %s", str(allow_policy))
    return allow_policy
