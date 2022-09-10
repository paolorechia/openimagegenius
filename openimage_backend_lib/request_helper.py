import json


def build_error_message_body(error):
    return json.dumps({
        "message_type": "error",
        "data": error
    })


def build_rate_limited_response():
    return {
        "statusCode": 429,
        "body": json.dumps({
            "message_type": "rate_limit",
            "data": "Too many requests. Try again soon."
        }),
    }
