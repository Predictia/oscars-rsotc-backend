import numpy as np
import pandas as pd
import xarray as xr

from app.models.summary_stats_params import SummaryStatsParams
from app.models.time_series_params import TimeseriesParams
from app.services.summary_stats import get_summary_stats
from app.services.time_series import get_time_series


def test_summary_stats_timedelta_serialization():
    """Test that variables with timedelta64 dtype are converted to float days."""
    # Create a mock dataset with a timedelta variable
    times = pd.date_range("2024-01-01", "2024-12-31", freq="D")
    # create dummy data, just zeros, but cast to timedelta for 'fd'
    # logic simulation if needed,
    # or actually more accurately: the issue usually happens when we have
    # counts that result in timedelta.
    # But usually 'days' variables in NetCDF are just floats.
    # The user says "dataset": "ERA5", "variable": "fd".
    # In the code, 'fd' seems to come from a dataset.
    # If the source data is already timedelta64[ns], we want to ensure
    # it gets converted.

    # Let's mock 'fd' as timedelta64[ns].
    # One day is 86400 * 1e9 ns
    one_day_ns = np.timedelta64(1, "D")

    # Create random data: 5 days, 10 days, etc.
    values_days = np.array([5, 10, 15] * (len(times) // 3) + [5] * (len(times) % 3))
    values_ns = values_days * one_day_ns

    # The service expects specific variable names logic.
    # 'fd' maps to internal_var 'fd_None' in the service map if we look at `var_info`.
    # "fd_None": ("fd", "days", "frost days")

    ds = xr.Dataset(
        data_vars={"fd_None": (("time",), values_ns)}, coords={"time": times}
    ).expand_dims(region=["ES130"])

    params = SummaryStatsParams(
        dataset="ERA5",
        region_set="NUTS-3",
        region_name="ES130",
        period="2024-2024",
        season_filter="01-12",
    )

    result = get_summary_stats(ds, params)

    stats = result["stats"]
    fd_stat = stats["fd"]

    print(f"FD Value: {fd_stat['value']}")

    # We expect the value to be in days (around 5-15), not huge integer (nanoseconds)
    # 5 days in ns is ~4.32e14
    assert (
        fd_stat["value"] < 1000
    ), f"Value {fd_stat['value']} is too large, likely nanoseconds"
    assert fd_stat["value"] > 0


def test_time_series_timedelta_serialization():
    """
    Test time series conversion from timedelta64.

    Ensure variables with timedelta64 dtype are converted to float days.
    """
    times = pd.date_range("2024-01-01", "2024-01-10", freq="D")
    one_day_ns = np.timedelta64(1, "D")
    values_days = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    values_ns = values_days * one_day_ns

    ds = xr.Dataset(
        data_vars={"fd_None": (("time",), values_ns)}, coords={"time": times}
    ).expand_dims(region=["ES130"])

    params = TimeseriesParams(
        dataset="ERA5",
        region_set="NUTS-3",
        region_name="ES130",
        variable="fd",
        period="2024-2024",
        season_filter="01-12",
    )

    result = get_time_series([ds], params)

    # Check the first value
    first_val = result["value"]["fd_None"][0]
    print(f"First TS Value: {first_val}")

    assert first_val < 100, f"Value {first_val} is too large, likely nanoseconds"
    assert first_val == 5.5
