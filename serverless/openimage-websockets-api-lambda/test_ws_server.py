import asyncio
import websockets
import json
import pytest
import functools

test_endpoint = "wss://dev.ws-api.openimagegenius.com"
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

get_requests_event = json.dumps({
    "action": "request",
    "request_type": "get_requests",
    "data": {
        "current_page": 0,
        "page_size": 20,
    }
})


async def authorized_connection():
    websocket = await websockets.connect(test_endpoint)
    await websocket.send(authorization_event)
    response = await websocket.recv()
    assert response == '{"message_type": "authorization", "data": "authorized"}'
    return websocket

@pytest.mark.regression
@pytest.mark.asyncio
async def test_request_rejected():
    async with websockets.connect(test_endpoint) as websocket:
        await websocket.send(request_event)
        response = await websocket.recv()
        print("Got response:", response)
        assert response == '{"message_type": "error", "data": "You\'re not authorized. Please send your valid token first."}'

@pytest.mark.regression
@pytest.mark.asyncio
async def test_authorized_request():
    websocket = await authorized_connection()
    try:
        await websocket.send(request_event)
        response = await websocket.recv()
        print("Got response:", response)
        j = json.loads(response)
        assert j["message_type"] == "request_accepted"
    finally:
        await websocket.close()


@pytest.mark.regression
@pytest.mark.asyncio
async def test_get_requests():
    websocket = await authorized_connection()
    try:
        await websocket.send(get_requests_event)
        response = await websocket.recv()
        print("Got response:", response)
        j = json.loads(response)
        assert j["message_type"] == "get_requests_response"
        print(j)
    finally:
        await websocket.close()


@pytest.mark.rate_limit_connect
@pytest.mark.asyncio
async def test_rate_limit_on_connect():
    limit = 30
    for i in range(limit + 1):
        try:
            print("Attempt ", i)
            websocket = await websockets.connect(test_endpoint)
        finally:
            websocket.close()
        

@pytest.mark.rate_limit_authorize
@pytest.mark.asyncio
async def test_rate_limit_on_authorize():
    try:
        websocket = await websockets.connect(test_endpoint)
        limit = 30
        for i in range(limit + 1):
                print("Attempt ", i)
                await websocket.send(authorization_event)
                response = await websocket.recv()
                assert response == '{"message_type": "authorization", "data": "authorized"}'
    finally:
        websocket.close()

@pytest.mark.rate_limit_request
@pytest.mark.asyncio
async def test_rate_limit_on_request():
    try:
        websocket = await authorized_connection()
        limit = 30
        for i in range(limit + 1):
                print("Attempt ", i)
                await websocket.send(request_event)
                response = await websocket.recv()
                print("Got response:", response)
                j = json.loads(response)
                assert j["message_type"] == "request_accepted"
    finally:
        websocket.close()

@pytest.mark.stress_test
@pytest.mark.asyncio
async def test_stress_test_jobs():
    async with websockets.connect(test_endpoint) as websocket:
        await websocket.send(authorization_event)
        response = await websocket.recv()
        assert response == '{"message_type": "authorization", "data": "authorized"}'
        for i in range(10):
            await websocket.send(request_event)
            response = await websocket.recv()
            print("Got response:", response)
            j = json.loads(response)
            assert j["message_type"] == "request_accepted"
