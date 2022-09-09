import json
import logging
import pydash as _

from typing import List

from openimage_backend_lib.database_models import RequestModel
from openimage_backend_lib import request_models
from openimage_backend_lib.repository import Repository

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_requests_handler(request: request_models.GetRequestsForUser, repository: Repository):
    requests: List[RequestModel] = repository.query_user_requests(
        unique_user_id=request.unique_user_id)

    dict_requests = []
    for request in requests:
        dict_requests.append(request.dict())
    logger.info("Success")
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message_type": "get_requests_response",
            "data": {
                "requests": dict_requests
            }
        })}
