"""
Yarasp module – API client for accessing Yandex Schedule service data.

Module capabilities:
- Synchronous requests are executed via hishel.hishel.CacheClient with User-Agent header: "httpx"
- Asynchronous requests are executed via hishel.AsyncCacheClient with the same header.
- Optional local caching with support for backends: sqlite (default) and redis.
- API key usage tracking (incremented only for "live" requests, not from cache).
- Safe mode (enabled by default): execution terminates when daily request limit is exceeded.
- Automatic pagination handling – with auto_paginate=True the client aggregates data from all pages.
- Ability to force "live" data requests (force_live=True) even if cache exists.
- The is_from_cache method allows checking if the last response came from cache.

Before use, the module requires the environment variable:
    YARASP_API_KEY
If it is not set – the module will not start.

Environment variables:
    YARASP_API_KEY          – API key (required)
    YARASP_API_DAILY_LIMIT  – daily request limit (default: 500)
    YARASP_SAFE_MODE        – safe mode (enabled by default)
    YARASP_VERBOSE          – verbose logging (disabled by default)
"""

import os
import httpx
import logging
from typing import Any, Optional, Set
from dataclasses import dataclass, field

from .utils import (
    JSONUsageCounter,
    CacheStorageType,
    _create_safe_storage_wrapper,
    _create_async_safe_storage_wrapper,
    format_size,
    human_readable_size,
)

# Reading environment variables
YARASP_API_KEY = os.environ.get('YARASP_API_KEY')

try:
    YARASP_API_DAILY_LIMIT = int(os.environ.get('YARASP_API_DAILY_LIMIT', '500'))
except ValueError:
    YARASP_API_DAILY_LIMIT = 500

_yarasp_safe_mode = os.environ.get('YARASP_SAFE_MODE', '1')
YARASP_SAFE_MODE = not (_yarasp_safe_mode.lower() in ['0', 'false'])

_yarasp_verbose = os.environ.get('YARASP_VERBOSE', '0')
YARASP_VERBOSE = _yarasp_verbose.lower() in ['1', 'true', 'yes']


