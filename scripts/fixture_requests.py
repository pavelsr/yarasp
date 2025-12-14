"""
Test fixture request parameters.

This module contains the request parameters used for generating test fixtures.
These parameters are shared between gen_fixtures.py script and test_02_cache.py
to ensure consistency.
"""

# Schedule between stations
# https://yandex.ru/dev/rasp/doc/ru/reference/schedule-point-point
# Example: schedule from Pulkovo to Sheremetyevo
SEARCH_REQUEST = {"endpoint": "search", "params": {"from": "s9600366", "to": "s9600213", "limit": 3, "transport_types": "plane"}}

# Schedule by station
# https://yandex.ru/dev/rasp/doc/ru/reference/schedule-on-station
# Example: departure schedule from Pulkovo airport
SCHEDULE_REQUEST = {"endpoint": "schedule", "params": {"station": "s9600366"}}

# List of stations on route
# https://yandex.ru/dev/rasp/doc/ru/reference/list-stations-route
# 723Р "Lastochka" SPb -> Moscow
THREAD_REQUEST = {"endpoint": "thread", "params": {"uid": "723R_0_2"}}

# List of nearest stations
# Example: 50.440046, 40.4882367 - point in Voronezh region, nearest city - Pavlovsk
# https://yandex.ru/dev/rasp/doc/ru/reference/query-nearest-station
NEAREST_STATIONS_REQUEST = {"endpoint": "nearest_stations", "params": {"lat": "50.440046", "lng": "40.4882367", "distance": 50}}

# Nearest city
# https://yandex.ru/dev/rasp/doc/ru/reference/nearest-settlement
# Example: 50.440046, 40.4882367 - point in Voronezh region, nearest city - Pavlovsk
# Value: The distance attribute in the response returns straight-line distance
NEAREST_SETTLEMENT_REQUEST = {"endpoint": "nearest_settlement", "params": {"lat": "50.440046", "lng": "40.4882367", "distance": 50}}

# Carrier information
# https://yandex.ru/dev/rasp/doc/ru/reference/query-carrier
# Example: Aeroflot
CARRIER_REQUEST = {"endpoint": "carrier", "params": {"code": "SU", "system": "iata"}}

# List of all available stations
# https://yandex.ru/dev/rasp/doc/ru/reference/stations-list
# Returns JSON of fairly large volume, more than 100MB
STATIONS_LIST_REQUEST = {"endpoint": "stations_list", "params": {}}

# Yandex Schedule copyright
# https://yandex.ru/dev/rasp/doc/ru/reference/query-copyright
# Value: various logos in frame
COPYRIGHT_REQUEST = {"endpoint": "copyright", "params": {}}

# All requests in a list (for iteration)
REQUESTS = [
    SEARCH_REQUEST,
    SCHEDULE_REQUEST,
    THREAD_REQUEST,
    NEAREST_STATIONS_REQUEST,
    NEAREST_SETTLEMENT_REQUEST,
    CARRIER_REQUEST,
    STATIONS_LIST_REQUEST,
    COPYRIGHT_REQUEST,
]

