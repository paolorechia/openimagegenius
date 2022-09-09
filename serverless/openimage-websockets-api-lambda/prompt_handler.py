import logging
from datetime import datetime, timezone
from uuid import uuid4

from openimage_backend_lib import database_models as models
from openimage_backend_lib.repository import Repository
from openimage_backend_lib.request_helper import build_error_message_body
from openimage_backend_lib.request_models import PromptRequest

import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def prompt_request_handler(request: PromptRequest, repository: Repository, sqs_client, queue_url):
    request_id = str(uuid4())
    maybe_existing_request = repository.get_request(request_id)
    if maybe_existing_request:
        logger.info("Conflict")
        return {"statusCode": 409, "body": build_error_message_body("Request ID conflict, try again.")}

    creation_time = datetime.now(tz=timezone.utc)
    creation_time_iso = creation_time.isoformat()
    creation_time_ts = creation_time.timestamp()

    request_status = "requested"

    new_request = models.RequestModel(
        requester_unique_user_id=request.unique_user_id,
        request_id=request_id,
        request_type=request.request_type,
        data=request.data,
        request_status=request_status,
        creation_time_iso=creation_time_iso,
        creation_time_timestamp=creation_time_ts,
        update_time_iso=creation_time_iso,
        update_time_timestamp=creation_time_ts,
    )

    repository.save_new_request(new_request)

    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({
            "request_type": request.request_type,
            "data": request.data,
            "unique_request_id": request_id,
            "requester_unique_user_id": request.unique_user_id,
        }),
    )
    logger.info("Success")
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message_type": "request_accepted",
            "data": {
                "request_id": request_id,
                "prompt": request.data,
                "status": request_status
            }
        })}
