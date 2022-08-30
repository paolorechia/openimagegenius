from re import L
from urllib import request
from .database_models import Metadata, RequestModel
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class EnviromentInfo:
    def __init__(self) -> None:
        self.user_table_name = os.environ["USER_TABLE_NAME"]
        self.request_table_name = os.environ["REQUEST_TABLE_NAME"]
        self.google_user_id_index_name = os.environ["GOOGLE_USER_ID_INDEX_NAME"]
        self.user_google_email_index_name = os.environ["USER_GOOGLE_EMAIL_INDEX_NAME"]
        self.request_unique_user_id_index = os.environ["REQUEST_UNIQUE_USER_ID_INDEX"]


def flatten_response(dynamodb_dict_response):
    flat_dict = {}
    for key, item in dynamodb_dict_response.items():
        type_ = [key for key in item.keys()][0]
        flat_dict[key] = item[type_]
    return flat_dict

def to_dynamodb_strings(model_dict_instance):
    to_dynamo = {}
    for key, item in model_dict_instance.items():
        to_dynamo[key] = {"S": item}
    return to_dynamo

class Repository:
    def __init__(self, dynamo_client, environment_info: EnviromentInfo):
        self.ddb = dynamo_client
        self.environment = environment_info

    def get_request(self, request_id) -> Optional[RequestModel]:
        logger.info("Looking for request in database...%s", str(request_id))
        response = self.ddb.get_item(
            TableName=self.enviroment.request_table_name,
            Key={
                Metadata.RequestTable.primary_key: {"S": request_id}
            }
        )
        logger.info("Dynamo response: %s", response)
        item = response.get("Item")
        if not item:
            return None
        return RequestModel(**flatten_response(item))

    def save_new_request(self, request: RequestModel) -> None:
        item = to_dynamodb_strings(request.dict())
        logger.info("Saving request to database: %s...", str(item))
        self.ddb.put_item(
            TableName=self.environment.request_table_name,
            Item=item
        )
        logger.info("Saved successfully!")
