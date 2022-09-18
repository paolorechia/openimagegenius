import json

from gpu_node_lib.dataclasses import RequestImageGenFromPrompt

MAX_MSG_SIZE = 4096


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


def message_parser(message: str):
    # Returns tuple parsed, type_, error_message
    type_ = None
    parsed = None

    if message is None:
        return None, None, "Empty message received"

    if type(message) != str:
        return None, type(message), "Non string message"

    if len(message) > MAX_MSG_SIZE:
        return None, type(message), "Message exceeds size limit"

    try:
        parsed = json.loads(message)
    except json.JSONDecodeError as excp:
        return None, type(excp), "Message is not JSON encoded"

    try:
        message_type = parsed["message_type"]
    except KeyError as excp:
        return None, type(excp), "key 'message_type' missing in JSON"

    # Parse specific message types
    try:
        if message_type == "request_prompt":
            prompt = parsed["prompt"]
            s3_url = parsed["s3_url"]
            s3_fields = parsed["s3_fields"]
            request_id = parsed["request_id"]
            return RequestImageGenFromPrompt(
                request_id,
                prompt,
                s3_url,
                s3_fields
            ), RequestImageGenFromPrompt, None

        elif message_type == "heartbeat":
            pass
    except KeyError as excp:
        return None, type(excp), f"key missing in JSON: {str(excp)}"

    return None, None, ValueError(f"Unrecognized message_type: {message_type}")
