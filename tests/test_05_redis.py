"""
Test Redis cache functionality.

Tests that data is successfully written to and read from Redis cache.

Tests three representative methods:
- stations_list: long response (tests large data handling in Redis)
- schedule: with pagination (tests paginated response caching in Redis)
- carrier: without pagination (tests simple response caching in Redis)

The choice of these three methods is based on representativeness:
- stations_list: returns a long response, testing Redis cache with large data volumes
- schedule: uses pagination, testing Redis cache with paginated responses
- carrier: does not use pagination, testing Redis cache with simple responses

WARNING: This test requires YARASP_API_KEY environment variable to be set.
The API key can be provided via:
- Environment variable: export YARASP_API_KEY='your-api-key'
- .env file: Create .env file in project root with YARASP_API_KEY=your-api-key
If YARASP_API_KEY is not set, all tests will be skipped.

NOTE: Tests use a separate Redis database (default: db=1) to avoid conflicts
with other Redis data. Set YARASP_REDIS_TEST_DB environment variable to use
a different database number.

Configuration:
    YARASP_REDIS_TEST_DB - Redis database number for tests (default: 1)
    YARASP_REDIS_NO_FLUSH - Set to "1" or "true" to disable flushdb() calls (default: flushdb enabled)

Running tests:
    # Run all Redis cache tests
    uv run pytest tests/test_05_redis.py

    # Run only stations_list test
    uv run pytest tests/test_05_redis.py -m stations_list

    # Run only schedule test
    uv run pytest tests/test_05_redis.py -m schedule

    # Run only carrier test
    uv run pytest tests/test_05_redis.py -m carrier

    # Run multiple specific tests
    uv run pytest tests/test_05_redis.py -m "schedule or carrier"

    # Run carrier test without flushing Redis database (preserves cache between runs)
    YARASP_REDIS_NO_FLUSH=1 uv run pytest tests/test_05_redis.py -m carrier
"""

import os
from pathlib import Path
import pytest

# Load .env file BEFORE importing yarasp to ensure YARASP_API_KEY is available
def _load_env_file():
    """Load environment variables from .env file if it exists."""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and value:
                        os.environ.setdefault(key, value)

# Load .env file early
_load_env_file()

from yarasp import YaraspClient
import hishel
from scripts.fixture_requests import (
    SCHEDULE_REQUEST,
    CARRIER_REQUEST,
    STATIONS_LIST_REQUEST,
)


def _api_key_available() -> bool:
    """Check if YARASP_API_KEY is available."""
    # .env file is already loaded at module level
    return bool(os.environ.get("YARASP_API_KEY"))


def _redis_available() -> bool:
    """Check if Redis is available and accessible."""
    try:
        import redis
    except ImportError:
        return False
    
    try:
        # Use test database (default: db=1) for availability check
        db_number = int(os.environ.get("YARASP_REDIS_TEST_DB", "1"))
        redis_client = redis.Redis(
            host="0.0.0.0", 
            port=6379, 
            db=db_number, 
            decode_responses=False, 
            socket_connect_timeout=1
        )
        redis_client.ping()
        redis_client.close()
        return True
    except (redis.ConnectionError, redis.TimeoutError, Exception):
        return False


pytestmark = [
    pytest.mark.skipif(
        not _api_key_available(),
        reason="YARASP_API_KEY environment variable is not set. Set it via environment variable or .env file.",
    ),
    pytest.mark.skipif(
        not _redis_available(),
        reason="Redis is not running or not accessible at 0.0.0.0:6379",
    ),
]


