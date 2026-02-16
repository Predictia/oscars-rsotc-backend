from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import xarray as xr

from app.load import get_datasets


def test_sfcWind_transformation():
    # Create a dummy dataset with sfcWind in m/s
    data = np.array([10.0, 20.0, 30.0])
    ds = xr.Dataset(
        {"sfcWind": (["time"], data, {"units": "m/s"})}, coords={"time": [1, 2, 3]}
    )

    # Mock _build_dataset_mapping to return a path for sfcWind_None
    mock_mapping = {
        ("sfcWind", "None", "dataset", "region_set"): {
            "local": "mock_path",
            "s3": "s3://mock_path",
        }
    }

    # Mock _open_zarr_local to return our dummy dataset
    with patch("app.load._build_dataset_mapping", return_value=mock_mapping):
        with patch("app.load._open_zarr_local", return_value=ds):
            params = SimpleNamespace(
                variable="sfcWind_None", dataset="dataset", region_set="region_set"
            )

            loaded_ds_list = get_datasets(params)
            loaded_ds = loaded_ds_list[0]

            # Check if renamed correctly
            assert "sfcWind_None" in loaded_ds.data_vars

            # Check if values are multiplied by 3.6
            expected_data = data * 3.6
            np.testing.assert_allclose(loaded_ds["sfcWind_None"].values, expected_data)

            # Check if units are updated
            assert loaded_ds["sfcWind_None"].attrs["units"] == "km/h"


def test_other_variable_no_transformation():
    # Create a dummy dataset with another variable
    data = np.array([10.0, 20.0, 30.0])
    ds = xr.Dataset(
        {"tas": (["time"], data, {"units": "K"})}, coords={"time": [1, 2, 3]}
    )

    # Mock _build_dataset_mapping
    mock_mapping = {
        ("tas", "None", "dataset", "region_set"): {
            "local": "mock_path",
            "s3": "s3://mock_path",
        }
    }

    with patch("app.load._build_dataset_mapping", return_value=mock_mapping):
        with patch("app.load._open_zarr_local", return_value=ds):
            params = SimpleNamespace(
                variable="tas_None", dataset="dataset", region_set="region_set"
            )

            loaded_ds_list = get_datasets(params)
            loaded_ds = loaded_ds_list[0]

            # Check if renamed correctly
            assert "tas_None" in loaded_ds.data_vars

            # Check if values are NOT changed
            np.testing.assert_allclose(loaded_ds["tas_None"].values, data)

            # Check if units are NOT updated
            assert loaded_ds["tas_None"].attrs["units"] == "K"


if __name__ == "__main__":
    try:
        test_sfcWind_transformation()
        print("sfcWind transformation test PASSED")
        test_other_variable_no_transformation()
        print("Other variable test PASSED")
    except Exception as e:
        print(f"Test FAILED: {e}")
        exit(1)
