import os
from requests import Session

class RedisEnvironmentInfo:
    def __init__(self) -> None:
        # tables
        self.api_url = os.environ["REDIS_URL"]
        self.token = os.environ["REDIS_TOKEN"]
        self.prefix = os.environ["REDIS_PREFIX"]


class RedisUpstashRestAPIClient:
    def __init__(self, environment: RedisEnvironmentInfo, http_session: Session, return_type = int) -> None:
        self.env = environment
        self.session = http_session
        self.session.headers = {
            "Authorization": f"Bearer {self.env.token}"
        }
        self.return_type = return_type

    def _call_api(self, url, method="get"):
        api = getattr(self.session, method)
        response = api(url)
        response.raise_for_status()
        r = response.json()["result"]
        if r is None:
            return None
        if r == "OK":
            return 0
        return self.return_type(r)


    def del_(self, key):
        return self._call_api(
            f"{self.env.api_url}/del/{self.env.prefix}-{key}"
        )

    def set(self, key, value):
        return self._call_api(
            f"{self.env.api_url}/set/{self.env.prefix}-{key}/{value}"
        )

    def incr(self, key):
        return self._call_api(
            f"{self.env.api_url}/incr/{self.env.prefix}-{key}"
        )

    def expire(self, key, ttl_seconds):
        return self._call_api(
            f"{self.env.api_url}/expire/{self.env.prefix}-{key}/{ttl_seconds}")

    def get(self, key):
        return self._call_api(
            f"{self.env.api_url}/get/{self.env.prefix}-{key}")

    

        