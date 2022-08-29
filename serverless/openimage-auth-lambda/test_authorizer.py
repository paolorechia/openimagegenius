

def handler(event, context):
    print("Event", event)
    print("contex", context)
    return {"statusCode": 200, "body": "You're authorized :)"}
