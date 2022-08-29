import asyncio
import websockets
import json

test_endpoint = "wss://dev.ws-api.openimagegenius.com"

foo_event = json.dumps({
        "action": "foo"
})
async def hello():
    async with websockets.connect(test_endpoint) as websocket:
        await websocket.send(foo_event)
        response = await websocket.recv()
        print("Got response", response)

asyncio.run(hello())

