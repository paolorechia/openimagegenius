import asyncio
import websockets
import json
import pytest


test_endpoint = "wss://qwd67w7upb.execute-api.eu-central-1.amazonaws.com/dev"
with open(".ws_secret_pass", "r") as fp:
    ws_secret_pass = fp.read().strip()

authorization_event = json.dumps({
    "action": "authorize",
    "token": ws_secret_pass
})

request_event = json.dumps({
    "action": "request",
    "request_type": "prompt",
    "data": "As astronaut cat"
})


@pytest.mark.asyncio
async def test_request_rejected():
    async with websockets.connect(test_endpoint) as websocket:
        await websocket.send(request_event)
        response = await websocket.recv()
        print("Got response:", response)
        assert response == "You're not authorized. Please send your valid token first."

@pytest.mark.asyncio
async def test_authorization():
    async with websockets.connect(test_endpoint) as websocket:
        await websocket.send(authorization_event)
        response = await websocket.recv()
        print("Got response:", response)
        assert response == "authorized"

@pytest.mark.asyncio
async def test_authorized_request():
    async with websockets.connect(test_endpoint) as websocket:
        await websocket.send(authorization_event)
        response = await websocket.recv()
        assert response == "authorized"
        await websocket.send(request_event)
        response = await websocket.recv()
        print("Got response:", response)
        assert response == "Request Accepted."