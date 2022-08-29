

def handler(event, context):
    print(event)
    return {"statusCode": 200, "message": "You're authorized :)"}
