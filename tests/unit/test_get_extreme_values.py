import numpy as np
import pandas as pd
import xarray as xr

from app.models.extreme_values_params import ExtremeValuesParams
from app.services.extreme_values import get_extreme_values


def test_get_extreme_values():
    # Create a mock dataset
    times = pd.date_range("2000-01-01", "2024-12-31", freq="D")
    data = np.random.rand(len(times))
    ds = xr.Dataset(data_vars={"tas": (("time",), data)}, coords={"time": times})
    ds = ds.expand_dims(region=["ES", "FR"])

    # Define parameters
    params = ExtremeValuesParams(
        dataset="ERA5",
        region_set="NUTS-0",
        region_name="ES",
        variable="tas",
        period="2020-2020",
        season_filter="01-12",
    )

    # Call the function
    get_extreme_values([ds], params)


def test_get_extreme_values_derived_index():
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
    ).expand_dims(region=["ES", "FR"])

    # Define parameters
    params = ExtremeValuesParams(
        dataset="ERA5",
        region_set="NUTS-0",
        region_name="ES",
        variable="tx35",
        period="2020-2020",
        season_filter="01-12",
    )

    # Call the function
    get_extreme_values([ds], params)
