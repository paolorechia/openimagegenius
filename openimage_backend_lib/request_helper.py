import json

def build_error_message_body(error):
    return json.dumps({
        "message_type": "error",
        "data": error
    })
