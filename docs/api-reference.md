# API Reference

This page provides detailed documentation for all public APIs in Yarasp.

## Clients

### YaraspClient

Synchronous client for accessing Yandex Schedule API.

```python
from yarasp import YaraspClient

client = YaraspClient(**kwargs)
```

**Parameters:**

- `base_url` (str, default: `"https://api.rasp.yandex.net/v3.0"`) - Base URL for API requests
- `verbose` (bool, default: `False`) - Enable verbose logging
- `safe_mode` (bool, default: `True`) - Enable safe mode (raises error when daily limit exceeded)
- `daily_limit` (int, default: `500`) - Daily API request limit
- `counter_backend` (str, default: `"json"`) - Usage counter backend (`"json"` or `"redis"`)
- `counter_storage_path` (str, default: `"yarasp_counter.json"`) - Path to JSON counter file
- `cache_enabled` (bool, default: `True`) - Enable HTTP caching
- `cache_storage` (optional) - Custom cache storage backend (hishel storage instance)
- `user_agent` (str, default: `"httpx"`) - User-Agent header for requests

**Methods:**

#### search(params=None, auto_paginate=True)

Search for routes between stations.

**Parameters:**
- `params` (dict, optional) - Request parameters (from, to, date, etc.)
- `auto_paginate` (bool, default: `True`) - Automatically fetch all pages
- `result_key` (str, optional, default: `"segments"`) - Key to extract from paginated results

**Returns:** List of route segments

**Example:**
```python
results = client.search(params={
    "from": "c213",
    "to": "c2",
    "date": "2024-01-15"
})
```

#### schedule(params=None, auto_paginate=True)

Get station schedule.

**Parameters:**
- `params` (dict, optional) - Request parameters (station, date, etc.)
- `auto_paginate` (bool, default: `True`) - Automatically fetch all pages
- `result_key` (str, optional, default: `"schedule"`) - Key to extract from paginated results

**Returns:** List of schedule entries

**Example:**
```python
schedule = client.schedule(params={
    "station": "s9600213",
    "date": "2024-01-15"
})
```

#### thread(params=None)

Get route thread information.

**Parameters:**
- `params` (dict, optional) - Request parameters (uid, etc.)

**Returns:** Thread information dictionary

**Example:**
```python
thread_info = client.thread(params={"uid": "12345"})
```

#### nearest_stations(params=None, auto_paginate=True)

Find nearest stations by coordinates.

**Parameters:**
- `params` (dict, optional) - Request parameters (lat, lng, distance, etc.)
- `auto_paginate` (bool, default: `True`) - Automatically fetch all pages
- `result_key` (str, optional, default: `"stations"`) - Key to extract from paginated results

**Returns:** List of station information

**Example:**
```python
stations = client.nearest_stations(params={
    "lat": 55.7558,
    "lng": 37.6173,
    "distance": 50
})
```

#### nearest_settlement(params=None)

Find nearest settlement by coordinates.

**Parameters:**
- `params` (dict, optional) - Request parameters (lat, lng, etc.)

**Returns:** Settlement information dictionary

**Example:**
```python
settlement = client.nearest_settlement(params={
    "lat": 55.7558,
    "lng": 37.6173
})
```

#### carrier(params=None)

Get carrier information.

**Parameters:**
- `params` (dict, optional) - Request parameters (code, etc.)

**Returns:** Carrier information dictionary

**Example:**
```python
carrier_info = client.carrier(params={"code": "SU"})
```

#### stations_list(params=None)

Get list of stations.

**Parameters:**
- `params` (dict, optional) - Request parameters

**Returns:** List of stations

**Example:**
```python
stations = client.stations_list()
```

#### copyright(params=None)

Get copyright information.

**Parameters:**
- `params` (dict, optional) - Request parameters

**Returns:** Copyright information dictionary

**Example:**
```python
copyright_info = client.copyright()
```

#### get(endpoint, params=None, auto_paginate=False, result_key=None)

Generic method to call any API endpoint.

**Parameters:**
- `endpoint` (str) - API endpoint path
- `params` (dict, optional) - Request parameters
- `auto_paginate` (bool, default: `False`) - Automatically fetch all pages
- `result_key` (str, optional) - Key to extract from paginated results

**Returns:** API response (list if paginated, dict otherwise)

**Example:**
```python
result = client.get("custom/endpoint", params={"param": "value"})
```

#### is_from_cache()

Check if the last response was retrieved from cache.

**Returns:** `bool` - `True` if last response was from cache, `False` otherwise

**Example:**
```python
client.search(params={"from": "c213", "to": "c2"})
if client.is_from_cache():
    print("Served from cache!")
```

---

### AsyncYaraspClient

Asynchronous client for accessing Yandex Schedule API.

```python
from yarasp import AsyncYaraspClient

client = AsyncYaraspClient(**kwargs)
```

**Parameters:** Same as `YaraspClient`

**Methods:** All methods from `YaraspClient`, but they are `async` and must be awaited.

**Example:**
```python
import asyncio
from yarasp import AsyncYaraspClient

async def main():
    client = AsyncYaraspClient()
    results = await client.search(params={
        "from": "c213",
        "to": "c2",
        "date": "2024-01-15"
    })
    print(f"Found {len(results)} routes")

asyncio.run(main())
```

---

## Utilities

### JSONUsageCounter

Counter for tracking API key usage stored in a JSON file.

```python
from yarasp import JSONUsageCounter

counter = JSONUsageCounter(file_path="yarasp_counter.json")
```

**Methods:**

#### get_count()

Get the current usage count for today.

**Returns:** `int` - Number of API requests made today

**Example:**
```python
count = counter.get_count()
print(f"Made {count} API requests today")
```

#### increment()

Increment the usage counter for today.

**Returns:** `int` - Updated count after incrementing

**Example:**
```python
count = counter.increment()
print(f"Usage count: {count}")
```

---

## Constants

### Environment Variables

- `YARASP_API_KEY` (required) - API key for Yandex Schedule API
- `YARASP_API_DAILY_LIMIT` (optional, default: `500`) - Daily request limit
- `YARASP_SAFE_MODE` (optional, default: `1`) - Enable safe mode (`1` or `0`)

---

## Exceptions

### RuntimeError

Raised when:
- API key is not set in environment variables
- Daily API limit is exceeded (when safe mode is enabled)

### NotImplementedError

Raised when trying to use Redis counter backend (not yet implemented).

### ValueError

Raised when unsupported counter backend is specified.

---

## Type Hints

Yarasp includes type hints for better IDE support and static type checking.

```python
from yarasp import YaraspClient
from typing import List, Dict, Any

client: YaraspClient = YaraspClient()
results: List[Dict[str, Any]] = client.search(params={"from": "c213", "to": "c2"})
```

