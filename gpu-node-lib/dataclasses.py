import logging
from dataclasses import dataclass


@dataclass
class UserConfig:
    vram: int
    log_level: int = logging.INFO

@dataclass
class RequestImageGenFromPrompt:
    request_id: str
    prompt: str
    s3_url: str
    s3_fields: dict

