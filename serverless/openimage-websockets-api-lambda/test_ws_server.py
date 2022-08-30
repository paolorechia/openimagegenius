import asyncio
import websockets
import json


test_endpoint = "wss://dev.ws-api.openimagegenius.com"
with open(".ws_secret_pass", "r") as fp:
        ws_secret_pass = fp.read().strip()

request_event = json.dumps({
        "action": "request"
})
async def hello():
    async with websockets.connect(test_endpoint, extra_headers={
            "Authorization": ws_secret_pass
    }) as websocket:
        print("Connected!")
        # await websocket.send(request_event)
        # response = await websocket.recv()
        # print("Got response", response)

asyncio.run(hello())

