from openimage_backend_lib.upstash_redis_client import RedisUpstashRestAPIClient
import os

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
            return True
        return False

limiter = None
def get_limiter():
    if limiter:
        return limiter

    limit = os.environ["REDIS_LIMIT"]
    period = os.environ["REDIS_PERIOD"]
    limiter = RateLimiter(
        redis=RedisUpstashRestAPIClient(),
        number_of_requests_limit=limit,
        reset_period_in_seconds=period
    )
    return limiter
