# This script tests all methods with pagination
# Others won't be tested because it requires saving to tests/.cache/hishel
# Namely:
# endpoints = {
#     "search": (True, "segments"),
#     "schedule": (True, "schedule"),
#     "nearest_stations": (True, "stations"),
#     "thread": (False, None),
#     "nearest_settlement": (False, None),
#     "carrier": (False, None),
#     "stations_list": (False, None),
#     "copyright": (False, None)
# }

import pytest

from yarasp import YaraspClient
import hishel
client = YaraspClient(cache_storage = hishel.FileStorage(base_path="tests/.cache/hishel"))


def test_search_pag():
    result = client.search({"from": "s9600366", "to": "s9600213", "transport_types": "plane"})
    assert client.last_response_from_cache is True
    assert isinstance(result, list), f"Expected list, but got {type(result)}"
    # assert 100 < len(result) <= 200
    assert len(result) == 192
    

def test_schedule_pag():
    result = client.schedule(params={"station": "2004001", "system": "express"})
    assert client.last_response_from_cache is True
    assert isinstance(result, list), f"Expected list, but got {type(result)}"
    # assert 100 < len(result) <= 200
    # assert len(result) == 200
    
def test_nearest_stations_pag():
    result = client.nearest_stations(params={"lat": "59.938784", "lng": "30.314997", "transport_types": "train,suburban", "distance": 35})
    assert client.last_response_from_cache is True
    assert isinstance(result, list), f"Expected list, but got {type(result)}"
    assert len(result) == 117


