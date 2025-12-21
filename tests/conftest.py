import os
import sys
import warnings
from pathlib import Path
import httpx
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
STATIONS_LIST_FIXTURE = FIXTURES_DIR / "stations_list_result.json"
STATIONS_LIST_S3_URL = "https://tierf15-pub.s3.cloud.ru/fixtures/stations_list_result.json"


def pytest_addoption(parser):
    """Adds command line option --large-fixtures to run tests with large fixtures."""
    parser.addoption(
        "--large-fixtures",
        action="store_true",
        default=False,
        help="Run tests that require large fixtures (e.g. stations_list_result.json)"
    )


def pytest_configure(config):
    """Registers marker for tests with large fixtures."""
    config.addinivalue_line(
        "markers", "large_fixture: marks tests that require large fixtures (deselect with '-m \"not large_fixture\"')"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically skips tests with large_fixture marker if --large-fixtures option is not specified."""
    if not config.getoption("--large-fixtures", default=False):
        skip_large_fixture = pytest.mark.skip(reason="Requires --large-fixtures option to run")
        for item in items:
            if "large_fixture" in item.keywords:
                item.add_marker(skip_large_fixture)
    
    # For test_07_sqlite.py: by default run only stations_list, schedule, carrier tests
    # unless all_endpoints or all marker is explicitly requested
    markerexpr = config.getoption("-m", default=None)
    request_all_endpoints = markerexpr and ("all_endpoints" in markerexpr or markerexpr == "all")
    
    if not request_all_endpoints:
        # Filter test_07_sqlite tests to run only default ones by default
        for item in items:
            # Check if this is a test from test_07_sqlite.py
            # Use nodeid which contains the full path like "tests/test_07_sqlite.py::test_name"
            if hasattr(item, 'nodeid') and "test_07_sqlite" in item.nodeid:
                # Skip tests that have all_endpoints/all marker but not stations_list/schedule/carrier
                has_all_marker = "all_endpoints" in item.keywords or "all" in item.keywords
                has_default_marker = (
                    "stations_list" in item.keywords
                    or "schedule" in item.keywords
                    or "carrier" in item.keywords
                )
                # If test has all_endpoints/all marker but no default marker, skip it
                if has_all_marker and not has_default_marker:
                    item.add_marker(
                        pytest.mark.skip(
                            reason="Run with -m all_endpoints or -m all to test all endpoints"
                        )
                    )


def ensure_stations_list_fixture():
    """
    Checks for stations_list_result.json and downloads it from S3 if necessary.
    
    Returns:
        bool: True if file is available, False if file is unavailable
    """
    if STATIONS_LIST_FIXTURE.exists():
        return True
    
    # Try to download file from S3
    try:
        print(f"Downloading {STATIONS_LIST_FIXTURE.name} from S3...", file=sys.stderr)
        with httpx.Client(timeout=300.0) as client:
            response = client.get(STATIONS_LIST_S3_URL)
            response.raise_for_status()
            
            # Create directory if it doesn't exist
            FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
            
            # Save file
            with open(STATIONS_LIST_FIXTURE, 'wb') as f:
                f.write(response.content)
            
            print(f"Successfully downloaded {STATIONS_LIST_FIXTURE.name}", file=sys.stderr)
            return True
    except Exception as e:
        print(f"\nWARNING: Could not download {STATIONS_LIST_FIXTURE.name} from S3: {e}", file=sys.stderr)
        print(f"WARNING: Tests requiring this fixture will be skipped.\n", file=sys.stderr)
        warnings.warn(
            f"Could not download {STATIONS_LIST_FIXTURE.name} from S3: {e}. "
            f"Tests requiring this fixture will be skipped.",
            UserWarning
        )
        return False


@pytest.fixture(scope="session")
def stations_list_fixture_available(request):
    """
    Pytest fixture for checking availability of stations_list_result.json.
    
    When running with --large-fixtures option, attempts to download file if it doesn't exist.
    """
    if request.config.getoption("--large-fixtures", default=False):
        return ensure_stations_list_fixture()
    return False

