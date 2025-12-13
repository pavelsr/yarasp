#!/usr/bin/env python3
"""
Script for generating test fixtures from Yandex Schedule API.

This script fetches data from various Yandex Schedule API endpoints and saves
the responses as JSON fixture files for use in tests.

Example usage:
    # Basic usage (requires YARASP_API_KEY environment variable)
    python scripts/gen_fixtures.py

    # Force rewrite existing fixtures
    python scripts/gen_fixtures.py --force-rewrite

    # Generate mock code for httpx_mock
    python scripts/gen_fixtures.py --gen-mock

    # If YARASP_API_KEY is not set, the script will prompt for it
    python scripts/gen_fixtures.py
"""

# If you get "httpx.ReadTimeout: The read operation timed out" error try to set HTTPX_TIMEOUT=30 env variable and enable/disable VPN.
# Yandex API works best from Russian IP addresses

import os
os.environ["HTTPX_TIMEOUT"] = "30.0"

# import httpx
# class CustomClient(httpx.Client):
#     def __init__(self, *args, **kwargs):
#         kwargs["timeout"] = httpx.Timeout(60.0)
#         super().__init__(*args, **kwargs)
# httpx.Client = CustomClient

import json
import logging
import argparse
from pathlib import Path
import hishel
from yarasp import YaraspClient

logging.basicConfig(level=logging.INFO)

# Default cache directory used by hishel FileStorage
DEFAULT_CACHE_DIR = "tests/.cache/hishel"

def count_cache_files(cache_dir=DEFAULT_CACHE_DIR):
    """Count the number of cache files in the cache directory."""
    if not os.path.exists(cache_dir):
        return 0
    cache_path = Path(cache_dir)
    # Count all files recursively in the cache directory
    return len(list(cache_path.rglob("*")))

