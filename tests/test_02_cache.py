"""
Test cache functionality using fixture requests.

All requests in this test must be taken from cache.
Fixtures are generated using scripts/gen_fixtures.py.
"""

import pytest

from yarasp import YaraspClient
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
    result = client.get(NEAREST_STATIONS_REQUEST["endpoint"], params=NEAREST_STATIONS_REQUEST["params"])
    assert client.last_response_from_cache is True
    assert isinstance(result, dict), f"Expected dict, but got {type(result)}"
    assert "stations" in result or "pagination" in result
    
    # Test nearest_settlement endpoint
    result = client.get(NEAREST_SETTLEMENT_REQUEST["endpoint"], params=NEAREST_SETTLEMENT_REQUEST["params"])
    assert client.last_response_from_cache is True
    assert isinstance(result, dict), f"Expected dict, but got {type(result)}"
    assert "settlement" in result or "title" in result
    
    # Test copyright endpoint
    result = client.get(COPYRIGHT_REQUEST["endpoint"], params=COPYRIGHT_REQUEST["params"])
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
        assert client.last_response_from_cache is True, f"Request for {endpoint} should be from cache"
        assert isinstance(result, dict), f"Expected dict for {endpoint}, but got {type(result)}"
