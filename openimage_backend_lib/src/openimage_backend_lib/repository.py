from enum import unique
from .database_models import Metadata, RequestModel, UserModel, APITokenModel
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EnvironmentInfo:
    def __init__(self) -> None:
        # tables
        self.user_table_name = os.environ["USER_TABLE_NAME"]
        self.request_table_name = os.environ["REQUEST_TABLE_NAME"]
        self.api_token_table_name = os.environ["API_TOKEN_TABLE_NAME"]
        # indices
        self.google_user_id_index_name = os.environ["GOOGLE_USER_ID_INDEX_NAME"]
        self.user_google_email_index_name = os.environ["USER_GOOGLE_EMAIL_INDEX_NAME"]
        self.request_unique_user_id_index = os.environ["REQUEST_UNIQUE_USER_ID_INDEX"]
        self.api_token_unique_user_id_index = os.environ["API_TOKEN_UNIQUE_USER_ID_INDEX"]


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
    def __init__(self, dynamo_client, environment_info: EnvironmentInfo):
        self.ddb = dynamo_client
        self.environment = environment_info

    def get_request(self, request_id) -> Optional[RequestModel]:
        logger.info("Looking for request in database...%s", str(request_id))
        response = self.ddb.get_item(
            TableName=self.environment.request_table_name,
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

    def get_user_by_unique_id(self, unique_user_id: str) -> Optional[UserModel]:
        logger.info("Requesting user by unique user id: %s", unique_user_id)
        response = self.ddb.get_item(
            TableName=self.environment.user_table_name,
            Key={
                "unique_user_id": {
                    "S": unique_user_id
                }
            }
        )
        logger.info("Response from 'Dynamo': %s", response)
        return response.get("Item")

    def get_user_by_google_user_id(self, google_user_id: str) -> Optional[UserModel]:
        logger.info("Requesting user by google_user_id: %s", google_user_id)
        response = self.ddb.query(
            TableName=self.environment.user_table_name,
            IndexName=self.environment.google_user_id_index_name,
            KeyConditionExpression="google_user_id = :gui",
            ExpressionAttributeValues={
                ":gui": {"S": google_user_id}
            }
        )
        logger.info("Response from DynamoDB: %s", response)
        existing_users = response["Items"]
        if len(existing_users) > 1:
            logger.info("Multiple users found, something went wrong :(")
            raise IndexError("Multiple users error")
        elif len(existing_users) == 1:
            user = existing_users[0]
            logger.info("User found, unique_user_id: %s", str(user))
            return UserModel(**flatten_response(user))
        return None

    def save_user(self, new_user: UserModel) -> None:
        logger.info("Saving user to Dynamo: %s", str(new_user))
        self.ddb.put_item(
            TableName=self.environment.user_table_name,
            Item={
                "unique_user_id": {"S": new_user.unique_user_id},
                "google_user_id": {"S": new_user.google_user_id},
                "user_google_email": {"S": new_user.user_google_email},
                "creation_time_iso": {"S": new_user.creation_time_iso},
                "creation_time_timestamp": {"S": new_user.creation_time_timestamp}
            }
        )
        logger.info("User saved")

    def get_user_by_api_token(self, api_token: str) -> Optional[APITokenModel]:
        logger.info("Requesting gpu user by api token: %s", api_token)
        response = self.ddb.get_item(
            TableName=self.environment.api_token_table_name,
            Key={
                Metadata.APITokenTable.primary_key: {
                    "S": api_token
                }
            }
        )
        logger.info("Response from 'Dynamo': %s", response)
        item = response.get("Item")
        if item:
            return APITokenModel(**flatten_response(item))
