# Examples

This page contains practical examples demonstrating how to use Yarasp for common tasks.

## Basic Usage

### Search for Routes

```python
from yarasp import YaraspClient

client = YaraspClient()

# Search for routes from Moscow to Saint Petersburg
results = client.search(params={
    "from": "c213",        # Moscow station code
    "to": "c2",            # Saint Petersburg station code
    "date": "2024-01-15",  # Date in YYYY-MM-DD format
    "transport_types": "train"
})

print(f"Found {len(results)} routes")

for route in results[:5]:  # Show first 5 routes
    thread = route.get('thread', {})
    print(f"- {thread.get('title', 'Unknown')}")
    print(f"  Departure: {route.get('departure', 'N/A')}")
    print(f"  Arrival: {route.get('arrival', 'N/A')}")
```

### Get Station Schedule

```python
from yarasp import YaraspClient

client = YaraspClient()

# Get schedule for a specific station
schedule = client.schedule(params={
    "station": "s9600213",  # Station code
    "date": "2024-01-15",
    "transport_types": "suburban"
})

print(f"Schedule entries: {len(schedule)}")

for entry in schedule[:10]:  # Show first 10 entries
    thread = entry.get('thread', {})
    print(f"- {thread.get('title', 'Unknown')} at {entry.get('departure', 'N/A')}")
```

### Find Nearest Stations

```python
from yarasp import YaraspClient

client = YaraspClient()

# Find stations near coordinates (Moscow city center)
stations = client.nearest_stations(params={
    "lat": 55.7558,      # Latitude
    "lng": 37.6173,      # Longitude
    "distance": 50,      # Search radius in kilometers
    "transport_types": "suburban"
})

print(f"Found {len(stations)} nearby stations")

for station in stations:
    print(f"- {station.get('title', 'Unknown')} "
          f"(distance: {station.get('distance', 0):.2f} km)")
```

## Asynchronous Usage

### Async Route Search

```python
import asyncio
from yarasp import AsyncYaraspClient

async def search_routes():
    client = AsyncYaraspClient()
    
    results = await client.search(params={
        "from": "c213",
        "to": "c2",
        "date": "2024-01-15"
    })
    
    return results

# Run async function
results = asyncio.run(search_routes())
print(f"Found {len(results)} routes")
```

### Multiple Concurrent Requests

```python
import asyncio
from yarasp import AsyncYaraspClient

async def fetch_multiple_routes():
    client = AsyncYaraspClient()
    
    tasks = [
        client.search(params={
            "from": "c213",
            "to": "c2",
            "date": "2024-01-15"
        }),
        client.search(params={
            "from": "c2",
            "to": "c213",
            "date": "2024-01-16"
        }),
        client.search(params={
            "from": "c213",
            "to": "c54",  # Ekaterinburg
            "date": "2024-01-15"
        })
    ]
    
    results = await asyncio.gather(*tasks)
    return results

# Execute all searches concurrently
all_results = asyncio.run(fetch_multiple_routes())
for i, routes in enumerate(all_results, 1):
    print(f"Route {i}: {len(routes)} options found")
```

## Advanced Usage

### Check Cache Status

```python
from yarasp import YaraspClient

client = YaraspClient(verbose=True)

# First request - will be fetched from API
results1 = client.search(params={"from": "c213", "to": "c2"})
print(f"First request from cache: {client.is_from_cache()}")  # False

# Second request - will be served from cache
results2 = client.search(params={"from": "c213", "to": "c2"})
print(f"Second request from cache: {client.is_from_cache()}")  # True
```

### Monitor API Usage

```python
from yarasp import YaraspClient, JSONUsageCounter

client = YaraspClient()

# Make some requests
client.search(params={"from": "c213", "to": "c2"})
client.schedule(params={"station": "s9600213"})

# Check usage counter
counter = client.usage_counter
today_count = counter.get_count()
print(f"API requests made today: {today_count}")
```

### Custom Cache Storage

