import os
import logging
from requests import Session

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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

    def _call_api(self, url, url_tail, method="get"):
        logger.info("Calling %s", url_tail)
        api = getattr(self.session, method)
        response = api(f"{url}/{url_tail}")
        response.raise_for_status()
        r = response.json()["result"]
        if r is None:
            return None
        if r == "OK":
            return 0
        return self.return_type(r)

    def del_(self, key):
        url_tail = f"del/{self.env.prefix}-{key}"
        return self._call_api(self.env.api_url, url_tail)

    def set(self, key, value):
        url_tail = f"set/{self.env.prefix}-{key}/{value}"
        return self._call_api(self.env.api_url, url_tail)

    def incr(self, key):
        url_tail = f"incr/{self.env.prefix}-{key}"
        return self._call_api(self.env.api_url, url_tail)

    def expire(self, key, ttl_seconds):
        url_tail = f"expire/{self.env.prefix}-{key}/{ttl_seconds}"
        return self._call_api(self.env.api_url, url_tail)

    def get(self, key):
        url_tail = f"get/{self.env.prefix}-{key}"
        return self._call_api(self.env.api_url, url_tail)
