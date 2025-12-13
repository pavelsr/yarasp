import pytest
from yarasp import YaraspClient

def test_yarasp_client_methods():
    client = YaraspClient()
    
    for method in [
        "search", "schedule", "nearest_stations", "thread",
        "nearest_settlement", "carrier", "stations_list", "copyright"
    ]:
        assert hasattr(client, method), f"Method {method} is missing in YaraspClient"
        assert callable(getattr(client, method)), f"Method {method} is not callable"


### ASYNC ###


from yarasp import AsyncYaraspClient

def test_yarasp_client_methods():
    client = AsyncYaraspClient()
    
    for method in [
        "search", "schedule", "nearest_stations", "thread",
        "nearest_settlement", "carrier", "stations_list", "copyright"
    ]:
        assert hasattr(client, method), f"Method {method} is missing in YaraspClient"
        assert callable(getattr(client, method)), f"Method {method} is not callable"
