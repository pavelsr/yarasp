# Installation

## Prerequisites

- Python >= 3.9
- pip or uv package manager

## Install from PyPI

The easiest way to install Yarasp is using pip:

```bash
pip install yarasp
```

## Install using uv

This project uses `uv` for dependency management. To install using uv:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the package
uv add yarasp
```

## Install from Source

If you want to install from source:

```bash
# Clone the repository
git clone https://github.com/pavelsr/yarasp.git
cd yarasp

# Install using uv (recommended)
uv sync
uv pip install -e .

# Or using pip
pip install -e .
```

## Verify Installation

After installation, verify that the package is correctly installed:

```python
import yarasp
print(yarasp.__version__)
```

You should see the version number printed (e.g., `0.1.0`).

## Dependencies

Yarasp requires the following dependencies:

- `httpx` - HTTP client library (automatically installed)
- `hishel` (>=0.1.1,<0.2.0) - HTTP caching library (automatically installed)

These are automatically installed when you install Yarasp.

## Optional Dependencies

For development and testing:

```bash
uv sync --extra dev
```

This installs:
- `pytest` - Testing framework
- `pytest-httpx` - HTTP mocking for tests
- `ruff` - Linter and formatter
- `mypy` - Static type checker
- `coverage` - Code coverage tool

## Environment Setup

Before using Yarasp, you need to set up your API key:

```bash
export YARASP_API_KEY='your-api-key-here'
```

Or on Windows:

```cmd
set YARASP_API_KEY=your-api-key-here
```

You can get your API key from the [Yandex Developer Portal](https://developer.tech.yandex.ru/).

## Next Steps

- Read the [Quick Start Guide](quickstart.md) to get started
- Check the [Configuration](configuration.md) page for all configuration options

