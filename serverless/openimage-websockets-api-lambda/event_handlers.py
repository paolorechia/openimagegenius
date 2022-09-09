from authorization_handler import authorization_handler
from connect_handler import connect_handler
from database_streaming import update_handler
from default_handler import default_handler
from disconnect_handler import disconnect_handler
from request_handler import request_handler

def connect(event, context):
    return connect_handler(event, context)


def disconnect(event, context):
    return disconnect_handler(event, context)


def authorization(event, context):
    return authorization_handler(event, context)


def default(event, context):
    return default_handler(event, context)


def request(event, context):
    return request_handler(event, context)


def update(event, context):
    return update_handler(event, context)
