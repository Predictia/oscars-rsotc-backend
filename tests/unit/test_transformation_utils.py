import numpy as np
import pytest
import xarray as xr

from app.utils.transformation import ensure_float, transform_units


def test_transform_units_dataset():
    """Test unit transformation for sfcWind in a Dataset."""
    data = np.array([10.0, 20.0, 30.0])
    ds = xr.Dataset(
        {"sfcWind": (["time"], data, {"units": "m/s"}), "tas": (["time"], data)},
        coords={"time": [1, 2, 3]},
    )

    transformed = transform_units(ds)

    # Check sfcWind
    np.testing.assert_allclose(transformed["sfcWind"].values, data * 3.6)
    assert transformed["sfcWind"].attrs["units"] == "km/h"

    # Check tas (should be unchanged)
    np.testing.assert_allclose(transformed["tas"].values, data)


def test_ensure_float_timedelta_dataset():
    """Test conversion from timedelta to float days in a Dataset."""
    one_day_ns = np.timedelta64(1, "D")
    values_days = np.array([5, 10, 15])
    values_ns = values_days * one_day_ns

    ds = xr.Dataset(
        {"fd": (["time"], values_ns), "tas": (["time"], [10.5, 11.0, 11.5])},
        coords={"time": [1, 2, 3]},
    )

    processed = ensure_float(ds)

    # Check fd
    np.testing.assert_allclose(processed["fd"].values, values_days)
    assert processed["fd"].dtype == float

    # Check tas
    assert processed["tas"].dtype == float

