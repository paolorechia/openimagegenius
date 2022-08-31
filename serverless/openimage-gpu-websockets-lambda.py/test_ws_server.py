import asyncio
import websockets
import json
import pytest



test_endpoint = "wss://dev.ws-gpus.openimagegenius.com"
with open(".ws_secret_pass", "r") as fp:
        ws_secret_pass = fp.read().strip()

request_event = json.dumps({
        "action": "request",
        "request_type": "prompt",
        "data": "As astronaut cat"
})

@pytest.mark.asyncio
async def test_connection_replies():
        async with websockets.connect(test_endpoint, extra_headers={
                "Authorization": ws_secret_pass
        }) as websocket:
                await websocket.send(request_event)
                response = await websocket.recv()
                print("Got response:", response)
                assert response == "Default"
