from request_handler import request_handler
from connection_handler import connection_handler
from authorization_handler import authorization_handler
from database_streaming import update_handler
from default_handler import default_handler


def connection(event, context):
    return connection_handler(event, context)


def authorization(event, context):
    return authorization_handler(event, context)


def default(event, context):
    return default_handler(event, context)


def request(event, context):
    return request_handler(event, context)


def update(event, context):
    return update_handler(event, context)
