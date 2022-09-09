from enum import unique
from .date_helper import get_iso_and_timestamp_now
from .database_models import Metadata, RequestModel, UserModel, APITokenModel, ConnectionModel
from typing import Optional, List
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
        self.connection_table = os.environ["CONNECTION_TABLE_NAME"]
        # indices
        self.google_user_id_index_name = os.environ["GOOGLE_USER_ID_INDEX_NAME"]
        self.user_google_email_index_name = os.environ["USER_GOOGLE_EMAIL_INDEX_NAME"]
        self.request_unique_user_id_index = os.environ["REQUEST_UNIQUE_USER_ID_INDEX"]
        self.api_token_unique_user_id_index = os.environ["API_TOKEN_UNIQUE_USER_ID_INDEX"]
        self.connection_unique_user_id_index = os.environ["CONNECTION_UNIQUE_USER_ID_INDEX"]
        self.connection_ip_address_index = os.environ["CONNECTION_IP_ADRESS_INDEX"]


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

    def get_connection_by_id(self, connection_id) -> Optional[ConnectionModel]:
        logger.info("Getting connection: %s", connection_id)
        response = self.ddb.get_item(
            TableName=self.environment.connection_table,
            Key={Metadata.ConnectionTable.primary_key: {"S": connection_id}}
        )
        logger.info("Dynamo response: %s", response)
        item = response.get("Item")
        if not item:
            return None
        return ConnectionModel(**flatten_response(item))

    def delete_connection(self, connection_id) -> Optional[ConnectionModel]:
        logger.info("Deleting connection: %s", connection_id)
        response = self.ddb.delete_item(
            TableName=self.environment.connection_table,
            Key={Metadata.ConnectionTable.primary_key: {"S": connection_id}}
        )
        logger.info("Dynamo response: %s", response)

    def add_connection(self, connection_id, ip_address):
        logger.info("Adding connection :%s", connection_id)
        response = self.ddb.put_item(
            TableName=self.environment.connection_table,
            Item={
                Metadata.ConnectionTable.primary_key: {"S": connection_id},
                "authorized": {"S": "unverified"},
                "unique_user_id": {"S": "anonymous"},
                "ip_address": {"S": ip_address}
            }
        )
        logger.info("Dynamo response: %s", response)

    def update_connection(self, connection_id: str, authorized: str, unique_user_id: str):
        logger.info("Updating connection: %s to state %s for user %s",
                    connection_id, authorized, unique_user_id)
        response = self.ddb.update_item(
            TableName=self.environment.connection_table,
            Key={
                Metadata.ConnectionTable.primary_key: {"S": connection_id}
            },
            UpdateExpression="SET authorized = :aut, unique_user_id = :uui",
            ExpressionAttributeValues={
                ":aut": {"S": authorized},
                ":uui": {"S": unique_user_id},
            }
        )
        logger.info("Dynamo DB response: %s", response)

    def get_request(self, request_id) -> Optional[RequestModel]:
        logger.info("Looking for request in database...%s", str(request_id))
        response = self.ddb.get_item(
            TableName=self.environment.request_table_name,
            Key={
                Metadata.RequestTable.primary_key: {"S": request_id},
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

    def set_unique_user_id_for_request(self, request_id: str, unique_user_id: str) -> None:
        logger.info("Setting gpu_user_id: %s on request: %s",
                    unique_user_id, request_id)

        iso, ts = get_iso_and_timestamp_now()
        self.ddb.update_item(
            TableName=self.environment.request_table_name,
            Key={
                Metadata.RequestTable.primary_key: {
                    "S": request_id
                }
            },
            UpdateExpression="SET gpu_user_id = :gui, request_status = :rs, update_time_iso = :uti, update_time_timestamp = :utt",
            ExpressionAttributeValues={
                ":gui": {"S": unique_user_id},
                ":rs": {"S": "assigned"},
                ":uti": {"S": iso},
                ":utt": {"S": ts},
            }
        )

    def set_failed_status_for_request(self, request_id: str) -> None:
        logger.info("Setting status to 'failed' on request: %s", request_id)

        iso, ts = get_iso_and_timestamp_now()

        self.ddb.update_item(
            TableName=self.environment.request_table_name,
            Key={
                Metadata.RequestTable.primary_key: {
                    "S": request_id
                }
            },
            UpdateExpression="SET request_status = :rs, update_time_iso = :uti, update_time_timestamp = :utt",
            ExpressionAttributeValues={
                ":rs": {"S": "failed"},
                ":uti": {"S": iso},
                ":utt": {"S": ts},
            }
        )

    def set_s3_path_for_request(self, request_id: str, s3_url: str) -> None:
        logger.info("Setting s3_url: %s on request: %s",
                    s3_url, request_id)

        iso, ts = get_iso_and_timestamp_now()

        self.ddb.update_item(
            TableName=self.environment.request_table_name,
            Key={
                Metadata.RequestTable.primary_key: {
                    "S": request_id
                }
            },
            UpdateExpression="SET s3_url = :su, request_status = :rs, update_time_iso = :uti, update_time_timestamp = :utt",
            ExpressionAttributeValues={
                ":su": {"S": s3_url},
                ":rs": {"S": "completed"},
                ":uti": {"S": iso},
                ":utt": {"S": ts},
            }
        )

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
        user = response.get("Item")
        if user:
            return UserModel(**flatten_response(user))
        return None

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

    def set_connection_id_for_user(self, unique_user_id: str, connection_id: str) -> None:
        logger.info("Setting connection_id: %s for user: %s",
                    connection_id, unique_user_id)

        self.ddb.update_item(
            TableName=self.environment.user_table_name,
            Key={
                Metadata.UserTable.primary_key: {
                    "S": unique_user_id
                }
            },
            UpdateExpression="SET connection_id = :coni, connection_status = :cons",
            ExpressionAttributeValues={
                ":coni": {"S": connection_id},
                ":cons": {"S": "connected"}
            }
        )

    def set_disconnect_for_user(self, unique_user_id: str) -> None:
        logger.info("Setting user %s as disconnected", unique_user_id)

        self.ddb.update_item(
            TableName=self.environment.user_table_name,
            Key={
                Metadata.UserTable.primary_key: {
                    "S": unique_user_id
                }
            },
            UpdateExpression="SET connection_status = :cons",
            ExpressionAttributeValues={
                ":cons": {"S": "disconnected"}
            }
        )

    def scan_api_tokens(self) -> List[APITokenModel]:
        logger.info("Scanning gpu nodes")
        response = self.ddb.scan(
            TableName=self.environment.api_token_table_name,
            Select="ALL_ATTRIBUTES"
        )
        logger.info("Response: %s", response)
        nodes = response.get("Items")
        if not nodes:
            return []

        return [
            APITokenModel(**flatten_response(node))
            for node in nodes
        ]

    def get_user_by_api_token(self, api_token: str) -> Optional[APITokenModel]:
        logger.info("Requesting gpu user by api token: %s*****",
                    api_token[0:5])
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

    def set_connection_id_for_token(self, api_token: str, connection_id):
        logger.info("Setting connection ID: %s on token: %s*****",
                    connection_id, api_token[0:5])

        self.ddb.update_item(
            TableName=self.environment.api_token_table_name,
            Key={
                Metadata.APITokenTable.primary_key: {
                    "S": api_token
                }
            },
            UpdateExpression="SET connection_id = :cid",
            ExpressionAttributeValues={
                ":cid": {"S": connection_id}
            }
        )

    def set_status_for_token(self, api_token: str, status):
        logger.info("Setting status ID: %s on token: %s*****",
                    status, api_token[0:5])

        iso, ts = get_iso_and_timestamp_now()

        self.ddb.update_item(
            TableName=self.environment.api_token_table_name,
            Key={
                Metadata.APITokenTable.primary_key: {
                    "S": api_token
                }
            },
            UpdateExpression="SET node_status = :sts, update_time_iso = :uti, update_time_timestamp = :utt",
            ExpressionAttributeValues={
                ":sts": {"S": status},
                ":uti": {"S": iso},
                ":utt": {"S": ts},
            }
        )

    def query_user_requests(self, unique_user_id: str):
        logger.info("Querying requests for user: %s", unique_user_id)

        response = self.ddb.query(
            TableName=self.environment.request_table_name,
            IndexName=self.environment.request_unique_user_id_index,
            KeyConditionExpression="requester_unique_user_id = :uui",
            ExpressionAttributeValues={
                ":uui": {"S": unique_user_id}
            }
        )

        logger.info("Got back as response: %s",  response)
        items = response.get("Items", [])
        parsed_response = []
        for item in items:
            parsed_response.append(RequestModel(
                **flatten_response(item)))
        return parsed_response
