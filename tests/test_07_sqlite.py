"""
Test SQLite cache and counter functionality.

This test verifies both caching functionality and API usage counter through SQLite.
It tests that:
1. Caching works correctly with SQLiteStorage (similar to test_02_cache)
2. API usage counter correctly stores usage data in SQLite database

Tests three representative methods by default:
- stations_list: long response (tests large data handling in SQLite)
- schedule: with pagination (tests paginated response caching in SQLite)
- carrier: without pagination (tests simple response caching in SQLite)

The choice of these three methods is based on representativeness:
- stations_list: returns a long response, testing SQLite cache with large data volumes
- schedule: uses pagination, testing SQLite cache with paginated responses
- carrier: does not use pagination, testing SQLite cache with simple responses

WARNING: This test requires YARASP_API_KEY environment variable to be set.
The API key can be provided via:
- Environment variable: export YARASP_API_KEY='your-api-key'
- .env file: Create .env file in project root with YARASP_API_KEY=your-api-key
If YARASP_API_KEY is not set, all tests will be skipped.

NOTE: This test uses SQLite database files that are created in the tests directory.
Test databases are cleaned up after tests complete (unless YARASP_SQLITE_NO_FLUSH is set).

When running with -v (verbose) flag, test will log paths to SQLite databases:
- sqlite_db_path: path to counter database
- sqlite_cache_db_path: path to cache database
Note: To see the database paths in output, use -v -s flags together.

Configuration:
    YARASP_SQLITE_NO_FLUSH - Set to "1" or "true" to disable database cleanup (default: cleanup enabled)

Running tests:
    # Run default tests (stations_list, schedule, carrier)
    uv run pytest tests/test_07_sqlite.py

    # Run all endpoint tests
    uv run pytest tests/test_07_sqlite.py -m all_endpoints
    # or
    uv run pytest tests/test_07_sqlite.py -m all

    # Run only stations_list test
    uv run pytest tests/test_07_sqlite.py -m stations_list

    # Run only schedule test
    uv run pytest tests/test_07_sqlite.py -m schedule

    # Run only carrier test
    uv run pytest tests/test_07_sqlite.py -m carrier

    # Run multiple specific tests
    uv run pytest tests/test_07_sqlite.py -m "schedule or carrier"

    # Run carrier test without flushing database (preserves cache between runs)
    YARASP_SQLITE_NO_FLUSH=1 uv run pytest tests/test_07_sqlite.py -m carrier

    # Run with verbose output to see database paths (use -v -s to see paths)
    uv run pytest tests/test_07_sqlite.py -v -s
"""

import os
import sqlite3
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Load .env file BEFORE importing yarasp to ensure YARASP_API_KEY is available
# Load .env file from project root
env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file, override=False)

from yarasp import YaraspClient
import hishel
from scripts.fixture_requests import (
    SCHEDULE_REQUEST,
    CARRIER_REQUEST,
    STATIONS_LIST_REQUEST,
    SEARCH_REQUEST,
    THREAD_REQUEST,
    NEAREST_STATIONS_REQUEST,
    NEAREST_SETTLEMENT_REQUEST,
    COPYRIGHT_REQUEST,
)


def _api_key_available() -> bool:
    """Check if YARASP_API_KEY is available."""
    return bool(os.environ.get("YARASP_API_KEY"))


pytestmark = pytest.mark.skipif(
    not _api_key_available(),
    reason="YARASP_API_KEY environment variable is not set. Set it via environment variable or .env file.",
)


@pytest.fixture
def sqlite_db_path(tmp_path):
    """Create temporary SQLite database path for counter."""
    db_path = tmp_path / "yarasp_counter.db"
    return str(db_path)


@pytest.fixture
def sqlite_cache_db_path(tmp_path):
    """Create temporary SQLite database path for cache storage."""
    db_path = tmp_path / "yarasp_cache.db"
    return str(db_path)


@pytest.fixture
def client(sqlite_db_path, sqlite_cache_db_path, request):
    """
    Create YaraspClient with SQLite storage and counter.
    
    This test verifies both caching functionality and API usage counter through SQLite.
    Uses separate database for cache to avoid conflicts between tests.
    
    When running with -v (verbose) flag, logs paths to SQLite databases.
    """
    import sqlite3
    
    # Log database paths if verbose mode is enabled
    # Check if -v or -vv flag is used
    verbose = request.config.getoption("verbose", default=0)
    if verbose > 0:
        # Print database paths (visible with -v -s flags)
        print(f"\n[SQLite Test] Counter database path: {sqlite_db_path}")
        print(f"[SQLite Test] Cache database path: {sqlite_cache_db_path}")
    
    # Create SQLiteStorage with separate database for cache
    cache_conn = sqlite3.connect(sqlite_cache_db_path)
    storage = hishel.SQLiteStorage(connection=cache_conn)
    return YaraspClient(
        cache_storage=storage, counter_backend="sqlite", counter_storage_path=sqlite_db_path
    )


