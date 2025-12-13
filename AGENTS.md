# AI Coding Assistant Context

This document provides context for AI coding assistants (Claude Code, Gemini CLI, GitHub Copilot, Cursor, etc.) to understand yarasp project and assist with development.

## Project overview

This repository contains a Python module for accessing the Yandex Schedule API. The module provides both synchronous and asynchronous clients with HTTP caching, API key usage tracking, and automatic pagination support.

**Primary goal:** Implement changes safely without breaking public API.

**API Documentation:** The official Yandex Schedule API documentation is available at https://yandex.ru/dev/rasp/doc/. Always refer to this source when implementing new endpoints, understanding request/response formats, or verifying API behavior.

### Repo map

```
yarasp/
├── src/yarasp/          # Main package source code
│   ├── __init__.py      # Public API exports
│   └── yarasp.py        # Core client implementation
├── tests/               # Test suite
│   ├── fixtures/        # JSON test fixtures
│   └── test_*.py        # Test modules
├── pyproject.toml       # Project configuration and dependencies
├── uv.lock              # Dependency lock file
└── Makefile             # Build and development commands
```

### Technology stack

**Core dependencies:**
- `httpx` - HTTP client library (used by hishel)
- `hishel` (version <= 0.1.15) - HTTP caching library with multiple storage backends

**Build and development tools:**
- `uv` - Fast Python package installer and resolver
- `uv_build` - Build backend for uv
- `mkdocs` - Documentation generator
- `pytest` - Testing framework
- `pytest-httpx` - HTTP mocking for tests
- `ruff` - Fast Python linter and formatter
- `mypy` - Static type checker

**Python version:** >= 3.9

## Build and test commands

### Build

```bash
# Install dependencies using uv
uv sync

# Build the package
uv build
```

### Testing

```bash
# Run all tests
pytest -q

# Run tests with coverage
coverage run --source yarasp -m pytest
coverage report -m

# Run specific test file
pytest tests/test_03_pagination.py
```

### Linting and formatting

```bash
# Check code style
ruff check .

# Format code
ruff format .

# Type checking
mypy .
```

### Documentation

```bash
# Generate documentation (if mkdocs is configured)
mkdocs build

# Serve documentation locally
mkdocs serve
```

## Code style guidelines

### Core principles

**KISS (Keep It Simple, Stupid):** Choose the simplest working solution. Avoid unnecessary patterns, "layers", and configurations without clear need. Prefer straightforward implementations over complex abstractions.