```python
import hishel
from yarasp import YaraspClient

# Use SQLite for cache storage
storage = hishel.SQLiteStorage(path="./cache.db")
client = YaraspClient(cache_storage=storage)

# Use the client normally
results = client.search(params={"from": "c213", "to": "c2"})
```

### Error Handling

```python
from yarasp import YaraspClient
import httpx

client = YaraspClient(safe_mode=True, daily_limit=10)

try:
    # Make multiple requests
    for i in range(15):
        results = client.search(params={
            "from": "c213",
            "to": "c2",
            "date": f"2024-01-{15+i}"
        })
        print(f"Request {i+1} successful")
except RuntimeError as e:
    print(f"Daily limit exceeded: {e}")
except httpx.HTTPError as e:
    print(f"Network error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Disable Caching for Fresh Data

```python
from yarasp import YaraspClient

# Create client without caching
client = YaraspClient(cache_enabled=False)

# All requests will be live
results = client.search(params={"from": "c213", "to": "c2"})
```

## Real-World Scenarios

### Travel Planner

```python
from yarasp import YaraspClient
from datetime import datetime, timedelta

def find_routes_for_week(from_code, to_code, start_date):
    """Find routes for a week starting from start_date."""
    client = YaraspClient()
    routes_by_date = {}
    
    for i in range(7):
        date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=i)).strftime("%Y-%m-%d")
        try:
            routes = client.search(params={
                "from": from_code,
                "to": to_code,
                "date": date,
                "transport_types": "train"
            })
            routes_by_date[date] = routes
            print(f"{date}: {len(routes)} routes found")
        except Exception as e:
            print(f"{date}: Error - {e}")
            routes_by_date[date] = []
    
    return routes_by_date

# Usage
routes = find_routes_for_week("c213", "c2", "2024-01-15")
```

### Station Finder

```python
from yarasp import YaraspClient

def find_station_by_name(name, client=None):
    """Find station codes by name."""
    if client is None:
        client = YaraspClient()
    
    # Get all stations
    stations = client.stations_list()
    
    # Search for matching stations
    matches = [
        station for station in stations
        if name.lower() in station.get('title', '').lower()
    ]
    
    return matches

# Usage
moscow_stations = find_station_by_name("Москва")
for station in moscow_stations[:5]:
    print(f"{station.get('title')} - {station.get('code')}")
```

### Route Comparison

```python
from yarasp import YaraspClient

def compare_routes(from_code, to_code, dates):
    """Compare routes for different dates."""
    client = YaraspClient()
    comparison = {}
    
    for date in dates:
        routes = client.search(params={
            "from": from_code,
            "to": to_code,
            "date": date
        })
        
        if routes:
            # Find fastest route
            fastest = min(routes, key=lambda r: r.get('duration', float('inf')))
            comparison[date] = {
                "total_routes": len(routes),
                "fastest_duration": fastest.get('duration'),
                "fastest_title": fastest.get('thread', {}).get('title')
            }
    
    return comparison

# Usage
dates = ["2024-01-15", "2024-01-16", "2024-01-17"]
comparison = compare_routes("c213", "c2", dates)

for date, info in comparison.items():
    print(f"{date}: {info['total_routes']} routes, "
          f"fastest: {info['fastest_title']} ({info['fastest_duration']} min)")
```

## Tips and Best Practices

1. **Use caching**: Keep `cache_enabled=True` (default) to reduce API calls
2. **Monitor usage**: Check `usage_counter.get_count()` regularly to stay within limits
3. **Enable safe mode**: Keep `safe_mode=True` (default) to prevent exceeding limits
4. **Use async client**: For multiple requests, use `AsyncYaraspClient` with `asyncio.gather()`
5. **Handle errors**: Always wrap API calls in try-except blocks
6. **Check cache status**: Use `is_from_cache()` to verify caching is working

For more information, see the [API Reference](api-reference.md) and [Configuration](configuration.md) pages.

