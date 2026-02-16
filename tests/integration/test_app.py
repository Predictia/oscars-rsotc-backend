import time

from starlette.testclient import TestClient

from app.app import app

client = TestClient(app)


def test_debug_routes():
    print("--- Registered Routes ---")
    for route in app.routes:
        methods = getattr(route, "methods", "N/A")
        print(f"Route: {route.path}, Methods: {methods}")
    print("--- End of Routes ---")


def test_time_series_endpoint():
    test_params = {
        "dataset": "ERA5",
        "variable": "tas",
        "pressure_level": "None",
        "region_set": "NUTS-0",
        "region_name": "ES",
        "period": "1981-2020",
        "anomaly": "True",
        "reference_period": "1991-2010",
    }

    start = time.perf_counter()
    response = client.post("/api/time_series", json=test_params)
    elapsed = time.perf_counter() - start

    print("Status:", response.status_code)
    print("Body:", response.json())
    print(f"Execution time: {elapsed:.3f} seconds")

    assert response.status_code == 200


def test_climatology_map_endpoint():
    test_params = {
        "dataset": "ERA5",
        "region_set": "NUTS-1",
        "region_name": "NL4;BE2;BE1;NL3;NL2",
        "variable": "tas",
        "pressure_level": "None",
        "period": "1981-2010",
        "season_filter": "01-12",
        "season_filter_func": "mean",
    }

    start = time.perf_counter()
    response = client.post("/api/climatology_map", json=test_params)
    elapsed = time.perf_counter() - start

    print("Status:", response.status_code)
    print("Body:", response.json())
    print(f"Execution time: {elapsed:.3f} seconds")

    assert response.status_code == 200


def test_annual_cycle_endpoint():
    test_params = {
        "dataset": "ERA5",
        "variable": "tas",
        "pressure_level": "None",
        "region_set": "NUTS-0",
        "region_name": "ES",
        "period": "2024-2024",
        "reference_period": "1940-2023",
    }

    start = time.perf_counter()
    response = client.post("/api/annual_cycle", json=test_params)
    elapsed = time.perf_counter() - start

    print("Status:", response.status_code)
    print("Body:", response.json())
    print(f"Execution time: {elapsed:.3f} seconds")

    assert response.status_code == 200


def test_extreme_values_endpoint():
    test_params = {
        "dataset": "ERA5",
        "variable": "tas",
        "pressure_level": "None",
        "region_set": "NUTS-0",
        "region_name": "ES",
        "period": "2024-2024",
        "season_filter": "01-12",
    }

    start = time.perf_counter()
    response = client.post("/api/extreme_values", json=test_params)
    elapsed = time.perf_counter() - start

    print("Status:", response.status_code)
    print("Body:", response.json())
    print(f"Execution time: {elapsed:.3f} seconds")

    assert response.status_code == 200


def test_histograms_endpoint():
    test_params = {
        "dataset": "ERA5",
        "variable": "tas",
        "pressure_level": "None",
        "region_set": "NUTS-0",
        "region_name": "ES",
        "period": "1991-2020",
        "reference_period": "1950-1980",
        "season_filter": "08-08",
    }

    start = time.perf_counter()
    response = client.post("/api/histograms", json=test_params)
    elapsed = time.perf_counter() - start

    print("Status:", response.status_code)
    print("Body:", response.json())
    print(f"Execution time: {elapsed:.3f} seconds")

    assert response.status_code == 200
