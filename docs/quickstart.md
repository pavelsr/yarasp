# Quick Start

This guide will help you get started with Yarasp in just a few minutes.

## Prerequisites

1. Python >= 3.9 installed
2. Yarasp package installed (see [Installation](installation.md))
3. Yandex Schedule API key (get it from [Yandex Developer Portal](https://developer.tech.yandex.ru/))

## Step 1: Set Your API Key

Set the `YARASP_API_KEY` environment variable:

```bash
export YARASP_API_KEY='your-api-key-here'
```

Or set it in your Python code:

```python
import os
os.environ['YARASP_API_KEY'] = 'your-api-key-here'
```

## Step 2: Create a Client

### Synchronous Client

```python
from yarasp import YaraspClient

client = YaraspClient()
```

### Asynchronous Client

```python
from yarasp import AsyncYaraspClient

client = AsyncYaraspClient()
```

## Step 3: Make Your First Request

### Search for Routes

```python
# Synchronous
results = client.search(params={
    "from": "c213",  # Moscow station code
    "to": "c2",      # Saint Petersburg station code
    "date": "2024-01-15"
})

print(f"Found {len(results)} routes")
for route in results[:3]:  # Show first 3 routes
    print(f"- {route.get('thread', {}).get('title', 'Unknown')}")
```

```python
# Asynchronous
import asyncio

async def main():
    results = await client.search(params={
        "from": "c213",
        "to": "c2",
        "date": "2024-01-15"
    })
    print(f"Found {len(results)} routes")

asyncio.run(main())
```

### Get Station Schedule

```python
# Get schedule for a station
schedule = client.schedule(params={
    "station": "s9600213",
    "date": "2024-01-15"
})

print(f"Schedule entries: {len(schedule)}")
```

### Find Nearest Stations

```python
# Find nearest stations to coordinates
stations = client.nearest_stations(params={
    "lat": 55.7558,
    "lng": 37.6173,
    "distance": 50
})

print(f"Found {len(stations)} nearby stations")
```

## Available Methods

Yarasp provides convenient methods for all Yandex Schedule API endpoints:

- `search()` - Search for routes between stations
- `schedule()` - Get station schedule
- `thread()` - Get route thread information
- `nearest_stations()` - Find nearest stations by coordinates
- `nearest_settlement()` - Find nearest settlement by coordinates
- `carrier()` - Get carrier information
- `stations_list()` - Get list of stations
- `copyright()` - Get copyright information

All methods support automatic pagination for endpoints that return paginated results.

## Configuration Options

You can customize the client behavior:

```python
client = YaraspClient(
    verbose=True,              # Enable verbose logging
    safe_mode=True,            # Enable safe mode (default: True)
    daily_limit=500,           # Daily API request limit (default: 500)
    cache_enabled=True,        # Enable HTTP caching (default: True)
    cache_storage=None,        # Custom cache storage backend
)
```

See the [Configuration](configuration.md) page for all available options.

## Check Cache Status

You can check if the last response came from cache:

```python
result = client.search(params={"from": "c213", "to": "c2"})
if client.is_from_cache():
    print("Response was served from cache!")
else:
    print("Response was fetched from API")
```

## Error Handling

The client will raise exceptions when:

- API key is not set: `RuntimeError`
- Daily limit exceeded (with safe mode): `RuntimeError`
- Network errors: `httpx.HTTPError`

```python
from yarasp import YaraspClient
import httpx

try:
    client = YaraspClient()
    results = client.search(params={"from": "c213", "to": "c2"})
except RuntimeError as e:
    print(f"Configuration error: {e}")
except httpx.HTTPError as e:
    print(f"Network error: {e}")
```

## Next Steps

- Explore the [API Reference](api-reference.md) for detailed method documentation
- Check out [Examples](examples.md) for more use cases
- Read about [Configuration](configuration.md) options

