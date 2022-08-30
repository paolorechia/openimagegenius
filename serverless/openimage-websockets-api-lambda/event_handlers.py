

def connection(event, context):
    print("Event", event)
    print("contex", context)
    return {"statusCode": 200, "body": "You're authorized :)"}

def default(event, context):
    print("Event", event)
    print("contex", context)
    return {"statusCode": 200, "body": "Default"}

def request(event, context):
    print("Event", event)
    print("contex", context)
    return {"statusCode": 200, "body": "Request Received"}
