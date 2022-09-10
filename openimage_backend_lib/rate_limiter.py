import os

from requests import Session

from openimage_backend_lib.upstash_redis_client import (
    RedisEnvironmentInfo, RedisUpstashRestAPIClient
)


class RateLimiter:
    def __init__(self, redis: RedisUpstashRestAPIClient, number_of_requests_limit: int, reset_period_in_seconds: int):
        self.period = reset_period_in_seconds
        self.limit = number_of_requests_limit
        self.redis = redis

    def should_allow(self, key) -> bool:
        current_requests = self.redis.get(key)
        if current_requests is None:
            self.redis.set(key, 1)
            self.redis.expire(key, self.period)
            return True
        if current_requests <= self.limit:
            self.redis.incr(key)
            return True
        return False


limiter = None


def get_limiter():
    global limiter
    if limiter:
        return limiter
    redis_env = RedisEnvironmentInfo()
    limit = int(os.environ["REDIS_LIMIT"])
    period = int(os.environ["REDIS_PERIOD"])
    redis_http_session = Session()
    limiter = RateLimiter(
        redis=RedisUpstashRestAPIClient(
            environment=redis_env, http_session=redis_http_session),
        number_of_requests_limit=limit,
        reset_period_in_seconds=period
    )
    return limiter
