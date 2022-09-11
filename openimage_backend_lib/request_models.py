from openimage_backend_lib import database_models as models
from pydantic import BaseModel, validator
from uuid import UUID
from typing import Dict, Any, Optional


class Request(BaseModel):
    data: str
    request_type: str
    unique_user_id: str

    @validator('request_type')
    def request_type_validator(cls, v):
        if v.lower() not in models.REQUEST_TYPES:
            raise ValueError(f"Request type {v} is not recognized.")
        return v

    @validator('unique_user_id')
    def check_if_valid_uuid_v4(cls, v):
        UUID(v, version=4)
        return v


class PromptRequest(Request):
    request_type: str = "prompt"

    @validator('request_type')
    def request_type_validator(cls, v):
        if v.lower() != "prompt":
            raise ValueError(f"Request type {v} is not recognized.")
        return v

    @validator('data')
    def max_length_1024(cls, v):
        if len(v) > 1024:
            raise ValueError("data exceeds the limit of 1024 characters.")
        return v


class PaginationRequestModel(BaseModel):
    last_evaluated_key: Optional[Dict[str, Any]] = None
    page_size: int = 20


class GetRequestsForUser(Request):
    data: PaginationRequestModel
    request_type: str = "get_requests"

    @validator('request_type')
    def request_type_validator(cls, v):
        if v.lower() != "get_requests":
            raise ValueError(f"Request type {v} is not recognized.")
        return v
