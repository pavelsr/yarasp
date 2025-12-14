# Configuration

Yarasp can be configured through environment variables and client initialization parameters.

## Environment Variables

### Required

#### YARASP_API_KEY

Your Yandex Schedule API key. This is **required** for Yarasp to work.

```bash
export YARASP_API_KEY='your-api-key-here'
```

You can get your API key from the [Yandex Developer Portal](https://developer.tech.yandex.ru/).

### Optional

#### YARASP_API_DAILY_LIMIT

Daily API request limit. Default: `500`

```bash
export YARASP_API_DAILY_LIMIT=1000
```

When safe mode is enabled, the client will raise a `RuntimeError` if this limit is exceeded.

#### YARASP_SAFE_MODE

Enable or disable safe mode. Default: `1` (enabled)

```bash
export YARASP_SAFE_MODE=1  # Enabled
export YARASP_SAFE_MODE=0  # Disabled
```

When enabled, the client will raise a `RuntimeError` if the daily API limit is exceeded, preventing accidental overuse.

## Client Parameters

You can configure the client behavior when creating an instance:

```python
from yarasp import YaraspClient

client = YaraspClient(
    base_url="https://api.rasp.yandex.net/v3.0",
    verbose=False,
    safe_mode=True,
    daily_limit=500,
    counter_backend="json",
    counter_storage_path="yarasp_counter.json",
    cache_enabled=True,
    cache_storage=None,
    user_agent="httpx"
)
```

### base_url

Base URL for API requests. Default: `"https://api.rasp.yandex.net/v3.0"`

```python
client = YaraspClient(base_url="https://api.rasp.yandex.net/v3.0")
```

### verbose

Enable verbose logging of HTTP requests. Default: `False`

When enabled, the client will log:
- HTTP method and URL
- Response status code
- Response data size
- Cache status (if response was served from cache)

```python
client = YaraspClient(verbose=True)
```

### safe_mode

Enable safe mode to prevent exceeding daily limits. Default: `True`

```python
client = YaraspClient(safe_mode=True)
```

### daily_limit

Daily API request limit. Default: `500` (or value from `YARASP_API_DAILY_LIMIT`)

```python
client = YaraspClient(daily_limit=1000)
```

### counter_backend

Backend for usage counter. Default: `"json"`

Supported values:
- `"json"` - Store counter in JSON file (default)
- `"redis"` - Store counter in Redis (not yet implemented)

```python
client = YaraspClient(counter_backend="json")
```

### counter_storage_path

Path to JSON counter file. Default: `"yarasp_counter.json"`

```python
client = YaraspClient(counter_storage_path="/tmp/yarasp_counter.json")
```

### cache_enabled

Enable HTTP caching. Default: `True`

```python
# Disable caching
client = YaraspClient(cache_enabled=False)

# Enable caching (default)
client = YaraspClient(cache_enabled=True)
```

### cache_storage

Custom cache storage backend. Default: `None` (uses hishel's default FileStorage)

You can provide a custom hishel storage instance:

```python
import hishel
from yarasp import YaraspClient

# Use SQLite storage
storage = hishel.SQLiteStorage()
client = YaraspClient(cache_storage=storage)

# Use Redis storage (if available)
# storage = hishel.RedisStorage(redis_client=redis_client)
# client = YaraspClient(cache_storage=storage)
```

Supported storage backends (hishel <= 0.1.15):
- `hishel.FileStorage()` - File-based storage (default)
- `hishel.SQLiteStorage()` - SQLite database storage
- `hishel.InMemoryStorage()` - In-memory storage (not persisted)

**Note:** In hishel 1.x, only SQLite storage is available. Other backends are deprecated.

### user_agent

User-Agent header for HTTP requests. Default: `"httpx"`

```python
client = YaraspClient(user_agent="MyApp/1.0")
```

## Cache Configuration

### Cache Location

By default, cache is stored in `.cache/hishel/` directory in the current working directory.

### Cache Security

Yarasp automatically excludes the `apikey` parameter from cache keys to prevent sensitive data from being stored in cache files. This is handled automatically and requires no configuration.

### Disable Caching

To disable caching completely:

```python
client = YaraspClient(cache_enabled=False)
```

## Usage Counter

### JSON Counter

The default counter backend stores usage data in a JSON file:

```json
{
  "2024-01-15": 42,
  "2024-01-16": 15
}
```

The file is automatically created when first used. Each day's count is stored separately.

### Custom Counter Path

```python
client = YaraspClient(counter_storage_path="/custom/path/counter.json")
```

## Example Configuration

Complete example with all options:

```python
import os
from yarasp import YaraspClient

# Set environment variables
os.environ['YARASP_API_KEY'] = 'your-api-key'
os.environ['YARASP_API_DAILY_LIMIT'] = '1000'
os.environ['YARASP_SAFE_MODE'] = '1'

# Create client with custom configuration
client = YaraspClient(
    verbose=True,
    safe_mode=True,
    daily_limit=1000,
    cache_enabled=True,
    counter_storage_path="./yarasp_counter.json"
)
```

## Priority Order

Configuration values are applied in the following priority order:

1. **Client parameters** (highest priority) - Values passed directly to client constructor
2. **Environment variables** - Values from environment
3. **Defaults** (lowest priority) - Hardcoded default values

Example:
```python
# Environment variable sets limit to 500
os.environ['YARASP_API_DAILY_LIMIT'] = '500'

# Client parameter overrides to 1000
client = YaraspClient(daily_limit=1000)  # Uses 1000, not 500
```

