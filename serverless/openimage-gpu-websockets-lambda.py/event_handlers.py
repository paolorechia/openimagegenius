
def connection(event, context):
    """"
    example_request = {
        'headers': {
            'Authorization': 'AAAAA',
            'Host': 'dev.ws-api.openimagegenius.com',
            'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
            'Sec-WebSocket-Key': 'WkQgPq2aaLgLt09qzhmA8g==',
            'Sec-WebSocket-Version': '13',
            'User-Agent': 'Python/3.8 websockets/10.3',
            'X-Amzn-Trace-Id': 'Root=1-630f637c-74d9e0581d71eb9d0ca0b056',
            'X-Forwarded-For': '93.193.144.114',
            'X-Forwarded-Port': '443',
            'X-Forwarded-Proto': 'https'
        },
        'multiValueHeaders': {
            'Authorization': ['AAAAA'],
            'Host': ['dev.ws-api.openimagegenius.com'],
            'Sec-WebSocket-Extensions': ['permessage-deflate; client_max_window_bits'],
            'Sec-WebSocket-Key': ['WkQgPq2aaLgLt09qzhmA8g=='],
            'Sec-WebSocket-Version': ['13'],
            'User-Agent': ['Python/3.8 websockets/10.3'],
            'X-Amzn-Trace-Id': ['Root=1-630f637c-74d9e0581d71eb9d0ca0b056'],
            'X-Forwarded-For': ['93.193.144.114'],
            'X-Forwarded-Port': ['443'],
            'X-Forwarded-Proto': ['https']
        },
        'requestContext': {
            'routeKey': '$connect',
            'authorizer': {
                'api_token': '123',
                'unique_user_id': '17b86c9e-9bac-4f2f-b10a-68619baba577',
                'integrationLatency': 111
            },
            'eventType': 'CONNECT',
            'extendedRequestId': 'Xux7aHf-FiAFqTg=',
            'requestTime': '31/Aug/2022:13:34:52 +0000',
            'messageDirection': 'IN',
            'stage': 'dev',
            'connectedAt': 1661952892072,
            'requestTimeEpoch': 1661952892073,
            'identity': {'userAgent': 'Python/3.8 websockets/10.3', 'sourceIp': '93.193.144.114'},
            'requestId': 'Xux7aHf-FiAFqTg=',
            'domainName': 'dev.ws-api.openimagegenius.com',
            'connectionId': 'Xux7aeaAFiACHZQ=',
            'apiId': '20kmit0mc5'
        },
        'isBase64Encoded': False
    }
    """
    print("Event", event)
    print("contex", context)
    return {"statusCode": 200, "body": "You're authorized :)"}


def default(event, context):
    print("Event", event)
    print("contex", context)
    return {"statusCode": 200, "body": "Default"}