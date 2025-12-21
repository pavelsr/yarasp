# yarasp

[![Yandex Schedule](https://yandex.ru/support/rasp/docs-assets/support-rasp/rev/r18182093/ru/_images/footer.png)](https://rasp.yandex.ru/)

**This is an unofficial community-developed module** for accessing the Yandex Schedule API.

Python client library for the [Yandex Schedule API](https://yandex.ru/dev/rasp/doc/) with HTTP caching, API key usage tracking, and automatic pagination support.

## Features

- ✅ **Synchronous and asynchronous** clients (`YaraspClient` and `AsyncYaraspClient`)
- ✅ **HTTP caching** with secure cache key generation (API keys excluded from cache keys)
- ✅ **API key usage tracking** (incremented only for live requests, not from cache)
- ✅ **Safe mode** (enabled by default) - prevents exceeding daily API limits
- ✅ **Automatic pagination** - aggregates data from all pages with `auto_paginate=True`
- ✅ **Force live requests** - bypass cache with `force_live=True`
- ✅ **Cache-only mode** - only return data from cache, raise `CacheMissError` if not cached
- ✅ **Multiple cache backends** - FileStorage (default), SQLiteStorage, RedisStorage
- ✅ **Type hints** - full type support for better IDE experience

## Installation

```bash
pip install yarasp


Or using `uv`:

```bash
uv add yarasp
```

## Quick Start

### Setup

Set your API key as an environment variable:

```bash
export YARASP_API_KEY="your-api-key-here"
```

Get your API key from [Yandex Developer](https://developer.tech.yandex.ru/).

### Basic Usage

```python
from yarasp import YaraspClient

# Create client
client = YaraspClient()

# Search for stations
results = client.search(query="Москва")

# Get schedule between stations
schedule = client.schedule(
    from_="s2000001",  # Moscow
    to="s2000002",    # Saint Petersburg
    date="2024-01-15"
)

# Get thread information
thread = client.thread(uid="12345")

# Get nearest stations
nearest = client.nearest_stations(lat=55.7558, lng=37.6173)
```

### Async Usage

```python
from yarasp import AsyncYaraspClient

async def main():
    client = AsyncYaraspClient()
    
    # Async requests
    results = await client.search(query="Москва")
    schedule = await client.schedule(from_="s2000001", to="s2000002")
    
    return results

# Run with asyncio
import asyncio
asyncio.run(main())
```

### Automatic Pagination

```python
# Automatically fetch all pages
all_results = client.search(
    query="Москва",
    auto_paginate=True,
    result_key="items"  # Key in response containing the list
)
```

### Check Cache Status

```python
result = client.search(query="Москва")
if client.is_from_cache():
    print("Response came from cache")
else:
    print("Live API request")
```

### Cache-Only Mode

Use `cache_only=True` to ensure you only get data from cache. This is useful when you want to avoid making API requests and only work with previously cached data:

```python
from yarasp import YaraspClient, CacheMissError

client = YaraspClient(cache_only=True)

try:
    # This will only return data if it's in cache
    result = client.search(query="Москва")
    print("Got cached data")
except CacheMissError:
    print("Data not in cache - need to fetch it first with cache_only=False")
```

## Configuration

### Environment Variables

- `YARASP_API_KEY` (required) - Your Yandex Schedule API key
- `YARASP_API_DAILY_LIMIT` (optional, default: 500) - Daily request limit
- `YARASP_SAFE_MODE` (optional, default: 1) - Enable safe mode (1) or disable (0)

### Client Options

```python
client = YaraspClient(
    cache_enabled=True,           # Enable/disable caching
    cache_only=False,             # Only use cache (raises CacheMissError if not cached)
    safe_mode=True,              # Enable safe mode (raises error on limit exceed)
    daily_limit=500,             # Daily API request limit
    verbose=False,               # Enable verbose logging
    counter_backend="json",      # Usage counter backend: "json", "redis", or "sqlite"
    counter_storage_path="yarasp_counter.json"  # Path for counter storage
)
```

## Available Methods

The client provides methods for all Yandex Schedule API endpoints:

- `search()` - Search for stations, settlements, and carriers
- `schedule()` - Get schedule between stations
- `thread()` - Get thread information
- `nearest_stations()` - Find nearest stations by coordinates
- `nearest_settlement()` - Find nearest settlement by coordinates
- `carrier()` - Get carrier information
- `stations_list()` - Get list of stations
- `copyright()` - Get copyright information

See the [official API documentation](https://yandex.ru/dev/rasp/doc/) for detailed endpoint parameters and response formats.

## Requirements

- Python >= 3.9
- httpx (via hishel)
- hishel >= 0.1.1, < 0.2.0

## License

MIT License

## Links

- **Yandex Schedule**: https://rasp.yandex.ru/
- **Module Documentation**: https://pavelsr.github.io/yarasp/
- **API Documentation**: https://yandex.ru/dev/rasp/doc/
- **GitHub Repository**: https://github.com/pavelsr/yarasp
- **Issue Tracker**: https://github.com/pavelsr/yarasp/issues
