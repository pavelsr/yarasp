"""
Test pagination functionality for API methods that support it.

Test algorithm:
1. Get all endpoints with auto_paginate=True from _YaraspClientBase._get_endpoints_config()
2. Match each endpoint with corresponding request parameters from fixture_requests.REQUESTS
3. Remove limit parameter from params (if present) as pagination uses limit=100 by default
4. Call each endpoint with auto_paginate=True and verify it returns a list

Note: Currently this test is applicable only to three API methods:
- search
- schedule  
- nearest_stations

Cache status is not verified because pagination makes multiple requests with different
offset values, and not all of them may be cached.
"""

import pytest

from yarasp import YaraspClient
from yarasp.yarasp import _YaraspClientBase
from scripts.fixture_requests import REQUESTS
import hishel

client = YaraspClient(cache_storage=hishel.FileStorage(base_path="tests/.cache/hishel"))


def test_paginated_endpoints():
    """
    Test pagination for all endpoints that support auto_paginate=True.
    
    Algorithm:
    1. Get endpoints configuration from _YaraspClientBase._get_endpoints_config()
    2. Filter endpoints where auto_paginate=True
    3. Match each endpoint name with request parameters from fixture_requests.REQUESTS
    4. Remove limit parameter from params (if present) as pagination uses limit=100 by default
    5. Call each endpoint method with matched parameters (auto_paginate=True by default)
    6. Verify response is a list (paginated aggregated result)
    
    Note: Cache status is not checked because pagination makes multiple requests
    with different offset values, and some may not be cached yet.
    """
    # Get endpoints configuration
    endpoints_config = _YaraspClientBase._get_endpoints_config()
    
    # Create a mapping from endpoint name to request params for quick lookup
    requests_map = {req["endpoint"]: req["params"] for req in REQUESTS}
    
    # Filter endpoints with auto_paginate=True
    paginated_endpoints = {
        endpoint: (auto_paginate, result_key)
        for endpoint, (auto_paginate, result_key) in endpoints_config.items()
        if auto_paginate is True
    }
    
    # Test each paginated endpoint
    for endpoint_name in paginated_endpoints.keys():
        # Get request parameters from fixture_requests
        if endpoint_name not in requests_map:
            pytest.skip(f"No request parameters found for endpoint: {endpoint_name}")
        
        params = requests_map[endpoint_name].copy()
        
        # Remove limit parameter if present, as pagination will use limit=100 by default
        # This allows pagination to work properly while using base parameters from fixtures
        if "limit" in params:
            params.pop("limit")
        
        # Get the method and call it (it will use auto_paginate=True by default from _create_wrapped_methods)
        method = getattr(client, endpoint_name)
        result = method(params=params)
        
        # Verify response is a list (paginated result)
        assert isinstance(result, list), f"Expected list for {endpoint_name}, but got {type(result)}"
        
        # Note: We don't check cache status here because pagination makes multiple requests
        # (with different offset values), and some of them may not be in cache yet.
        # The important thing is that pagination works and returns a list.
