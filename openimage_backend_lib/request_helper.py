import json

def build_error_message_body(error):
    return json.dumps({
        "message_type": "error",
        "data": error
    })


def build_rate_limited_response():
    return json.dumps({
        "statusCode": 429,
        "body": '{"message": "Too many requests. Try again soon."}',
        }
    )