import json
from dataclasses import dataclass

@dataclass
class RequestImageGenFromPrompt:
    request_id: str
    prompt: str
    s3_url: str
    s3_fields: dict

def message_parser(message: str):
    # Returns tuple parsed, type_, error_message
    type_ = None
    parsed = None

    if message is None:
        return None, None, "Empty message received"

    if type(message) != str:
        return None, type(message), "Non string message"

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
