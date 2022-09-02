import logging
import time
from typing import Optional

import boto3
import pydash as _

from openimage_backend_lib import database_models as models
from openimage_backend_lib import repository as repo_module

dynamodb_client = boto3.client("dynamodb")
environment = repo_module.EnvironmentInfo()
repository = repo_module.Repository(dynamodb_client, environment)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def default_handler(event, context):
    logger.info("Event: %s", event)
    connection_id = _.get(event, "requestContext.connectionId")
    connection: Optional[models.ConnectionModel] = repository.get_connection_by_id(
        connection_id)

    if not connection or connection.authorized != "authorized":
        return {"statusCode": 401, "body": "You're not authorized. Please send your valid token first."}

    return {"statusCode": 200, "body": "Default route. Nothing fancy."}
