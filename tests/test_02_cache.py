"""
Test cache functionality using fixture requests.

All requests in this test must be taken from cache.
Fixtures are generated using scripts/gen_fixtures.py.
"""

from pathlib import Path

import pytest

from yarasp import YaraspClient, CacheMissError
import hishel
from scripts.fixture_requests import (
    REQUESTS,
    SEARCH_REQUEST,
    SCHEDULE_REQUEST,
    THREAD_REQUEST,
    NEAREST_STATIONS_REQUEST,
    NEAREST_SETTLEMENT_REQUEST,
    CARRIER_REQUEST,
    COPYRIGHT_REQUEST,
)

# Get cache directory path relative to this test file
CACHE_DIR = Path(__file__).parent / ".cache" / "hishel"


def _cache_dir_exists_and_not_empty() -> bool:
    """Check if cache directory exists and is not empty."""
    if not CACHE_DIR.exists() or not CACHE_DIR.is_dir():
        return False
    try:
        # Check if directory has any files (excluding .gitignore and other hidden files)
        # Only count actual cache files
        for item in CACHE_DIR.iterdir():
            if not item.name.startswith("."):
                return True
        return False
    except OSError:
        return False


pytestmark = pytest.mark.skipif(
    not _cache_dir_exists_and_not_empty(),
    reason="Cache directory tests/.cache/hishel does not exist or is empty",
)

client = YaraspClient(cache_storage=hishel.FileStorage(base_path="tests/.cache/hishel"))


def test_yarasp_cache():
    """
    Test that all requests are served from cache.

    Uses the same request parameters as gen_fixtures.py to ensure consistency.
    All requests here must be taken from cache.
    Generation: scripts/gen_fixtures.py
    """

    # Test carrier endpoint
    result = client.get(CARRIER_REQUEST["endpoint"], params=CARRIER_REQUEST["params"])
    assert client.last_response_from_cache is True
    assert isinstance(result, dict), f"Expected dict, but got {type(result)}"
    assert "carrier" in result
    assert isinstance(result["carrier"], dict)
    assert "title" in result["carrier"]
    assert "codes" in result["carrier"]

    # Test search endpoint
    result = client.get(SEARCH_REQUEST["endpoint"], params=SEARCH_REQUEST["params"])
    assert client.last_response_from_cache is True
    assert isinstance(result, dict), f"Expected dict, but got {type(result)}"
    assert "segments" in result or "search" in result
    assert "pagination" in result

    # Test schedule endpoint
    result = client.get(SCHEDULE_REQUEST["endpoint"], params=SCHEDULE_REQUEST["params"])
    assert client.last_response_from_cache is True
    assert isinstance(result, dict), f"Expected dict, but got {type(result)}"
    assert "schedule" in result
    assert isinstance(result["schedule"], list)
    if "pagination" in result:
        assert isinstance(result["pagination"], dict)

    # Test thread endpoint
    result = client.get(THREAD_REQUEST["endpoint"], params=THREAD_REQUEST["params"])
    assert client.last_response_from_cache is True
    assert isinstance(result, dict), f"Expected dict, but got {type(result)}"
    assert "thread" in result or "stops" in result

    # Test nearest_stations endpoint
    result = client.get(
        NEAREST_STATIONS_REQUEST["endpoint"], params=NEAREST_STATIONS_REQUEST["params"]
    )
    assert client.last_response_from_cache is True
    assert isinstance(result, dict), f"Expected dict, but got {type(result)}"
    assert "stations" in result or "pagination" in result

    # Test nearest_settlement endpoint
    result = client.get(
        NEAREST_SETTLEMENT_REQUEST["endpoint"],
        params=NEAREST_SETTLEMENT_REQUEST["params"],
    )
    assert client.last_response_from_cache is True
    assert isinstance(result, dict), f"Expected dict, but got {type(result)}"
    assert "settlement" in result or "title" in result

    # Test copyright endpoint
    result = client.get(
        COPYRIGHT_REQUEST["endpoint"], params=COPYRIGHT_REQUEST["params"]
    )
    assert client.last_response_from_cache is True
    assert isinstance(result, dict), f"Expected dict, but got {type(result)}"
    assert "copyright" in result or "text" in result


def test_all_fixture_requests_from_cache():
    """
    Test that all requests from fixture_requests.REQUESTS are served from cache.

    This ensures that gen_fixtures.py and tests use the same request parameters.
    """
    for request in REQUESTS:
        endpoint = request["endpoint"]
        params = request["params"]

        # Skip stations_list as it requires large fixture marker
        if endpoint == "stations_list":
            continue

        result = client.get(endpoint, params=params)
        assert client.last_response_from_cache is True, (
            f"Request for {endpoint} should be from cache"
        )
        assert isinstance(result, dict), (
            f"Expected dict for {endpoint}, but got {type(result)}"
        )


def test_cache_only_mode_with_cached_data():
    """
    Test that cache_only=True works correctly when data is in cache.

    This test verifies that cache_only mode allows reading from cache
    and doesn't raise CacheMissError when data exists.
    """
    cache_client = YaraspClient(
        cache_storage=hishel.FileStorage(base_path="tests/.cache/hishel"),
        cache_only=True,
    )

    # This should work because data is in cache
    result = cache_client.get(
        CARRIER_REQUEST["endpoint"], params=CARRIER_REQUEST["params"]
    )
    assert isinstance(result, dict)
    assert "carrier" in result
    assert cache_client.last_response_from_cache is True


def test_cache_only_mode_without_cached_data():
    """
    Test that cache_only=True raises CacheMissError when data is not in cache.

    This test verifies that cache_only mode prevents API requests
    and raises CacheMissError when data doesn't exist in cache.
    """
    import tempfile
    import shutil

    # Create a temporary empty cache directory
    temp_cache_dir = tempfile.mkdtemp()
    try:
        cache_client = YaraspClient(
            cache_storage=hishel.FileStorage(base_path=temp_cache_dir), cache_only=True
        )

        # This should raise CacheMissError because cache is empty
        with pytest.raises(CacheMissError) as exc_info:
            cache_client.get(
                CARRIER_REQUEST["endpoint"], params=CARRIER_REQUEST["params"]
            )

        assert "not found in cache" in str(exc_info.value).lower()
        assert "cache_only=False" in str(exc_info.value)
    finally:
        shutil.rmtree(temp_cache_dir, ignore_errors=True)


def test_cache_only_mode_disabled():
    """
    Test that cache_only=False allows API requests when cache is empty.

    This test verifies that with cache_only=False, the client can make
    API requests even when cache is empty.
    """
    import tempfile
    import shutil
    import os

    # Skip if API key is not available
    if not os.environ.get("YARASP_API_KEY"):
        pytest.skip("YARASP_API_KEY not set")

    # Create a temporary empty cache directory
    temp_cache_dir = tempfile.mkdtemp()
    try:
        cache_client = YaraspClient(
            cache_storage=hishel.FileStorage(base_path=temp_cache_dir), cache_only=False
        )

        # This should work because cache_only=False allows API requests
        result = cache_client.get(
            CARRIER_REQUEST["endpoint"], params=CARRIER_REQUEST["params"]
        )
        assert isinstance(result, dict)
        assert "carrier" in result
        # First request should not be from cache (cache was empty)
        assert cache_client.last_response_from_cache is False

        # Second request should be from cache
        result2 = cache_client.get(
            CARRIER_REQUEST["endpoint"], params=CARRIER_REQUEST["params"]
        )
        assert cache_client.last_response_from_cache is True
        assert result == result2
    finally:
        shutil.rmtree(temp_cache_dir, ignore_errors=True)
