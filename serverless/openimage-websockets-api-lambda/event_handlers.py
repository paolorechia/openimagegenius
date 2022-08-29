

def connect(event, context):
    print("Event", event)
    print("contex", context)
    return {"statusCode": 200, "body": "You're authorized :)"}

def foo(event, context):
    print("Event", event)
    print("contex", context)
    return {"statusCode": 200, "body": "Foo!"}

def default(event, context):
    print("Event", event)
    print("contex", context)
    return {"statusCode": 200, "body": "Default"}
