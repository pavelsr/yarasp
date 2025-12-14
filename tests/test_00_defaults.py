import pytest

from yarasp import YaraspClient

def test_yarasp_client_sync_cached_defaults():
    import hishel
    client = YaraspClient()
    assert client.base_url == "https://api.rasp.yandex.net/v3.0"
    assert client.ignore_params == {'apikey'}
    assert client.verbose is False
    assert isinstance(client.safe_mode, bool)
    assert isinstance(client.daily_limit, int)
    assert client.counter_backend in {"json", "redis"}
    assert client.counter_storage_path == "yarasp_counter.json"
    assert client.redis_client is None
    assert client.user_agent == "httpx" # hishel.CacheClient
    #assert isinstance(client.user_agent, hishel.CacheClient)
    assert client.cache_enabled is True
    # Storage is wrapped with SafeStorageWrapper which inherits from FileStorage
    assert isinstance(client.cache_storage, hishel.BaseStorage)
    assert client.last_response_from_cache is None
    assert hasattr(client, "api_key")  # Check attribute presence


def test_yarasp_client_sync_nocached_defaults():
    client = YaraspClient(cache_enabled=False)
    assert client.base_url == "https://api.rasp.yandex.net/v3.0"
    assert client.ignore_params == {'apikey'}
    assert client.verbose is False
    assert isinstance(client.safe_mode, bool)
    assert isinstance(client.daily_limit, int)
    assert client.counter_backend in {"json", "redis"}
    assert client.counter_storage_path == "yarasp_counter.json"
    assert client.redis_client is None
    assert client.user_agent == "httpx"
    assert client.cache_enabled is False
    assert client.cache_storage is None
    assert client.last_response_from_cache is None
    assert hasattr(client, "api_key")  # Check attribute presence


### ASYNC ###

from yarasp import AsyncYaraspClient

def test_yarasp_client_async_cached_defaults():
    import hishel
    client = AsyncYaraspClient()
    assert client.base_url == "https://api.rasp.yandex.net/v3.0"
    assert client.ignore_params == {'apikey'}
    assert client.verbose is False
    assert isinstance(client.safe_mode, bool)
    assert isinstance(client.daily_limit, int)
    assert client.counter_backend in {"json", "redis"}
    assert client.counter_storage_path == "yarasp_counter.json"
    assert client.redis_client is None
    assert client.user_agent == "httpx" # hishel.CacheClient
    #assert isinstance(client.user_agent, hishel.CacheClient)
    assert client.cache_enabled is True
    # Storage is wrapped with AsyncSafeStorageWrapper which inherits from AsyncFileStorage
    assert isinstance(client.cache_storage, hishel.AsyncBaseStorage)
    assert client.last_response_from_cache is None
    assert hasattr(client, "api_key")  # Check attribute presence


def test_yarasp_client_async_nocached_defaults():
    client = AsyncYaraspClient(cache_enabled=False)
    assert client.base_url == "https://api.rasp.yandex.net/v3.0"
    assert client.ignore_params == {'apikey'}
    assert client.verbose is False
    assert isinstance(client.safe_mode, bool)
    assert isinstance(client.daily_limit, int)
    assert client.counter_backend in {"json", "redis"}
    assert client.counter_storage_path == "yarasp_counter.json"
    assert client.redis_client is None
    assert client.user_agent == "httpx"
    assert client.cache_enabled is False
    assert client.cache_storage is None
    assert client.last_response_from_cache is None
    assert hasattr(client, "api_key")  # Check attribute presence