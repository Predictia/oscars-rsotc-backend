import numpy as np
import pandas as pd
import xarray as xr

from app.utils.time_filtering import TemporalFiltering


def test_sel_time_filter_basic():
    """
    Test basic time filtering for a specific period and season.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    times = pd.date_range("2000-01-01", "2002-12-31", freq="D")
    data = np.random.rand(len(times))
    ds = xr.Dataset({"tas": (("time",), data)}, coords={"time": times})

    # Filter for 2001, JAN to MAR
    tf = TemporalFiltering(dataset=ds, period_range="2001-2001", time_filter="01-03")
    filtered = tf.sel_time_filter()

    assert (filtered.time.dt.year == 2001).all()
    assert filtered.time.dt.month.min() == 1
    assert filtered.time.dt.month.max() == 3
    # 2001 is not a leap year. Jan(31) + Feb(28) + Mar(31) = 90
    assert len(filtered.time) == 90


def test_sel_time_filter_all_period():
    """
    Test time filtering when period_range is set to 'all'.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    times = pd.date_range("2000-01-01", "2001-12-31", freq="D")
    data = np.random.rand(len(times))
    ds = xr.Dataset({"tas": (("time",), data)}, coords={"time": times})

    tf = TemporalFiltering(dataset=ds, period_range="all", time_filter="01-01")
    filtered = tf.sel_time_filter()

    assert len(filtered.time) == 31 + 31  # Jan 2000 + Jan 2001
    assert (filtered.time.dt.month == 1).all()


def test_sel_time_filter_cross_year():
    """
    Test time filtering for seasons that cross the calendar year boundary (e.g., DJF).

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    times = pd.date_range("2000-01-01", "2002-12-31", freq="D")
    data = np.random.rand(len(times))
    ds = xr.Dataset({"tas": (("time",), data)}, coords={"time": times})

    # Filter for Dec to Feb (12-02) for year 2001
    # This should take Dec 2000 to Feb 2001
    tf = TemporalFiltering(dataset=ds, period_range="2001-2001", time_filter="12-02")
    filtered = tf.sel_time_filter()

    # Dec 2000 + Jan 2001 + Feb 2001
    # 31 + 31 + 28 = 90
    assert len(filtered.time) == 90
    assert filtered.time.min().values == np.datetime64("2000-12-01")
    assert filtered.time.max().values == np.datetime64("2001-02-28")


def test_compute_climatology():
    """
    Test the compute method which returns filtered and yearly aggregated data.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    times = pd.date_range("2000-01-01", "2002-12-31", freq="D")
    data = np.ones(len(times))
    ds = xr.Dataset({"tas": (("time",), data)}, coords={"time": times})

    tf = TemporalFiltering(
        dataset=ds, period_range="2000-2002", time_filter="01-12", statistical="sum"
    )
    data_for_period, yearly_data = tf.compute()

    # data_for_period should be all days
    assert len(data_for_period.time) == len(times)

    # yearly_data should be 3 points (2000, 2001, 2002)
    assert len(yearly_data.time) == 3
    # Sum for 2000 (leap year) = 366
    # Sum for 2001 = 365
    # Sum for 2002 = 365
    # The compute method does a mean of the resampled values in line 137
    # Resample(YS-JAN).reduce(sum) gives [366, 365, 365]
    # Resample(YS).reduce(mean) on those same timestamps gives [366, 365, 365]
    np.testing.assert_array_equal(yearly_data.tas.values, [366, 365, 365])
