import json
import logging
import os

import boto3
import pydash as _
import requests

from openimage_backend_lib import repository as repo_module
from openimage_backend_lib import telegram

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

environment = repo_module.EnvironmentInfo()

telegram_client = telegram.get_telegram(requests.Session())

dynamodb_client = boto3.client("dynamodb")
api_client = boto3.client('apigatewaymanagementapi')
lambda_client = boto3.client("lambda")

repository = repo_module.Repository(dynamodb_client, environment)

retrying_lambda_name = os.environ["RETRYING_LAMBDA_NAME"]


def connection(event, context):
    """"
    example_request = {
        'headers': {
            'Authorization': 'AAAAA',
            'Host': 'dev.ws-api.openimagegenius.com',
        },
        'requestContext': {
            'routeKey': '$connect',
            'authorizer': {
                'api_token': '123',
                'unique_user_id': '17b86c9e-9bac-4f2f-b10a-68619baba577',
                'integrationLatency': 111
            },
            'eventType': 'CONNECT',
            'extendedRequestId': 'Xux7aHf-FiAFqTg=',
            'requestTime': '31/Aug/2022:13:34:52 +0000',
            'messageDirection': 'IN',
            'stage': 'dev',
            'connectedAt': 1661952892072,
            'requestTimeEpoch': 1661952892073,
            'identity': {'userAgent': 'Python/3.8 websockets/10.3', 'sourceIp': '93.193.144.114'},
            'requestId': 'Xux7aHf-FiAFqTg=',
            'domainName': 'dev.ws-api.openimagegenius.com',
            'connectionId': 'Xux7aeaAFiACHZQ=',
            'apiId': '20kmit0mc5'
        },
        'isBase64Encoded': False
    }
    """
    logger.info("Event: %s", event)
    api_token = _.get(event, "requestContext.authorizer.api_token")
    connection_id = _.get(event, "requestContext.connectionId")
    repository.set_connection_id_for_token(api_token, connection_id)
    repository.set_status_for_token(api_token, "connecting")
    telegram_client.send_message(f"GPU node {api_token[0:5]}** is connecting")
    lambda_client.invoke(
        FunctionName=retrying_lambda_name,
        InvocationType="Event",
        LogType="None"
    )
    return {"statusCode": 200, "body": "Connected"}


def default(event, context):
    print("Event", event)
    print("contex", context)
    return {"statusCode": 200, "body": "Default"}


def disconnect(event, context):
    print("Event", event)
    api_token = _.get(event, "requestContext.authorizer.api_token")
    repository.set_status_for_token(api_token, "disconnected")
    telegram_client.send_message(
        f"GPU node {api_token[0:5]}** is disconnecting")
    return {"statusCode": 200, "body": "disconnected"}


def status(event, context):
    print("Event", event)
    print("contex", context)
    json_body = json.loads(event["body"])
    status_ = json_body["data"]
    api_token = _.get(event, "requestContext.authorizer.api_token")
    repository.set_status_for_token(api_token, status_)
    telegram_client.send_message(
        f"GPU node {api_token[0:5]}** changed to status {status_}")
    return {"statusCode": 200, "body": "Status Acknowledged."}


def retrying(event, context):
    logger.info("Event: %s", event)
    # TODO: query DDB
    # TODO: push to SQS
    # sqs_client.send_message(
    #     QueueUrl=queue_url,
    #     MessageBody=json.dumps({
    #         "request_type": request.request_type,
    #         "data": request.data,
    #         "unique_request_id": request_id,
    #         "requester_unique_user_id": request.unique_user_id,
    #     }),
    # )
