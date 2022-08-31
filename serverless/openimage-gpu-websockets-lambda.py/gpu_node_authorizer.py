
import logging
import os
import pydash as _
import boto3
from openimage_backend_lib import authorizer_helper
from openimage_backend_lib import repository as repo_module

dynamodb_client = boto3.client("dynamodb")
environment = repo_module.EnvironmentInfo()
repository = repo_module.Repository(dynamodb_client, environment)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stage = os.environ["AUTHORIZER_STAGE"]


def handler(event, context):
    logger.info("Event: %s", event)

    api_token = _.get(event, "headers.Authorization")
    resources = authorizer_helper.find_resources(event, stage)

    should_allow = False
    if api_token:
        gpu_user = repository.get_user_by_api_token(api_token)
        if gpu_user:
            should_allow = True

    if not should_allow:
        deny_policy = authorizer_helper.create_policy(
            event["methodArn"], "Deny")
        logger.info("Denied policy: %s", str(deny_policy))
        return deny_policy

    allow_policy = authorizer_helper.create_policy(resources, "Allow")
    allow_policy["context"] = {
        "api_token": gpu_user.api_token,
        "unique_user_id": gpu_user.unique_user_id,
    }

    logger.info("Allowed policy: %s", str(allow_policy))
    return allow_policy
