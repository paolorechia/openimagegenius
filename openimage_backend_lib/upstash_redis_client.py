import os
from requests import Session

class RedisEnvironmentInfo:
    def __init__(self) -> None:
        # tables
        self.api_url = os.environ["REDIS_URL"]
        self.token = os.environ["REDIS_TOKEN"]
        self.prefix = os.environ["REDIS_PREFIX"]


class RedisUpstashRestAPIClient:
    def __init__(self, environment: RedisEnvironmentInfo, http_session: Session) -> None:
        self.env = environment
        self.session.headers = {
            "Authorization": f"Bearer {self.env.token}"
        }

    def set(self, key, value):
        self.session.get(f"{self.api_}/set/{self.prefix}-{key}/{value}")

    def incr(self, key):
        self.session.get(f"{self.api_}/incr/{self.prefix}-{key}")

    def expire(self, key, ttl_seconds):
        self.session.get(f"{self.api_}/expire/{self.prefix}-{key}/{ttl_seconds}")

    def get(self, key, value):
        self.session.get(f"{self.api_}/get/{self.prefix}-{key}/{value}")

    

        