def fetch_and_save(client, endpoint, params=None, base_fixtures_path="tests/fixtures", force_rewrite=False, show_mock=True):
    """Fetch data from API endpoint and save as fixture file."""
    fixture_file = f"{base_fixtures_path}/{endpoint}_result.json"
    
    params = client._prepare_params(params)
    del params['apikey']
    from urllib.parse import urlencode
    query_string = urlencode(params, doseq=True)
    api_endpoint = client._build_url(endpoint)
    full_url = f"{api_endpoint}?{query_string}"
    
    if os.path.exists(fixture_file) and not force_rewrite:
        logging.info(f"ℹ️ Fixture for {endpoint} already exists: {fixture_file}. Source: {full_url}")
    else:
        result = client.get(endpoint, params=params)
        with open(fixture_file, "w") as file:
            json.dump(result, file, indent=4)
        logging.info(f"✓ Saved fixture for {endpoint}: {fixture_file}")

    return (api_endpoint, fixture_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate fixtures for API methods")
    parser.add_argument("--force-rewrite", action="store_true", help="Overwrite existing fixtures")
    parser.add_argument("--gen-mock", action="store_true", help="Generate and output mock code for httpx_mock to console")
    args = parser.parse_args()
    
    # Check if YARASP_API_KEY is set, if not, prompt for it
    api_key = os.environ.get("YARASP_API_KEY")
    if not api_key:
        logging.warning("YARASP_API_KEY environment variable is not set.")
        api_key = input("Please enter your Yandex Schedule API key: ").strip()
        if api_key:
            os.environ["YARASP_API_KEY"] = api_key
            logging.info("API key set from console input")
        else:
            logging.error("API key is required. Exiting.")
            exit(1)
    
    # Create directory if it doesn't exist
    base_fixtures_path = "tests/fixtures"
    os.makedirs(base_fixtures_path, exist_ok=True)

    # Create client with explicit cache storage and set API key explicitly (since api_key has init=False in dataclass)
    client = YaraspClient(cache_storage=hishel.FileStorage(base_path="tests/.cache/hishel"))
    client.api_key = api_key

    requests = [
        # Schedule between stations
        # https://yandex.ru/dev/rasp/doc/ru/reference/schedule-point-point
        # Example: schedule from Pulkovo to Sheremetyevo
        {"endpoint": "search", "params": {"from": "s9600366", "to": "s9600213", "limit": 3, "transport_types": "plane"}},

        # Schedule by station
        # https://yandex.ru/dev/rasp/doc/ru/reference/schedule-on-station
        # Example: departure schedule from Pulkovo airport
        {"endpoint": "schedule", "params": {"station": "s9600366"}},

        # List of stations on route (*)
        # https://yandex.ru/dev/rasp/doc/ru/reference/list-stations-route
        # Original example {"endpoint": "thread", "params": {"uid": "038AA_tis"}} no longer exists
        # 741У "Aurora" SPb -> Moscow # {"endpoint": "thread", "params": {"uid": "741U_0_2"}},
        # You can also try _0_2, _1_2, _2_2, _3_2
        # 723Р "Lastochka" SPb -> Moscow
        {"endpoint": "thread", "params": {"uid": "723R_0_2"}},

        # List of nearest stations
        # Example: 50.440046, 40.4882367 - point in Voronezh region, nearest city - Pavlovsk
        # https://yandex.ru/dev/rasp/doc/ru/reference/query-nearest-station
        {"endpoint": "nearest_stations", "params": {"lat": "50.440046", "lng": "40.4882367", "distance": 50}},

        # Nearest city
        # https://yandex.ru/dev/rasp/doc/ru/reference/nearest-settlement
        # Example: 50.440046, 40.4882367 - point in Voronezh region, nearest city - Pavlovsk
        # Value: The distance attribute in the response returns straight-line distance
        {"endpoint": "nearest_settlement", "params": {"lat": "50.440046", "lng": "40.4882367", "distance": 50}},

        # Carrier information (*)
        # https://yandex.ru/dev/rasp/doc/ru/reference/query-carrier
        # Example: Aeroflot
        {"endpoint": "carrier", "params": {"code": "SU", "system": "iata"}},

        # List of all available stations
        # https://yandex.ru/dev/rasp/doc/ru/reference/stations-list
        # Returns JSON of fairly large volume, more than 100MB
        {"endpoint": "stations_list", "params": {}},
        
        # Yandex Schedule copyright
        # https://yandex.ru/dev/rasp/doc/ru/reference/query-copyright
        # Value: various logos in frame
        {"endpoint": "copyright", "params": {}}
    ]

    if args.gen_mock:
        mock_code = []
    
    # Get cache directory from client if available
    cache_dir = DEFAULT_CACHE_DIR
    if hasattr(client, 'cache_storage') and client.cache_storage:
        # Try to get the actual cache directory from hishel FileStorage
        if hasattr(client.cache_storage, 'base_path'):
            cache_dir = str(client.cache_storage.base_path)
        elif hasattr(client.cache_storage, '_base_path'):
            cache_dir = str(client.cache_storage._base_path)
    
    for request in requests:
        endpoint = request["endpoint"]
        # Count cache files before request
        cache_count_before = count_cache_files(cache_dir)
        
        (full_url, fixture_file) = fetch_and_save(client, endpoint, params=request["params"], force_rewrite=args.force_rewrite)
        
        # Count cache files after request
        cache_count_after = count_cache_files(cache_dir)
        cache_files_generated = cache_count_after - cache_count_before
        
        if cache_files_generated > 0:
            logging.info(f"Generated {cache_files_generated} cache file(s) for {endpoint} request")
        elif cache_count_after > 0:
            logging.info(f"Using existing cache for {endpoint} request (total cache files: {cache_count_after})")
        
        if args.gen_mock:
            mock_code.append(f"httpx_mock.add_response(url=\"{full_url}\", json=load_mock_json(\"{fixture_file}\"))")
        
    if args.gen_mock:
        print("\n")
        print("## API mock code: ")
        print("\n".join(mock_code))
