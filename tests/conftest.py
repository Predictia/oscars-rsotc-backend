from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
import xarray as xr


@pytest.fixture(autouse=True)
def mock_app_load():
    mock_mapping = {
        ("tas", "None", "ERA5", "NUTS-0"): {
            "local": "/data/tas_None_ERA5_NUTS-0.zarr",
            "s3": "s3://bucket/tas_None_ERA5_NUTS-0.zarr",
        },
        ("tas", "None", "ERA5", "NUTS-1"): {
            "local": "/data/tas_None_ERA5_NUTS-1.zarr",
            "s3": "s3://bucket/tas_None_ERA5_NUTS-1.zarr",
        },
        ("pr", "None", "ERA5", "NUTS-0"): {
            "local": "/data/pr_None_ERA5_NUTS-0.zarr",
            "s3": "s3://bucket/pr_None_ERA5_NUTS-0.zarr",
        },
        ("fd", "None", "ERA5", "NUTS-0"): {
            "local": "/data/fd_None_ERA5_NUTS-0.zarr",
            "s3": "s3://bucket/fd_None_ERA5_NUTS-0.zarr",
        },
    }

    def mock_open_zarr(path, *args, **kwargs):
        # Create a dummy dataset that has multiple regions if needed
        # Use a large enough time range to satisfy period filters in tests
        # (e.g. 1981-2020)
        times = pd.date_range("1940-01-01", "2025-01-01", freq="MS")
        regions = ["ES", "FR", "NL4", "BE2", "BE1", "NL3", "NL2", "ES130", "Spain"]

        # Determine variable name from path or URI
        varname = "tas"
        if "pr" in path:
            varname = "pr"
        if "fd" in path:
            varname = "fd"

        data = np.random.rand(len(times), len(regions))
        ds = xr.Dataset(
            data_vars={varname: (("time", "region"), data)},
            coords={"time": times, "region": regions},
        )
        return ds

    with patch("app.load._build_dataset_mapping", return_value=mock_mapping), patch(
        "app.load._open_zarr_local", side_effect=mock_open_zarr
    ), patch("app.load._open_zarr_s3", side_effect=mock_open_zarr):
        yield