**YAGNI (You Aren't Gonna Need It):** Don't add functionality "for the future", extensibility hooks, feature flags, dependency injection containers, or similar abstractions unless explicitly required right now. Solve today's problems, not tomorrow's hypothetical ones.

**SRP (Single Responsibility Principle):** Functions and classes should do one clear, well-defined task. If an object "knows too much" or handles multiple concerns, split it by responsibility into separate components.

**SoC (Separation of Concerns):** Separate domain logic from I/O operations (HTTP/CLI/DB/files). Don't mix parsing, business rules, and side effects in a single function. Keep I/O at the boundaries and core logic pure where possible.

**DRY (Don't Repeat Yourself):** Avoid code duplication, but don't abstract prematurely. If repetition occurs ≤ 2 times and abstraction would worsen readability or add unnecessary complexity, leave it as is. Wait for the third occurrence before extracting.

**Boy Scout Rule (Leave it better than you found it):** When working with existing code, make small improvements if you notice issues: fix typos, improve variable names, add missing type hints, remove dead code, or improve comments. Don't refactor everything, but leave the codebase slightly better than when you started.

**Don't Make Me Think:** Code should be self-documenting and intuitive. Use clear, descriptive names for functions, variables, and classes. The code should explain what it does without requiring extensive mental effort to understand. If you need a comment to explain what code does, consider refactoring to make the code itself clearer.

**POLS (Principle of Least Surprise):** Code should behave in a way that is least surprising to a reasonable developer. Follow established conventions, use predictable naming patterns, and ensure that methods do what their names suggest. When working with APIs, maintain consistency with existing patterns and user expectations.

### Code style rules

- Follow existing project conventions (structure, naming, formatting)
- Use type hints for all public APIs
- Keep functions focused and small
- Prefer composition over inheritance
- Use dataclasses for simple data containers
- Follow PEP 8 naming conventions
- **All comments and docstrings must be written in English**

### Avoid (anti-patterns)

**Don't:**
- Create abstract base classes or interfaces "just in case"
- Add configuration layers or feature flags without explicit requirement
- Implement dependency injection frameworks or service locators
- Mix HTTP request/response handling with business logic
- Create "helper" modules that become catch-all dumping grounds
- Over-engineer with design patterns when simple functions suffice
- Add "plugin systems" or "extensibility hooks" without current need
- Create multiple layers of abstraction for simple operations
- Use complex inheritance hierarchies when composition works
- Prematurely optimize or abstract code that's only used once or twice

**Do:**
- Keep functions small and focused
- Separate I/O from business logic
- Use simple data structures (dicts, lists, dataclasses)
- Write clear, readable code over clever code
- Extract abstractions only when you have 3+ concrete examples

### Docstrings (PEP 257)

Follow PEP 257 conventions for docstrings. Use docstrings to document public APIs and non-trivial behavior, but avoid redundant documentation for self-explanatory code.

#### When to write docstrings (required)

**Always add docstrings for:**
- **Public API surface**: Every public module, class, function, and method that is part of the project's public API
- **Module-level docstrings**: Brief explanation of module purpose; when applicable, list exported classes/exceptions/functions with one-line summaries
- **Stand-alone scripts**: Module docstring should serve as help/usage documentation (purpose, invocation, inputs/outputs, environment assumptions)
- **Non-trivial behavior**: Multi-line docstrings for functions with side effects, constraints, edge cases, exceptions, or invariants that aren't obvious from the signature

**Format requirements:**
- One-line docstrings: Triple quotes on same line, no blank lines before/after, closing quotes on same line
- Multi-line docstrings: Start with one-line summary, blank line, then detailed description
- First line should describe effect/action ("Return ...", "Compute ...", "Validate ..."), not describe the text itself
- Do not duplicate information available from function signature or type hints

#### When NOT to write docstrings

**Skip docstrings for:**
- **Internal helpers** (names starting with `_`): If code is trivial and self-explanatory, prefer clearer names and simpler structure instead
- **Signature restatements**: Do not write docstrings that merely repeat parameter names/types or return types (available via introspection)
- **Trivial wrappers**: Simple getters/setters/wrappers without logic don't need long docstrings; keep documentation proportional to complexity (follow KISS/YAGNI)

#### Default rule

**Write a docstring if:** A developer should understand the API without reading implementation details.

**Omit a docstring if:** The code is self-explanatory through clear naming, type hints, and simple structure.

### Documentation and library references

**Before generating code, always:**
1. Check `@docs` for library dependencies of the required versions (if available)
   - For `hishel <= 0.1.15`, check its documentation for API usage
   - For `httpx`, verify method signatures and best practices
   - For other dependencies, consult their official documentation
2. Use MCP server GitHub (if connection is available) to:
   - Search for examples in the library's repository
   - Check issue discussions for common patterns
   - Review recent changes and deprecations
   - Understand version-specific behaviors

This ensures code compatibility with the specified dependency versions and follows library best practices.

## Testing instructions

**Always use pytest for new tests.** Do not use `unittest` framework. The project uses pytest exclusively for its testing infrastructure, fixtures, and plugins (like `pytest-httpx`).

### Test structure

Tests are located in the `tests/` directory:
- `test_00_defaults.py` - Default configuration tests
- `test_01_client_methods_presence.py` - API method presence verification
- `test_02_cache.py` - Caching functionality tests
- `test_03_pagination.py` - Pagination handling tests

### Test fixtures

JSON fixtures are stored in `tests/fixtures/` and represent real API responses for:
- `carrier_result.json`
- `copyright_result.json`
- `nearest_settlement_result.json`
- `nearest_stations_result.json`
- `schedule_result.json`
- `search_result.json`
- `stations_list_result.json`
- `thread_result.json`

**Large fixtures (>10MB):**
- Do not commit fixtures larger than 10MB to the repository
- Store large fixtures in external storage (S3-compatible storage)
- When generating code, use default URL pattern: `https://<bucket_name>.s3.cloud.ru/<path_for_yarasp_fixtures>/`
- If developer provides a specific URL, use that instead of the default
- **Important:** If you use the default URL pattern, you MUST alert the developer that:
  - The URL must be replaced with the actual storage URL
  - The fixture file must be uploaded to the storage
  - The download must be verified to ensure the file is accessible and correct
- Tests that require large fixtures should not run by default (use pytest markers or skip by default)
- Document how to download/configure large fixtures for running those specific tests

### Running tests

```bash
# Quick test run
pytest -q

# Verbose output
pytest -v

# Run specific test
pytest tests/test_02_cache.py

# Run with coverage
coverage run --source yarasp -m pytest
coverage report -m
```

### Test requirements

- All tests must pass before merging
- Use `pytest-httpx` for HTTP request mocking
- Test both sync (`YaraspClient`) and async (`AsyncYaraspClient`) clients
- Verify cache behavior (responses from cache vs live requests)
- Test pagination for endpoints that support it
- Verify API key usage counter increments only for live requests

## Security considerations

Follow [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/) when implementing security-related features. Key areas to consider:

- **Input validation**: Validate and sanitize all inputs from external sources (API responses, environment variables, user parameters)
- **Output encoding**: Ensure proper encoding when handling data from external APIs
- **Error handling**: Don't expose sensitive information (API keys, internal paths) in error messages or logs
- **Authentication and session management**: Use environment variables for secrets, never hardcode credentials
- **Cryptographic practices**: When handling sensitive data, use appropriate encryption and secure storage
- **Data protection**: Exclude sensitive parameters (like API keys) from cache keys and logs
- **Communication security**: Use HTTPS for all API communications (enforced by httpx)
- **System configuration**: Ensure secure defaults (safe_mode enabled by default, appropriate file permissions for cache storage)

### API key handling

- **Never commit API keys** to version control
- API keys must be provided via environment variable `YARASP_API_KEY`
- The `apikey` parameter is automatically excluded from cache keys to prevent key leakage in cached responses
- API keys are not logged or exposed in error messages

### Environment variables

- `YARASP_API_KEY` (required) - API key for Yandex Schedule API
- `YARASP_API_DAILY_LIMIT` (optional, default: 500) - Daily request limit
- `YARASP_SAFE_MODE` (optional, default: 1) - Enable safe mode to prevent exceeding daily limits

### Safe mode

When `safe_mode=True` (default), the client will raise `RuntimeError` if the daily API limit is exceeded, preventing accidental overuse and potential API key suspension.

### Cache security

- Cache keys exclude the `apikey` parameter to prevent sensitive data in cache
- Custom key generator ensures API keys don't affect cache lookup
- Cache storage backends (FileStorage, SQLiteStorage, RedisStorage) should be configured with appropriate permissions

### Dependencies

- Keep dependencies up to date for security patches
- Use `uv.lock` to ensure reproducible builds with known-good dependency versions
- Review dependency changes before updating major versions

## Repository expectations (always)

- Follow existing project conventions (structure, naming, formatting)
- Do not introduce new production dependencies without an explicit request
- If behavior changes, update tests and docs
- Maintain backward compatibility with public API unless explicitly breaking changes are required
- Use type hints for all public functions and classes

## Definition of Done (verification)

Before considering a task complete:

- ✅ All tests pass: `pytest -q`
- ✅ Lint/format pass: `ruff check .` and `ruff format .`
- ✅ Type checking passes: `mypy .`
- ✅ Public API remains compatible unless the task explicitly says otherwise
- ✅ Documentation updated if behavior or API changed
- ✅ No new linter warnings or errors introduced
- ✅ Code follows KISS, YAGNI, SRP, SoC, and DRY principles
