# Yarasp Documentation

Welcome to the **Yarasp** documentation! Yarasp is a Python client library for accessing the [Yandex Schedule API](https://yandex.ru/dev/rasp/doc/).

## Features

- 🚀 **Synchronous and Asynchronous Support** - Use `YaraspClient` for synchronous requests or `AsyncYaraspClient` for async/await patterns
- 💾 **HTTP Caching** - Built-in caching using `hishel` to reduce API calls and improve performance
- 🔐 **Secure Caching** - API keys are automatically excluded from cache keys to prevent sensitive data leakage
- 📊 **API Usage Tracking** - Monitor daily API request usage with configurable limits
- 🛡️ **Safe Mode** - Enabled by default to prevent exceeding daily API limits
- 🔄 **Automatic Pagination** - Built-in support for automatic pagination on supported endpoints
- 📝 **Flexible Configuration** - Configure cache storage, request limits, and more

## Quick Example

```python
import os
from yarasp import YaraspClient

# Set your API key (required)
os.environ['YARASP_API_KEY'] = 'your-api-key-here'

# Create a client
client = YaraspClient()

# Search for routes
results = client.search(params={
    "from": "c213",
    "to": "c2",
    "date": "2024-01-15"
})

print(f"Found {len(results)} routes")
```

## Installation

```bash
pip install yarasp
```

Or using `uv`:

```bash
uv add yarasp
```

See the [Installation Guide](installation.md) for detailed instructions.

## Getting Started

1. **Get your API key** from [Yandex Developer Portal](https://developer.tech.yandex.ru/)
2. **Set the environment variable**:
   ```bash
   export YARASP_API_KEY='your-api-key-here'
   ```
3. **Follow the [Quick Start Guide](quickstart.md)**

## Documentation Structure

- **[Installation](installation.md)** - How to install and configure Yarasp
- **[Quick Start](quickstart.md)** - Get up and running in minutes
- **[API Reference](api-reference.md)** - Complete API documentation
- **[Configuration](configuration.md)** - Configuration options and environment variables
- **[Examples](examples.md)** - Code examples for common use cases
- **[Deployment](deployment.md)** - Instructions for publishing documentation

## Requirements

- Python >= 3.9
- `httpx` - HTTP client library
- `hishel` (version <= 0.1.15) - HTTP caching library

## License

This project is licensed under the MIT License.

## Support

- **Issues**: [GitHub Issues](https://github.com/pavelsr/yarasp/issues)
- **Source Code**: [GitHub Repository](https://github.com/pavelsr/yarasp)