@pytest.fixture(autouse=True)
def cleanup_sqlite_db(sqlite_db_path, sqlite_cache_db_path):
    """
    Clean up SQLite databases before and after each test.
    
    Respects YARASP_SQLITE_NO_FLUSH environment variable to preserve database state.
    """
    # Check if flush should be disabled
    no_flush = os.environ.get("YARASP_SQLITE_NO_FLUSH", "").lower() in ("1", "true", "yes")
    
    # Clean databases before test
    if not no_flush:
        if os.path.exists(sqlite_db_path):
            os.remove(sqlite_db_path)
        if os.path.exists(sqlite_cache_db_path):
            os.remove(sqlite_cache_db_path)
    
    yield
    
    # Clean databases after test
    if not no_flush:
        if os.path.exists(sqlite_db_path):
            os.remove(sqlite_db_path)
        if os.path.exists(sqlite_cache_db_path):
            os.remove(sqlite_cache_db_path)


@pytest.mark.stations_list
@pytest.mark.all_endpoints
@pytest.mark.all
def test_sqlite_cache_stations_list(client):
    """
    Test SQLite cache for stations_list endpoint.
    
    stations_list returns a long response, testing large data handling in SQLite cache.
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
@pytest.mark.all_endpoints
@pytest.mark.all
def test_sqlite_cache_schedule(client):
    """
    Test SQLite cache for schedule endpoint.
    
    schedule uses pagination, testing paginated response caching in SQLite.
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
@pytest.mark.all_endpoints
@pytest.mark.all
def test_sqlite_cache_carrier(client):
    """
    Test SQLite cache for carrier endpoint.
    
    carrier does not use pagination, testing simple response caching in SQLite.
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


@pytest.mark.all_endpoints
@pytest.mark.all
def test_sqlite_cache_search(client):
    """
    Test SQLite cache for search endpoint.
    
    search uses pagination, testing paginated response caching in SQLite.
    """
    # First request: may be from cache if noflush is enabled and data exists
    result1 = client.get(SEARCH_REQUEST["endpoint"], params=SEARCH_REQUEST["params"])
    assert isinstance(result1, dict)
    first_from_cache = client.last_response_from_cache
    
    # Second request: should read from cache
    result2 = client.get(SEARCH_REQUEST["endpoint"], params=SEARCH_REQUEST["params"])
    assert client.last_response_from_cache is True, "Second request should be from cache"
    assert isinstance(result2, dict)
    
    # Compare full equality of written and read data
    assert result1 == result2, "Cached data should match original data"
    
    if not first_from_cache:
        assert client.last_response_from_cache is True


@pytest.mark.all_endpoints
@pytest.mark.all
def test_sqlite_cache_thread(client):
    """
    Test SQLite cache for thread endpoint.
    
    thread does not use pagination, testing simple response caching in SQLite.
    """
    # First request: may be from cache if noflush is enabled and data exists
    result1 = client.get(THREAD_REQUEST["endpoint"], params=THREAD_REQUEST["params"])
    assert isinstance(result1, dict)
    first_from_cache = client.last_response_from_cache
    
    # Second request: should read from cache
    result2 = client.get(THREAD_REQUEST["endpoint"], params=THREAD_REQUEST["params"])
    assert client.last_response_from_cache is True, "Second request should be from cache"
    assert isinstance(result2, dict)
    
    # Compare full equality of written and read data
    assert result1 == result2, "Cached data should match original data"
    
    if not first_from_cache:
        assert client.last_response_from_cache is True


@pytest.mark.all_endpoints
@pytest.mark.all
def test_sqlite_cache_nearest_stations(client):
    """
    Test SQLite cache for nearest_stations endpoint.
    
    nearest_stations uses pagination, testing paginated response caching in SQLite.
    """
    # First request: may be from cache if noflush is enabled and data exists
    result1 = client.get(
        NEAREST_STATIONS_REQUEST["endpoint"], params=NEAREST_STATIONS_REQUEST["params"]
    )
    assert isinstance(result1, dict)
    first_from_cache = client.last_response_from_cache
    
    # Second request: should read from cache
    result2 = client.get(
        NEAREST_STATIONS_REQUEST["endpoint"], params=NEAREST_STATIONS_REQUEST["params"]
    )
    assert client.last_response_from_cache is True, "Second request should be from cache"
    assert isinstance(result2, dict)
    
    # Compare full equality of written and read data
    assert result1 == result2, "Cached data should match original data"
    
    if not first_from_cache:
        assert client.last_response_from_cache is True


@pytest.mark.all_endpoints
@pytest.mark.all
def test_sqlite_cache_nearest_settlement(client):
    """
    Test SQLite cache for nearest_settlement endpoint.
    
    nearest_settlement does not use pagination, testing simple response caching in SQLite.
    """
    # First request: may be from cache if noflush is enabled and data exists
    result1 = client.get(
        NEAREST_SETTLEMENT_REQUEST["endpoint"], params=NEAREST_SETTLEMENT_REQUEST["params"]
    )
    assert isinstance(result1, dict)
    first_from_cache = client.last_response_from_cache
    
    # Second request: should read from cache
    result2 = client.get(
        NEAREST_SETTLEMENT_REQUEST["endpoint"], params=NEAREST_SETTLEMENT_REQUEST["params"]
    )
    assert client.last_response_from_cache is True, "Second request should be from cache"
    assert isinstance(result2, dict)
    
    # Compare full equality of written and read data
    assert result1 == result2, "Cached data should match original data"
    
    if not first_from_cache:
        assert client.last_response_from_cache is True


@pytest.mark.all_endpoints
@pytest.mark.all
def test_sqlite_cache_copyright(client):
    """
    Test SQLite cache for copyright endpoint.
    
    copyright does not use pagination, testing simple response caching in SQLite.
    """
    # First request: may be from cache if noflush is enabled and data exists
    result1 = client.get(COPYRIGHT_REQUEST["endpoint"], params=COPYRIGHT_REQUEST["params"])
    assert isinstance(result1, dict)
    first_from_cache = client.last_response_from_cache
    
    # Second request: should read from cache
    result2 = client.get(COPYRIGHT_REQUEST["endpoint"], params=COPYRIGHT_REQUEST["params"])
    assert client.last_response_from_cache is True, "Second request should be from cache"
    assert isinstance(result2, dict)
    
    # Compare full equality of written and read data
    assert result1 == result2, "Cached data should match original data"
    
    if not first_from_cache:
        assert client.last_response_from_cache is True


@pytest.mark.carrier
def test_apikey_counter_sqlite(client, sqlite_db_path):
    """
    Test that API usage counter correctly stores usage data in SQLite database.
    
    Verifies that:
    - Counter increments only for non-cached requests
    - Counter does not increment for cached requests
    - Data is correctly stored in SQLite database table apikey_usage
    """
    from datetime import date

    # Get initial count from counter
    initial_count = client.usage_counter.get_count()

    # Make a request (may be from API or cache)
    result = client.get(CARRIER_REQUEST["endpoint"], params=CARRIER_REQUEST["params"])
    assert isinstance(result, dict)

    # Check if request was from cache
    was_from_cache = client.last_response_from_cache is True

    # Get count after request
    count_after_first = client.usage_counter.get_count()

    if not was_from_cache:
        # If first request was from API, counter should increment
        assert count_after_first == initial_count + 1, "Counter should increment for API requests"
    else:
        # If first request was from cache, counter should not increment
        assert count_after_first == initial_count, "Counter should not increment for cached requests"

    # Make second request (should be from cache)
    result = client.get(CARRIER_REQUEST["endpoint"], params=CARRIER_REQUEST["params"])
    assert isinstance(result, dict)
    assert client.last_response_from_cache is True, "Second request should be from cache"

    # Counter should not increment for cached request
    count_after_second = client.usage_counter.get_count()
    assert count_after_second == count_after_first, "Counter should not increment for cached requests"

    # Verify data in SQLite database
    conn = sqlite3.connect(sqlite_db_path)
    try:
        cursor = conn.execute(
            "SELECT key, date, counter FROM apikey_usage WHERE key = ? AND date = ?",
            (client.api_key, date.today().isoformat()),
        )
        row = cursor.fetchone()
        assert row is not None, "Counter data should be stored in SQLite database"
        key, date_str, counter = row
        assert key == client.api_key, "API key should match"
        assert date_str == date.today().isoformat(), "Date should be today"
        assert counter == count_after_second, "Counter value should match"
    finally:
        conn.close()

    # Make another request to a different endpoint (should be from API if not cached)
    result = client.get(SEARCH_REQUEST["endpoint"], params=SEARCH_REQUEST["params"])
    assert isinstance(result, dict)

    # Check if this request was from cache
    was_from_cache = client.last_response_from_cache is True

    # Get count after third request
    count_after_third = client.usage_counter.get_count()

    if not was_from_cache:
        # If request was from API, counter should increment
        assert count_after_third == count_after_second + 1, "Counter should increment for API requests"
    else:
        # If request was from cache, counter should not increment
        assert count_after_third == count_after_second, "Counter should not increment for cached requests"

    # Verify updated data in SQLite database
    conn = sqlite3.connect(sqlite_db_path)
    try:
        cursor = conn.execute(
            "SELECT key, date, counter FROM apikey_usage WHERE key = ? AND date = ?",
            (client.api_key, date.today().isoformat()),
        )
        row = cursor.fetchone()
        assert row is not None, "Counter data should be stored in SQLite database"
        key, date_str, counter = row
        assert key == client.api_key, "API key should match"
        assert date_str == date.today().isoformat(), "Date should be today"
        assert counter == count_after_third, "Counter value should match updated count"
    finally:
        conn.close()
