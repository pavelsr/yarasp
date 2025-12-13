# Tests for stations_list endpoint
# Require large fixture file stations_list_result.json (105MB)
# Run only with --large-fixtures option

import pytest
from yarasp import YaraspClient
import hishel


@pytest.mark.large_fixture
def test_stations_list(stations_list_fixture_available):
    """
    Test for stations_list method.
    
    Requires stations_list_result.json in tests/fixtures/.
    File is automatically downloaded from S3 when running with --large-fixtures option.
    """
    if not stations_list_fixture_available:
        pytest.skip("stations_list_result.json is not available")
    
    client = YaraspClient(cache_storage = hishel.FileStorage(base_path="tests/.cache/hishel"))
    
    # stations_list doesn't require parameters
    result = client.stations_list()
    assert client.last_response_from_cache is True
    assert isinstance(result, dict), f"Expected dict, but got {type(result)}"
    assert "countries" in result, "Response should contain 'countries' key"
    
    # Check response structure
    assert isinstance(result["countries"], list), "countries should be a list"
    assert len(result["countries"]) > 0, "countries list should not be empty"

