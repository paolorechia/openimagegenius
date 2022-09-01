import asyncio
import websockets
import json
import pytest
from unittest.mock import patch
import os
import boto3
import time

from openimage_backend_lib import repository as repo_module

test_endpoint = "wss://dev.ws-gpus.openimagegenius.com"
with open(".ws_secret_pass", "r") as fp:
    ws_secret_pass = fp.read().strip()

request_event = json.dumps({
    "message_type": "status",
    "data": "ready"
})


@patch.dict(os.environ, {

}, clear=True)
@pytest.mark.asyncio
async def test_connection_replies():
    async with websockets.connect(test_endpoint, extra_headers={
            "Authorization": ws_secret_pass
    }) as websocket:
        dynamodb_client = boto3.client("dynamodb")
        os.environ["USER_TABLE_NAME"] = "dummy"
        os.environ["REQUEST_TABLE_NAME"] = "dummy"
        os.environ["API_TOKEN_TABLE_NAME"] = "api-token-table-dev"
        os.environ["GOOGLE_USER_ID_INDEX_NAME"] = "dummy"
        os.environ["USER_GOOGLE_EMAIL_INDEX_NAME"] = "dummy"
        os.environ["REQUEST_UNIQUE_USER_ID_INDEX"] = "dummy"
        os.environ["API_TOKEN_UNIQUE_USER_ID_INDEX"] = "dummy"
        environment = repo_module.EnvironmentInfo()
        repository = repo_module.Repository(dynamodb_client, environment)
        gpu_user = repository.get_user_by_api_token(ws_secret_pass)
        assert gpu_user.node_status == "connecting"

        await websocket.send(request_event)
        time.sleep(0.2)

        gpu_user = repository.get_user_by_api_token(ws_secret_pass)
        assert gpu_user.node_status == "ready"

    time.sleep(0.2)
    gpu_user = repository.get_user_by_api_token(ws_secret_pass)
    assert gpu_user.node_status == "disconnected"