@pytest.fixture
def redis_client():
    """Create Redis client for cache storage using separate test database."""
    import redis
    
    # Use separate database for tests (default: db=1) to avoid conflicts
    db_number = int(os.environ.get("YARASP_REDIS_TEST_DB", "1"))
    client = redis.Redis(
        host="0.0.0.0", 
        port=6379, 
        db=db_number, 
        decode_responses=False
    )
    
    # Check if flushdb should be disabled
    no_flush = os.environ.get("YARASP_REDIS_NO_FLUSH", "").lower() in ("1", "true", "yes")
    
    # Clear test database before each test to ensure clean state
    if not no_flush:
        client.flushdb()
    yield client
    # Clean up after test
    if not no_flush:
        client.flushdb()
    client.close()


@pytest.fixture
def client(redis_client):
    """Create YaraspClient with Redis storage."""
    storage = hishel.RedisStorage(client=redis_client)
    return YaraspClient(cache_storage=storage)


@pytest.mark.stations_list
def test_redis_cache_stations_list(client):
    """
    Test Redis cache for stations_list endpoint.
    
    stations_list returns a long response, testing large data handling in Redis cache.
    """
    # First request: may be from cache if noflush is enabled and data exists
    result1 = client.get(
        STATIONS_LIST_REQUEST["endpoint"], params=STATIONS_LIST_REQUEST["params"]
    )
    assert isinstance(result1, dict)
    first_from_cache = client.last_response_from_cache
    
    # Second request: should read from cache
    result2 = client.get(
        STATIONS_LIST_REQUEST["endpoint"], params=STATIONS_LIST_REQUEST["params"]
    )
    assert client.last_response_from_cache is True, "Second request should be from cache"
    assert isinstance(result2, dict)
    
    # Compare full equality of written and read data
    assert result1 == result2, "Cached data should match original data"
    
    # If first request was not from cache, verify that second is from cache
    # (if first was from cache due to noflush, that's also valid - cache is working)
    if not first_from_cache:
        # First request wrote to cache, second should read from cache
        assert client.last_response_from_cache is True


@pytest.mark.schedule
def test_redis_cache_schedule(client):
    """
    Test Redis cache for schedule endpoint.
    
    schedule uses pagination, testing paginated response caching in Redis.
    """
    # First request: may be from cache if noflush is enabled and data exists
    result1 = client.get(
        SCHEDULE_REQUEST["endpoint"], params=SCHEDULE_REQUEST["params"]
    )
    assert isinstance(result1, dict)
    first_from_cache = client.last_response_from_cache
    
    # Second request: should read from cache
    result2 = client.get(
        SCHEDULE_REQUEST["endpoint"], params=SCHEDULE_REQUEST["params"]
    )
    assert client.last_response_from_cache is True, "Second request should be from cache"
    assert isinstance(result2, dict)
    
    # Compare full equality of written and read data
    assert result1 == result2, "Cached data should match original data"
    
    # If first request was not from cache, verify that second is from cache
    # (if first was from cache due to noflush, that's also valid - cache is working)
    if not first_from_cache:
        # First request wrote to cache, second should read from cache
        assert client.last_response_from_cache is True


@pytest.mark.carrier
def test_redis_cache_carrier(client):
    """
    Test Redis cache for carrier endpoint.
    
    carrier does not use pagination, testing simple response caching in Redis.
    """
    # First request: may be from cache if noflush is enabled and data exists
    result1 = client.get(
        CARRIER_REQUEST["endpoint"], params=CARRIER_REQUEST["params"]
    )
    assert isinstance(result1, dict)
    first_from_cache = client.last_response_from_cache
    
    # Second request: should read from cache
    result2 = client.get(
        CARRIER_REQUEST["endpoint"], params=CARRIER_REQUEST["params"]
    )
    assert client.last_response_from_cache is True, "Second request should be from cache"
    assert isinstance(result2, dict)
    
    # Compare full equality of written and read data
    assert result1 == result2, "Cached data should match original data"
    
    # If first request was not from cache, verify that second is from cache
    # (if first was from cache due to noflush, that's also valid - cache is working)
    if not first_from_cache:
        # First request wrote to cache, second should read from cache
        assert client.last_response_from_cache is True

