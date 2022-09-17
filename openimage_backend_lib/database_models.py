from lib2to3.pgen2.token import OP
from pydantic import BaseModel
from typing import Optional

LAMBDA_DEFAULT_QUOTA_LIMIT = 1000


class Metadata:
    class UserTable:
        primary_key = "unique_user_id"

    class RequestTable:
        primary_key = "request_id"

    class APITokenTable:
        primary_key = "api_token"

    class ConnectionTable:
        primary_key = "connection_id"


class ConnectionModel(BaseModel):
    connection_id: str
    authorized: Optional[str] = "unverified"
    unique_user_id: Optional[str] = ""
    ip_address: Optional[str] = ""


class UserModel(BaseModel):
    unique_user_id: str
    google_user_id: str
    user_google_email: str
    creation_time_iso: str
    creation_time_timestamp: str
    connection_id: Optional[str] = ""
    connection_status: Optional[str] = "disconnected"


class APITokenModel(BaseModel):
    api_token: str
    unique_user_id: str
    connection_id: Optional[str] = ""
    node_status: Optional[str] = ""
    update_time_iso: Optional[str] = ""
    update_time_timestamp: Optional[str] = ""
    quota_limit: Optional[int] = -1
    number_requests: Optional[int] = -1


class RequestModel(BaseModel):
    request_id: str
    requester_unique_user_id: str
    request_type: str
    data: str
    request_status: str
    creation_time_iso: str
    creation_time_timestamp: str
    update_time_iso: str
    update_time_timestamp: str
    gpu_user_id: Optional[str] = ""
    s3_url: Optional[str] = ""
    small_tumbnail_s3_path: Optional[str] = ""
    medium_thumbnail_s3_path: Optional[str] = ""


class LambdaAvailabilityModel(APITokenModel):
    api_token: str = "lambda"
    unique_user_id: str = "lambda"
    connection_id: Optional[str] = "lambda"
    node_status: Optional[str] = "lambda"
    update_time_iso: Optional[str] = ""
    update_time_timestamp: Optional[str] = ""
    quota_limit: Optional[int] = LAMBDA_DEFAULT_QUOTA_LIMIT
    number_requests: Optional[int] = 0


REQUEST_TYPES = frozenset(["prompt", "get_requests"])
