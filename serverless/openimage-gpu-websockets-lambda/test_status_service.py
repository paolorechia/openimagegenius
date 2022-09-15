import asyncio
import websockets
import json
import pytest
from unittest.mock import patch
import os
import boto3
import time

from openimage_backend_lib import repository as repo_module
from gpu_node_lib.websockets import WebsocketsClient

test_endpoint = "wss://dev.ws-gpus.openimagegenius.com"
with open(".ws_secret_pass", "r") as fp:
    ws_secret_pass = fp.read().strip()


@patch.dict(os.environ, {

}, clear=True)
@pytest.mark.asyncio
async def test_connection_replies():
    async with websockets.connect(test_endpoint, extra_headers={
            "Authorization": ws_secret_pass
    }) as websocket:
        time.sleep(0.5)
        ws_client = WebsocketsClient(ws_connection=websocket)
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

        await ws_client.send_initializing_state()
        time.sleep(1)
        gpu_user = repository.get_user_by_api_token(ws_secret_pass)
        assert gpu_user.node_status == "initializing"

        await ws_client.send_ready_state()
        time.sleep(0.5)

        gpu_user = repository.get_user_by_api_token(ws_secret_pass)
        assert gpu_user.node_status == "ready"

        await ws_client.send_busy_state()
        time.sleep(0.5)

        gpu_user = repository.get_user_by_api_token(ws_secret_pass)
        assert gpu_user.node_status == "busy"

    time.sleep(0.5)
    gpu_user = repository.get_user_by_api_token(ws_secret_pass)
    assert gpu_user.node_status == "disconnected"
