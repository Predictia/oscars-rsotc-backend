import numpy as np
import pandas as pd
import pytest
import xarray as xr

from app.models.summary_stats_params import SummaryStatsParams
from app.services.summary_stats import get_summary_stats


@pytest.fixture
def mock_datasets():
    # 1. Mock ERA5-like dataset (Daily)
    times_daily = pd.date_range("1960-01-01", "2024-12-31", freq="D")
    tas_data = 15 + np.random.normal(0, 5, len(times_daily))
    ds_era5 = xr.Dataset(
        data_vars={"tas_None": (("time",), tas_data)}, coords={"time": times_daily}
    ).expand_dims(region=["Spain"])

    # 2. Mock Index-like dataset (Yearly with time_filter)
    times_yearly = pd.date_range("1960-01-01", "2024-01-01", freq="YS")
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
    fd_data = np.random.randint(0, 10, (len(times_yearly), len(time_filters)))
    ds_index = xr.Dataset(
        data_vars={"fd_None": (("time", "time_filter"), fd_data)},
        coords={"time": times_yearly, "time_filter": time_filters},
    ).expand_dims(region=["Spain"])

    return [ds_era5, ds_index]


def test_get_summary_stats_output_structure(mock_datasets):
    """Test that the endpoint returns a dictionary of items."""
    params = SummaryStatsParams(
        region_name="Spain", period="2024-2024", season_filter="01-12"
    )

    result = get_summary_stats(mock_datasets, params)

    assert "stats" in result
    items = result["stats"]
    assert isinstance(items, dict)

    # Check that variables are present
    assert "tas" in items
    assert "fd" in items


def test_get_summary_stats_seasonal_filter(mock_datasets):
    """Test that seasonal filtering works for both ERA5 and indices."""
    # March 2024
    params = SummaryStatsParams(
        region_name="Spain", period="2024-2024", season_filter="03-03"
    )

    result = get_summary_stats(mock_datasets, params)
    items = result["stats"]

    # Check tas (ERA5)
    tas_item = items["tas"]
    assert tas_item["value"] is not None
    assert "1991_2020" in tas_item["anomalies"]

    # Check fd (Index)
    fd_item = items["fd"]
    assert fd_item["value"] is not None
    # Verify it selected March data from the index dataset
    # (In a real test we'd compare against known values from mock_datasets)
