from pydantic import BaseModel
from typing import Optional


class Metadata:
    class UserTable:
        primary_key = "unique_user_id"

    class RequestTable:
        primary_key = "request_id"

    class APITokenTable:
        primary_key = "api_token"


class UserModel(BaseModel):
    unique_user_id: str
    google_user_id: str
    user_google_email: str
    creation_time_iso: str
    creation_time_timestamp: str


class APITokenModel(BaseModel):
    api_token: str
    unique_user_id: str
    node_status: Optional[str] = ""


class RequestModel(BaseModel):
    request_id: str
    requester_unique_user_id: str
    request_type: str
    data: str
    status: str
    creation_time_iso: str
    creation_time_timestamp: str
    update_time_iso: str
    update_time_timestamp: str


REQUEST_TYPES = frozenset(["prompt"])
