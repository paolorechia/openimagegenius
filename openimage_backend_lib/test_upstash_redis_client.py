import requests
from time import sleep
import pytest
from upstash_redis_client import RedisUpstashRestAPIClient, RedisEnvironmentInfo

TEST_PREFIX = "some-test-prefix"
TEST_KEY = "123456-abcdefg-123456-abcdefg-123456"

@pytest.fixture()
def redis_client():
    env = RedisEnvironmentInfo()
    env.prefix = TEST_PREFIX
    yield RedisUpstashRestAPIClient(RedisEnvironmentInfo(), requests.Session())


def test_redis_ops(redis_client):
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
