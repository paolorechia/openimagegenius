import json
import logging
from urllib import response
import pydash as _

from typing import List

from openimage_backend_lib.database_models import RequestModel
from openimage_backend_lib import request_models
from openimage_backend_lib.repository import Repository

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_requests_handler(request: request_models.GetRequestsForUser, repository: Repository):
    requests, last_evaluated_key = repository.query_user_requests(
        unique_user_id=request.unique_user_id,
        page_size=request.data.page_size,
        last_evaluated_key=request.data.last_evaluated_key
    )

    dict_requests = []
    for request in requests:
        dict_requests.append(request.dict())
    logger.info("Success")
    response_body = {
        "message_type": "get_requests_response",
        "data": {
            "requests": dict_requests
        },
        "pagination": {
            "last_evaluated_key": None
        }
    }
    if last_evaluated_key:
        response_body["pagination"]["last_evaluated_key"] = last_evaluated_key
    return {
        "statusCode": 200,
        "body": json.dumps(response_body)}
