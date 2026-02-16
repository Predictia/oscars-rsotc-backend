import numpy as np
import pandas as pd
import pytest
import xarray as xr

from app.utils.dataset_helpers import (
    filter_by_period,
    get_single_dataset,
    handle_precomputed_time_filter,
)


def test_get_single_dataset():
    """
    Test that get_single_dataset returns the first element or raises ValueError.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    ds1 = xr.Dataset({"a": 1})
    ds2 = xr.Dataset({"b": 2})

    assert get_single_dataset([ds1]) == ds1

    with pytest.raises(ValueError, match="Multiple datasets not supported"):
        get_single_dataset([ds1, ds2])


def test_handle_precomputed_time_filter():
    """
    Test selecting a precomputed time filter from a DataArray.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    times = pd.date_range("2000-01-01", periods=3, freq="D")
    data = np.array([[1, 2, 3], [4, 5, 6]])  # (time_filter, time)
    da = xr.DataArray(
        data,
        coords={"time_filter": ["Annual", "DJF"], "time": times},
        dims=["time_filter", "time"],
        name="test_var",
    )

    # Test valid filter
    result = handle_precomputed_time_filter(da, "01-12", "test_var")  # mapped to Annual
    assert (result.values == [1, 2, 3]).all()

    # Test fallback to Annual
    result_fallback = handle_precomputed_time_filter(
        da, "06-08", "test_var"
    )  # mapped to JJA, not in coords
    assert (result_fallback.values == [1, 2, 3]).all()


def test_filter_by_period():
    """
    Test filtering a DataArray by a period string.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    times = pd.date_range("2000-01-01", "2010-12-31", freq="YS")
    da = xr.DataArray(np.arange(len(times)), coords={"time": times}, dims=["time"])

    # Test specific period
    filtered = filter_by_period(da, "2002-2005")
    assert filtered.time.dt.year.min() == 2002
    assert filtered.time.dt.year.max() == 2005
    assert len(filtered) == 4

    # Test 'all'
    all_da = filter_by_period(da, "all")
    assert len(all_da) == len(da)
    assert (all_da.values == da.values).all()
