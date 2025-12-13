import pytest

from yarasp import YaraspClient
import hishel
client = YaraspClient(cache_storage = hishel.FileStorage(base_path="tests/.cache/hishel"))

def test_yarasp_cache():
    # All requests here must be taken from cache 
    # Generation: scripts/gen_mock_responses.py + remove apikey manually
    # For completeness of testing, there should be at least one method with pagination
    
    result = client.get("carrier", params={"code": "SU", "system": "iata"})
    assert client.last_response_from_cache is True
    assert isinstance(result, dict), f"Expected dict, but got {type(result)}"
    assert result["carrier"]["title"] == "Аэрофлот"
    assert result["carrier"]["codes"]["iata"] == "SU"

    result = client.get("search", params={"from": "s9600366", "to": "s9600213", "transport_types": "plane"})
    assert client.last_response_from_cache is True
    assert isinstance(result, dict), f"Expected dict, but got {type(result)}"
    assert result["pagination"] == {'total': 195, 'limit': 100, 'offset': 0}

    # client.schedule is method with pagination

    result = client.get("schedule", params={"station": "2004001", "system": "express"})
    assert client.last_response_from_cache is True
    assert isinstance(result, dict), f"Expected dict, but got {type(result)}"
    assert len(result["schedule"]) == 100
    assert result["pagination"] == {'total': 557, 'limit': 100, 'offset': 0}

    result = client.get("schedule", params={"station": "2004001", "system": "express"}, auto_paginate=True)
    assert client.last_response_from_cache is True
    assert isinstance(result, list), f"Expected list, but got {type(result)}"
    assert len(result) == 6

    result = client.get("schedule", params={"station": "2004001", "system": "express"}, auto_paginate=True, result_key="schedule")
    assert client.last_response_from_cache is True
    assert isinstance(result, list), f"Expected list, but got {type(result)}"
    assert len(result) == 558