###############################################################################
# Common base class
###############################################################################
@dataclass
class _YaraspClientBase:
    base_url: str = "https://api.rasp.yandex.net/v3.0"
    ignore_params: Set[str] = field(default_factory=lambda: {'apikey'})
    verbose: bool = YARASP_VERBOSE
    safe_mode: bool = YARASP_SAFE_MODE
    daily_limit: int = YARASP_API_DAILY_LIMIT
    counter_backend: str = "json"  # or "redis"
    counter_storage_path: str = "yarasp_counter.json"
    redis_client: Optional[Any] = None
    user_agent: str = "httpx"
    cache_enabled: bool = True
    cache_storage: Optional["CacheStorageType"] = None
    last_response_from_cache: bool = field(init=False, default=None)
    api_key: str = field(init=False, default_factory=lambda: os.environ.get('YARASP_API_KEY') or YARASP_API_KEY, repr=False)
    _in_pagination: bool = field(init=False, default=False)

    #print("Self anfter init: ", self)

    def __post_init__(self):

        self._init_http_client()
        
        if self.counter_backend == "json":
            self.usage_counter = JSONUsageCounter(self.counter_storage_path)
        elif self.counter_backend == "redis":
            # RedisUsageCounter is not yet implemented
            # TODO: Implement RedisUsageCounter when needed
            raise NotImplementedError("Redis counter backend is not yet implemented. Use 'json' backend.")
        else:
            raise ValueError("Unsupported counter backend: use 'json' or 'redis'.")
        
        # TODO:
        # cache_storage depends on cache_enabled = True
        # redis_client depends on counter_backend = redis


    def _init_http_client(self, async_mode=False):
        """Initialize HTTP client with caching support."""
        ua_header = {"User-Agent": self.user_agent}

        # default storage for files: .cache/hishel
        
        if self.cache_enabled:
            try:
                import hishel
            except ImportError:
                raise ImportError("hishel module is required for caching. Install it: pip install hishel")
            
            # WARNING: Upgrading hishel to version >=1.x will result in only SQLite
            # caching backend being available (as of December 2025). Other backends
            # (FileStorage, RedisStorage, InMemoryStorage, S3Storage) will no longer
            # be supported in hishel 1.x.
            
            if async_mode:
                if not isinstance(self.cache_storage, hishel.AsyncBaseStorage):
                    #self.cache_storage = hishel.AsyncSQLiteStorage()
                    self.cache_storage = hishel.AsyncFileStorage()
                # Wrap storage to remove apikey from URLs before storing
                self.cache_storage = _create_async_safe_storage_wrapper(self.cache_storage)
            else:
                if not isinstance(self.cache_storage, hishel.BaseStorage):
                    #self.cache_storage = hishel.SQLiteStorage()
                    self.cache_storage = hishel.FileStorage()
                # Wrap storage to remove apikey from URLs before storing
                self.cache_storage = _create_safe_storage_wrapper(self.cache_storage)

            def custom_key_generator(request: "httpcore.Request", body: bytes = b"") -> str:
                # modified hishel._utils.generate_key function
                if isinstance(request.method, bytes):  # Ensure method is a string
                    method = request.method.decode()
                else:
                    method = request.method  # Already a string

                if method == "GET":
                    from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
                    parsed_url = urlparse(str(request.url))
                    query_params = [(k, v) for k, v in parse_qsl(parsed_url.query) if k.lower() != "apikey"] 
                    new_query = urlencode(query_params)
                    new_url = urlunparse((
                        parsed_url.scheme, parsed_url.netloc, parsed_url.path,
                        parsed_url.params, new_query, parsed_url.fragment
                    ))
                    
                    request = httpcore.Request(
                        method=request.method,
                        url=new_url,
                        headers=request.headers,
                        content=request.stream,
                        extensions=request.extensions
                    )          
                cache_key = hishel._utils.generate_key(request, body)
                return cache_key
            
            import httpcore
            controller = hishel.Controller(
                key_generator=custom_key_generator, 
                cache_private=False,
                force_cache=True,
                cacheable_status_codes=[200, 201, 202, 203, 204, 205, 206, 300, 301, 302, 303, 304, 305, 306, 307, 308]
            )
            client_cls = hishel.AsyncCacheClient if async_mode else hishel.CacheClient
            self.http_client = client_cls(storage=self.cache_storage, controller=controller, headers=ua_header)
        else:
            httpx_client_cls = httpx.AsyncClient if async_mode else httpx.Client
            self.http_client = httpx_client_cls(headers=ua_header)

    def _prepare_params(self, params):
        if params is None:
            params = {}
        else:
            for key in list(params.keys()):
                if key in self.ignore_params:
                    params.pop(key)
        params["apikey"] = self.api_key
        return params

    def _build_url(self, endpoint):
        return f"{self.base_url}/{endpoint.lstrip('/').rstrip('/')}/"

    def _log_response_verbose(self, response):
        """Logs HTTP response with extended information."""
        if self.verbose:
            size_str = format_size(len(response.content))
            cached = "cached" if self.last_response_from_cache else ""
            logging.basicConfig(level=logging.INFO)
            logging.info(
                f" {response.request.method.upper()} {response.url} - Status: {response.status_code}, Data Length: ~{size_str} {cached}".strip()
            )

    def _check_daily_limit(self):
        current_count = self.usage_counter.get_count()
        if self.safe_mode and current_count >= self.daily_limit:
            logging.warning("Daily API request limit exceeded: %d/%d", current_count, self.daily_limit)
            # For synchronous client execution can be terminated,
            # for asynchronous client – exception is raised
            raise RuntimeError("Daily API request limit exceeded.")

    def _increment_usage(self):
        self.usage_counter.increment()

    def _has_valid_apikey(self, response):
        """Check if request has a valid (non-empty) API key.
        
        Args:
            response: HTTP response object
            
        Returns:
            bool: True if API key is present and non-empty, False otherwise
        """
        # First check self.api_key (the key used in _prepare_params)
        # Handle None, empty string, and whitespace-only strings
        if not self.api_key or (isinstance(self.api_key, str) and not self.api_key.strip()):
            return False
        
        # Also check the actual request URL to catch cases where empty apikey was passed
        # This handles the case: GET ...?apikey=&...
        try:
            from urllib.parse import urlparse, parse_qsl
            request_url = str(response.request.url) if hasattr(response, 'request') and hasattr(response.request, 'url') else str(response.url)
            parsed_url = urlparse(request_url)
            query_params = dict(parse_qsl(parsed_url.query))
            apikey_in_url = query_params.get('apikey', '')
            # If apikey is in URL but empty, it's invalid
            if apikey_in_url == '':
                return False
        except Exception:
            # If we can't parse URL, fall back to self.api_key check
            pass
        
        return True

    def _log_and_check_limits(self, response, skip_counter=False):
        """Request logging and limit checking.
        
        Args:
            response: HTTP response object
            skip_counter: If True, skip counter increment (used internally for pagination tracking)
        """
        # Safely get from_cache flag - it may not be set if request was mocked
        # Default to None if not set, which we'll treat as "unknown" (likely mocked)
        self.last_response_from_cache = response.extensions.get("from_cache")
        self._log_response_verbose(response)
        # Only increment counter if response is explicitly NOT from cache
        # (from_cache is False, meaning it was a real API request)
        # If from_cache is None, it's likely a mocked request, so don't count it
        # If from_cache is True, it's from cache, so don't count it
        # skip_counter is used internally to track pagination requests separately
        # Also skip if we're in pagination mode (counter will be handled in _get_paginated_results)
        # Only increment counter if request has a valid (non-empty) API key
        if not skip_counter and not self._in_pagination and self.last_response_from_cache is False:
            if self._has_valid_apikey(response):
                self._check_daily_limit()
                self._increment_usage()

    # async def _parse_json_response(self, response, async_mode):
    #     """JSON response handler for synchronous and asynchronous modes."""
    #     try:
    #         return await response.json() if async_mode else response.json()
    #     except Exception:
    #         raw_text = await response.text() if async_mode else response.text
    #         return {"error": "Failed to decode JSON", "raw": raw_text}

    # async def _parse_json_response(self, response, is_async=False):
    #     """Common JSON response handler for synchronous and asynchronous calls."""
    #     try:
    #         if is_async:
    #             return await response.json()
    #         return response.json()
    #     except Exception:
    #         if is_async:
    #             return {"error": "Failed to decode JSON", "raw": await response.text()}
    #         return {"error": "Failed to decode JSON", "raw": response.text()}


    def _parse_json_response_sync(self, response):
        """Synchronous JSON response handler."""
        try:
            return response.json()
        except Exception:
            return {"error": "Failed to decode JSON", "raw": response.text}

    async def _parse_json_response_async(self, response):
        """Asynchronous JSON response handler."""
        try:
            return await response.json()
        except Exception:
            return {"error": "Failed to decode JSON", "raw": response.text}

    # Pagination in API looks like this:
    # {
    # "pagination":
    # {
    #     "total": 11,
    #     "limit": 100,
    #     "offset": 0
    # },

    def _get_paginated_results(self, get_page, params, result_key=None, async_mode=False, limit=100):
        """Hybrid method for pagination (supports both synchronous and asynchronous calls)."""

        if not callable(get_page):
            raise TypeError(f"get_page is not a function, it has type {type(get_page)}")

        # TODO: create method to check is page in cache
        #if not YARASP_API_KEY:
        #    raise RuntimeError("Environment variable YARASP_API_KEY is not set!")
        
        async def _async_mode():
            # Set pagination flag to skip counter increments in _log_and_check_limits
            self._in_pagination = True
            aggregated = []
            params["limit"] = limit
            params["offset"] = 0
            # Track if any request was a real API call (not from cache)
            any_real_request = False
            data = await get_page(params)
            # Check if first request was real (not from cache)
            if self.last_response_from_cache is False:
                any_real_request = True

            if result_key:
                aggregated.extend(data.get(result_key, []))
            else:
                aggregated.append(data)

            pagination = data.get("pagination", {})
            total = pagination.get("total", 0)
            offset = pagination.get("offset", 0)

            while offset + limit < total:
                offset += limit
                params["offset"] = offset
                page_data = await get_page(params)
                # Check if this request was real (not from cache)
                if self.last_response_from_cache is False:
                    any_real_request = True

                if result_key:
                    aggregated.extend(page_data.get(result_key, []))
                else:
                    aggregated.append(page_data)

            # Only increment counter once if any request was real and has valid API key
            if any_real_request and self.api_key and (isinstance(self.api_key, str) and self.api_key.strip()):
                self._check_daily_limit()
                self._increment_usage()
            # Set last_response_from_cache based on whether all were from cache
            self.last_response_from_cache = not any_real_request
            # Reset pagination flag
            self._in_pagination = False

            return aggregated

        def _sync_mode():
            # Set pagination flag to skip counter increments in _log_and_check_limits
            self._in_pagination = True
            aggregated = []
            params["limit"] = limit
            params["offset"] = 0
            # Track if any request was a real API call (not from cache)
            any_real_request = False
            data = get_page(params)
            # Check if first request was real (not from cache)
            if self.last_response_from_cache is False:
                any_real_request = True

            if result_key:
                aggregated.extend(data.get(result_key, []))
            else:
                aggregated.append(data)

            pagination = data.get("pagination", {})
            total = pagination.get("total", 0)
            offset = pagination.get("offset", 0)

            while offset + limit < total:
                offset += limit
                params["offset"] = offset
                page_data = get_page(params)
                # Check if this request was real (not from cache)
                if self.last_response_from_cache is False:
                    any_real_request = True

                if result_key:
                    aggregated.extend(page_data.get(result_key, []))
                else:
                    aggregated.append(page_data)

            # Only increment counter once if any request was real and has valid API key
            if any_real_request and self.api_key and (isinstance(self.api_key, str) and self.api_key.strip()):
                self._check_daily_limit()
                self._increment_usage()
            # Set last_response_from_cache based on whether all were from cache
            self.last_response_from_cache = not any_real_request
            # Reset pagination flag
            self._in_pagination = False

            return aggregated

        return _async_mode() if async_mode else _sync_mode()


    def is_from_cache(self) -> bool:
        """
        Returns True if the last response was retrieved from cache.
        Returns False if response was not from cache or cache status is unknown.
        """
        return self.last_response_from_cache is True
    
    @classmethod
    def _get_endpoints_config(cls):
        """
        Get endpoints configuration.
        
        Returns:
            dict: Dictionary mapping endpoint names to (auto_paginate, result_key) tuples.
        """
        return {
            "search": (True, "segments"),
            "schedule": (True, "schedule"),
            "nearest_stations": (True, "stations"),
            "thread": (False, None),
            "nearest_settlement": (False, None),
            "carrier": (False, None),
            "stations_list": (False, None),
            "copyright": (False, None)
        }
    
    @classmethod
    def _create_wrapped_methods(cls):
        endpoints = cls._get_endpoints_config()
        
        for name, (auto_paginate, result_key) in endpoints.items():
            setattr(cls, name, lambda self, params=None, ep=name, ap=auto_paginate, rk=result_key: self.get(ep, params, auto_paginate=ap, result_key=rk))

###############################################################################
# Synchronous client
###############################################################################
class YaraspClient(_YaraspClientBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def get(self, endpoint, params=None, auto_paginate=False, result_key=None):
        params = self._prepare_params(params)
        url = self._build_url(endpoint)

        def get_page(p):
            response = self.http_client.get(url, params=p, extensions={"force_cache": True})
            self._log_and_check_limits(response)
            return self._parse_json_response_sync(response)

        if auto_paginate:
            return self._get_paginated_results(get_page, params, result_key=result_key, async_mode=False)

        return get_page(params)
    


###############################################################################
# Asynchronous client
###############################################################################
class AsyncYaraspClient(_YaraspClientBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_http_client(async_mode=True)

    async def get(self, endpoint, params=None, auto_paginate=False, result_key=None):
        params = self._prepare_params(params)
        url = self._build_url(endpoint)

        async def get_page(p):
            response = await self.http_client.get(url, params=p, extensions={"force_cache": True})
            self._log_and_check_limits(response)
            return await self._parse_json_response_async(response)

        if auto_paginate:
            return await self._get_paginated_results(get_page, params, result_key=result_key, async_mode=True)
        
        return await get_page(params)



YaraspClient._create_wrapped_methods()
AsyncYaraspClient._create_wrapped_methods()