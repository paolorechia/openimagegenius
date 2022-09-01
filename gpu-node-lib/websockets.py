import json


class WebsocketsClient:
    def __init__(self, ws_connection):
        self.ws_connection = ws_connection

    async def send_initializing_state(self):
        return await self.ws_connection.send(json.dumps({
            "message_type": "status",
            "data": "initializing"
        }))

    async def send_busy_state(self):
        return await self.ws_connection.send(json.dumps({
            "message_type": "status",
            "data": "busy"
        }))

    async def send_ready_state(self, vram):
        return await self.ws_connection.send(json.dumps({
            "message_type": "status",
            "data": "ready"
        }))

    async def send_ack_message(self):
        return await self.ws_connection.send(json.dumps({
            "message_type": "acknowledge",
            "data": ""
        }))

    async def send_error_message(self, error_message):
        return await self.ws_connection.send(json.dumps({
            "message_type": "error",
            "data": error_message
        }))

    async def send_job_completed(self, request_id):
        return await self.ws_connection.send(json.dumps({
            "message_type": "job_completed",
            "data": request_id
        }))

    async def send_job_failed(self, request_id):
        return await self.ws_connection.send(json.dumps({
            "message_type": "job_failed",
            "data": request_id
        }))
