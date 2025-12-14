"""
Utility functions and classes for yarasp module.

This module contains helper functions, classes, and constants used by
YaraspClient and AsyncYaraspClient classes.
"""

import os
import json
import logging
import math
from datetime import date
from typing import Union


def format_size(size_in_units):
    """Formats data size in human-readable format."""
    units = ["B", "KB", "MB"]
    index = 0
    while size_in_units >= 1024 and index < len(units) - 1:
        size_in_units /= 1024.0
        index += 1
    if index == 2 and size_in_units > 300:
        logging.warning("Response is suspiciously big size, it's recommended to enable verbose mode and check manually that the use of this module corresponds to the desired behavior")
    return f"{round(size_in_units)}{units[index]}"


def human_readable_size(size_bytes):
    """Converts size in bytes to human-readable format (KB, MB, GB)."""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    size = round(size_bytes / p, 2)
    return f"{size}{size_names[i]}"


class JSONUsageCounter:
    """
    API key usage counter stored in a JSON file.
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self._load()

    def _load(self):
        try:
            with open(self.file_path, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {}

    def _save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f)

    def _get_today_key(self):
        return date.today().isoformat()

    def get_count(self):
        return self.data.get(self._get_today_key(), 0)

    def increment(self):
        key = self._get_today_key()
        self.data[key] = self.data.get(key, 0) + 1
        self._save()
        return self.data[key]


CacheStorageType = Union[
    "hishel.FileStorage",
    "hishel.InMemoryStorage",
    "hishel.RedisStorage",
    "hishel.SQLiteStorage",
    "hishel.S3Storage",
    "hishel.AsyncBaseStorage"
]


def _create_safe_storage_wrapper(storage):
    """
    Create a wrapper class that inherits from storage's class to pass isinstance checks.
    
    This allows the wrapper to be used where BaseStorage is expected by hishel.
    """
    import hishel
    
    # Inherit from storage's class so isinstance checks pass
    # storage.__class__ is either FileStorage, SQLiteStorage, etc., which all inherit from BaseStorage
    class SafeStorageWrapper(storage.__class__):
        """
        Wrapper over cache storage that removes apikey from request URL before storing.
        
        This prevents API keys from being saved in cache files, improving security.
        The wrapper intercepts store() calls and cleans the URL from apikey parameter
        before passing the request to the underlying storage.
        """
        
        def __init__(self, wrapped_storage):
            """Initialize wrapper with underlying storage."""
            self._wrapped_storage = wrapped_storage
            # Call super().__init__() to properly initialize the base class
            # BaseStorage accepts optional serializer and ttl parameters
            super().__init__(None, None)
            # Copy all attributes from wrapped storage to maintain compatibility
            for attr in dir(wrapped_storage):
                if not attr.startswith('_') and not callable(getattr(wrapped_storage, attr, None)):
                    try:
                        setattr(self, attr, getattr(wrapped_storage, attr))
                    except (AttributeError, TypeError):
                        pass
        
        def _clean_url_from_apikey(self, url_str):
            """Remove apikey parameter from URL string."""
            from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
            parsed = urlparse(str(url_str))
            query_params = [(k, v) for k, v in parse_qsl(parsed.query) if k.lower() != "apikey"]
            new_query = urlencode(query_params)
            cleaned_url = urlunparse((
                parsed.scheme, parsed.netloc, parsed.path,
                parsed.params, new_query, parsed.fragment
            ))
            return cleaned_url
        
        def _create_clean_request(self, request):
            """Create a new request object with URL cleaned from apikey."""
            import httpcore
            
            if not hasattr(request, 'url') or not request.url:
                return request
            
            cleaned_url = self._clean_url_from_apikey(request.url)
            
            # Create new request with cleaned URL
            # Preserve all other attributes
            try:
                clean_request = httpcore.Request(
                    method=request.method,
                    url=cleaned_url,
                    headers=dict(request.headers) if hasattr(request, 'headers') else {},
                    content=getattr(request, 'stream', None),
                    extensions=getattr(request, 'extensions', {})
                )
                return clean_request
            except Exception:
                # If we can't create clean request, return original
                # This shouldn't happen, but better safe than sorry
                return request
        
        def store(self, key, response, request, metadata=None):
            """
            Store request in cache after removing apikey from URL.
            
            Args:
                key: Cache key
                response: HTTP response object
                request: HTTP request object
                metadata: Cache metadata (optional)
                
            Returns:
                Result from underlying storage.store()
            """
            clean_request = self._create_clean_request(request)
            return self._wrapped_storage.store(key, response, clean_request, metadata)
        
        def retrieve(self, key):
            """Retrieve cached response by key."""
            return self._wrapped_storage.retrieve(key)
        
        def delete(self, key):
            """Delete cached response by key."""
            return self._wrapped_storage.delete(key)
        
        def __getattr__(self, name):
            """Forward all other attribute access to underlying storage."""
            return getattr(self._wrapped_storage, name)
    
    return SafeStorageWrapper(storage)


def _create_async_safe_storage_wrapper(storage):
    """
    Create an async wrapper class that inherits from storage's class to pass isinstance checks.
    
    This allows the wrapper to be used where AsyncBaseStorage is expected by hishel.
    """
    import hishel
    
    # Inherit from storage's class so isinstance checks pass
    # storage.__class__ is either AsyncFileStorage, AsyncSQLiteStorage, etc., which all inherit from AsyncBaseStorage
    class AsyncSafeStorageWrapper(storage.__class__):
        """
        Async wrapper over cache storage that removes apikey from request URL before storing.
        
        This prevents API keys from being saved in cache files, improving security.
        The wrapper intercepts store() calls and cleans the URL from apikey parameter
        before passing the request to the underlying storage.
        """
        
        def __init__(self, wrapped_storage):
            """Initialize wrapper with underlying storage."""
            self._wrapped_storage = wrapped_storage
            # Call super().__init__() to properly initialize the base class
            # AsyncBaseStorage accepts optional serializer and ttl parameters
            super().__init__(None, None)
            # Copy all attributes from wrapped storage to maintain compatibility
            for attr in dir(wrapped_storage):
                if not attr.startswith('_') and not callable(getattr(wrapped_storage, attr, None)):
                    try:
                        setattr(self, attr, getattr(wrapped_storage, attr))
                    except (AttributeError, TypeError):
                        pass
        
        def _clean_url_from_apikey(self, url_str):
            """Remove apikey parameter from URL string."""
            from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
            parsed = urlparse(str(url_str))
            query_params = [(k, v) for k, v in parse_qsl(parsed.query) if k.lower() != "apikey"]
            new_query = urlencode(query_params)
            cleaned_url = urlunparse((
                parsed.scheme, parsed.netloc, parsed.path,
                parsed.params, new_query, parsed.fragment
            ))
            return cleaned_url
        
        def _create_clean_request(self, request):
            """Create a new request object with URL cleaned from apikey."""
            import httpcore
            
            if not hasattr(request, 'url') or not request.url:
                return request
            
            cleaned_url = self._clean_url_from_apikey(request.url)
            
            # Create new request with cleaned URL
            # Preserve all other attributes
            try:
                clean_request = httpcore.Request(
                    method=request.method,
                    url=cleaned_url,
                    headers=dict(request.headers) if hasattr(request, 'headers') else {},
                    content=getattr(request, 'stream', None),
                    extensions=getattr(request, 'extensions', {})
                )
                return clean_request
            except Exception:
                # If we can't create clean request, return original
                # This shouldn't happen, but better safe than sorry
                return request
        
        async def store(self, key, response, request, metadata=None):
            """
            Store request in cache after removing apikey from URL.
            
            Args:
                key: Cache key
                response: HTTP response object
                request: HTTP request object
                metadata: Cache metadata (optional)
                
            Returns:
                Result from underlying storage.store()
            """
            clean_request = self._create_clean_request(request)
            return await self._wrapped_storage.store(key, response, clean_request, metadata)
        
        async def retrieve(self, key):
            """Retrieve cached response by key."""
            return await self._wrapped_storage.retrieve(key)
        
        async def delete(self, key):
            """Delete cached response by key."""
            return await self._wrapped_storage.delete(key)
        
        def __getattr__(self, name):
            """Forward all other attribute access to underlying storage."""
            return getattr(self._wrapped_storage, name)
    
    return AsyncSafeStorageWrapper(storage)

