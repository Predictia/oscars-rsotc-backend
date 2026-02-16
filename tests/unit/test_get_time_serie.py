import time

import numpy as np
import pandas as pd
import xarray as xr

from app.models.time_series_params import TimeseriesParams
from app.services.time_series import get_time_series


def test_get_time_serie():
    # Create a mock dataset
    times = pd.date_range("2000-01-01", "2024-12-31", freq="D")
    data = np.random.rand(len(times))
    ds = xr.Dataset(data_vars={"tas": (("time",), data)}, coords={"time": times})
    ds = ds.expand_dims(region=["Spain", "France"])

    start = time.perf_counter()
    # Define parameters
    params = TimeseriesParams(
        dataset="test_dataset",
        region_set="NUTS-0",
        region_name="Spain",
        variable="tas",
        resample_freq="MS",
        resample_func="mean",
        period="2010-2020",
        season_filter="01-12",
        season_filter_func="mean",
        anomaly=True,
        reference_period="2000-2005",
    )

    # Call the function
    get_time_series([ds], params)
    elapsed = time.perf_counter() - start
    print(f"Execution time: {elapsed:.3f} seconds")


def test_get_time_serie_derived_index():
    # Create a mock dataset
    times = pd.date_range("2000-01-01", "2024-12-31", freq="MS")
    time_filters = [
        "Annual",
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    tf_to_month = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }

    # Start with NaNs everywhere: (time, time_filter)
    data = np.full((len(times), len(time_filters)), np.nan, dtype=float)

    months = times.month  # 1..12

    # Annual: only fill January timestamps
    annual_col = time_filters.index("Annual")
    jan_mask = months == 1
    data[jan_mask, annual_col] = np.random.rand(jan_mask.sum())

    # Monthly filters: only fill their month timestamps
    for tf, month in tf_to_month.items():
        col = time_filters.index(tf)
        mask = months == month
        data[mask, col] = np.random.rand(mask.sum())

    ds = xr.Dataset(
        data_vars={"tx35": (("time", "time_filter"), data)},
        coords={"time": times, "time_filter": time_filters},
    ).expand_dims(region=["Spain", "France"])

    start = time.perf_counter()
    # Define parameters
    params = TimeseriesParams(
        dataset="test_dataset",
        region_set="NUTS-0",
        region_name="Spain",
        variable="tx35",
        resample_freq="MS",
        resample_func="mean",
        period="2010-2020",
        season_filter="01-12",
        season_filter_func="mean",
        anomaly=True,
        reference_period="2000-2005",
    )

    # Call the function
    get_time_series([ds], params)
    elapsed = time.perf_counter() - start
    print(f"Execution time: {elapsed:.3f} seconds")


def test_get_time_serie_multivariable():
    # Create a mock dataset with multiple variables
    times = pd.date_range("2000-01-01", "2024-12-31", freq="D")
    region_coords = {"region": ["Spain", "France"]}

    ds_tas = xr.Dataset(
        data_vars={"tas": (("region", "time"), np.random.rand(2, len(times)))},
        coords={"time": times, **region_coords},
    )
    ds_tasmin = xr.Dataset(
        data_vars={"tasmin": (("region", "time"), np.random.rand(2, len(times)))},
        coords={"time": times, **region_coords},
    )
    ds_tasmax = xr.Dataset(
        data_vars={"tasmax": (("region", "time"), np.random.rand(2, len(times)))},
        coords={"time": times, **region_coords},
    )

    start = time.perf_counter()
    # Define parameters
    params = TimeseriesParams(
        dataset="test_dataset",
        region_set="NUTS-0",
        region_name="Spain",
        variable="tas;tasmin;tasmax",
        resample_freq="MS",
        resample_func="mean",
        period="2010-2020",
        season_filter="01-12",
        season_filter_func="mean",
        anomaly=True,
        reference_period="2000-2005",
    )

    # Call the function with a list of datasets
    result = get_time_series([ds_tas, ds_tasmin, ds_tasmax], params)

    elapsed = time.perf_counter() - start
    print(f"Execution time: {elapsed:.3f} seconds")

    # Assertions
    assert "date" in result
    assert "value" in result
    assert "tas" in result["value"]
    assert "tasmin" in result["value"]
    assert "tasmax" in result["value"]
    assert len(result["date"]) == len(result["value"]["tas"])
