import requests
from time import sleep
import pytest
from unittest.mock import MagicMock
from upstash_redis_client import RedisUpstashRestAPIClient, RedisEnvironmentInfo

TEST_PREFIX = "some-test-prefix"
TEST_KEY = "123456-abcdefg-123456-abcdefg-123456"

@pytest.fixture()
def redis_client():
    with open(".REDIS_TOKEN", "r") as fp:
        token = fp.read().strip()
    with open(".REDIS_URL", "r") as fp:
        url = fp.read().strip()
    env = MagicMock()
    env.token = token
    env.api_url = url
    env.prefix = TEST_PREFIX
    yield RedisUpstashRestAPIClient(env, requests.Session())


def test_redis_ops(redis_client):
    result = redis_client.del_(TEST_KEY)

    result = redis_client.get(TEST_KEY)
    assert result is None
    
    redis_client.set(TEST_KEY, 1)
    result = redis_client.get(TEST_KEY)
    assert result == 1

    expire_time = 3
    redis_client.expire(TEST_KEY, expire_time)
    result = redis_client.get(TEST_KEY)
    assert result == 1

    sleep(expire_time)
    result = redis_client.get(TEST_KEY)
    assert result is None
