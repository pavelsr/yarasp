"""
Test API key counter logic.

Tests that the usage counter does not increment when:
- API key is None
- API key is empty string
- API key contains only whitespace
- API key is empty in request URL (apikey=&...)

Tests that the usage counter increments when:
- API key is valid (non-empty string)
"""

import os
import tempfile
import json

from yarasp import YaraspClient


class MockResponse:
    """Mock HTTP response for testing."""
    def __init__(self, url, from_cache=False, method="GET"):
        self.url = url
        # Create request object with url and method attributes
        request_obj = type('obj', (object,), {'url': url, 'method': method})()
        self.request = request_obj
        self.extensions = {"from_cache": from_cache}
        self.status_code = 200
        self.content = b'{"test": "data"}'
    
    def json(self):
        return {"test": "data"}


def test_has_valid_apikey_none():
    """Test _has_valid_apikey with None API key."""
    client = YaraspClient(cache_enabled=False)
    client.api_key = None
    response = MockResponse('https://api.rasp.yandex.net/v3.0/search/?apikey=&from=s9600366')
    assert client._has_valid_apikey(response) is False


def test_has_valid_apikey_empty_string():
    """Test _has_valid_apikey with empty string API key."""
    client = YaraspClient(cache_enabled=False)
    client.api_key = ''
    response = MockResponse('https://api.rasp.yandex.net/v3.0/search/?apikey=&from=s9600366')
    assert client._has_valid_apikey(response) is False


def test_has_valid_apikey_whitespace():
    """Test _has_valid_apikey with whitespace-only API key."""
    client = YaraspClient(cache_enabled=False)
    client.api_key = '   '
    response = MockResponse('https://api.rasp.yandex.net/v3.0/search/?apikey=&from=s9600366')
    assert client._has_valid_apikey(response) is False


def test_has_valid_apikey_empty_in_url():
    """Test _has_valid_apikey with empty apikey in URL."""
    client = YaraspClient(cache_enabled=False)
    client.api_key = 'valid_key_123'
    # Even if self.api_key is valid, if URL has empty apikey, it should be invalid
    response = MockResponse('https://api.rasp.yandex.net/v3.0/search/?apikey=&from=s9600366')
    assert client._has_valid_apikey(response) is False


def test_has_valid_apikey_valid():
    """Test _has_valid_apikey with valid API key."""
    client = YaraspClient(cache_enabled=False)
    client.api_key = 'valid_key_123'
    response = MockResponse('https://api.rasp.yandex.net/v3.0/search/?apikey=valid_key_123&from=s9600366')
    assert client._has_valid_apikey(response) is True


def test_counter_not_incremented_with_empty_apikey():
    """Test that counter does not increment when API key is empty."""
    
    # Create temporary counter file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({}, f)
        counter_file = f.name
    
    try:
        # Create client with empty API key
        client = YaraspClient(
            cache_enabled=False,
            counter_storage_path=counter_file
        )
        client.api_key = ''
        
        # Create mock response (not from cache, so it would normally increment)
        response = MockResponse('https://api.rasp.yandex.net/v3.0/search/?apikey=&from=s9600366', from_cache=False)
        
        # Get initial count
        initial_count = client.usage_counter.get_count()
        
        # Call _log_and_check_limits (this would normally increment counter)
        client._log_and_check_limits(response)
        
        # Check that counter was NOT incremented
        final_count = client.usage_counter.get_count()
        assert final_count == initial_count, "Counter should not increment with empty API key"
    finally:
        # Clean up
        if os.path.exists(counter_file):
            os.unlink(counter_file)


def test_counter_not_incremented_with_none_apikey():
    """Test that counter does not increment when API key is None."""
    
    # Create temporary counter file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({}, f)
        counter_file = f.name
    
    try:
        # Create client with None API key
        client = YaraspClient(
            cache_enabled=False,
            counter_storage_path=counter_file
        )
        client.api_key = None
        
        # Create mock response (not from cache, so it would normally increment)
        response = MockResponse('https://api.rasp.yandex.net/v3.0/search/?apikey=&from=s9600366', from_cache=False)
        
        # Get initial count
        initial_count = client.usage_counter.get_count()
        
        # Call _log_and_check_limits (this would normally increment counter)
        client._log_and_check_limits(response)
        
        # Check that counter was NOT incremented
        final_count = client.usage_counter.get_count()
        assert final_count == initial_count, "Counter should not increment with None API key"
    finally:
        # Clean up
        if os.path.exists(counter_file):
            os.unlink(counter_file)


def test_counter_incremented_with_valid_apikey():
    """Test that counter increments when API key is valid."""
    
    # Create temporary counter file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({}, f)
        counter_file = f.name
    
    try:
        # Create client with valid API key
        client = YaraspClient(
            cache_enabled=False,
            counter_storage_path=counter_file
        )
        client.api_key = 'valid_key_123'
        
        # Create mock response (not from cache, so it should increment)
        response = MockResponse('https://api.rasp.yandex.net/v3.0/search/?apikey=valid_key_123&from=s9600366', from_cache=False)
        
        # Get initial count
        initial_count = client.usage_counter.get_count()
        
        # Call _log_and_check_limits (this should increment counter)
        client._log_and_check_limits(response)
        
        # Check that counter WAS incremented
        final_count = client.usage_counter.get_count()
        assert final_count == initial_count + 1, "Counter should increment with valid API key"
    finally:
        # Clean up
        if os.path.exists(counter_file):
            os.unlink(counter_file)


def test_counter_not_incremented_from_cache():
    """Test that counter does not increment when response is from cache (even with valid API key)."""
    
    # Create temporary counter file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({}, f)
        counter_file = f.name
    
    try:
        # Create client with valid API key
        client = YaraspClient(
            cache_enabled=False,
            counter_storage_path=counter_file
        )
        client.api_key = 'valid_key_123'
        
        # Create mock response (from cache, so it should NOT increment)
        response = MockResponse('https://api.rasp.yandex.net/v3.0/search/?apikey=valid_key_123&from=s9600366', from_cache=True)
        
        # Get initial count
        initial_count = client.usage_counter.get_count()
        
        # Call _log_and_check_limits (this should NOT increment counter)
        client._log_and_check_limits(response)
        
        # Check that counter was NOT incremented
        final_count = client.usage_counter.get_count()
        assert final_count == initial_count, "Counter should not increment for cached responses"
    finally:
        # Clean up
        if os.path.exists(counter_file):
            os.unlink(counter_file)

