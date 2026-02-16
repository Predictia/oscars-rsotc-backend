from unittest.mock import patch

import xarray as xr

from app.load import get_datasets
from app.models.summary_stats_params import SummaryStatsParams


def test_get_dataset_multi_variables():
    """Test that _get_dataset correctly loads and merges multiple variables."""
    params = SummaryStatsParams(
        region_name="Spain", dataset="ERA5", region_set="NUTS-0"
    )

    # Mock mapping with two variables
    mock_mapping = {
        ("tas", "None", "ERA5", "NUTS-0"): {"local": "tas.zarr", "s3": "s3://tas.zarr"},
        ("pr", "None", "ERA5", "NUTS-0"): {"local": "pr.zarr", "s3": "s3://pr.zarr"},
    }

    # Mock opening local Zarr files
    def mock_open_zarr_local(path):
        if "tas" in path:
            return xr.Dataset({"tas": (("time",), [10, 11])}, coords={"time": [1, 2]})
        if "pr" in path:
            return xr.Dataset({"pr": (("time",), [100, 110])}, coords={"time": [1, 2]})
        return xr.Dataset()

    with patch("app.load._build_dataset_mapping", return_value=mock_mapping), patch(
        "app.load._open_zarr_local", side_effect=mock_open_zarr_local
    ):
        datasets = get_datasets(params)
        ds = xr.merge(datasets)

        # Check that both variables are present with their renamed combined names
        assert "tas_None" in ds.data_vars
        assert "pr_None" in ds.data_vars
        assert ds.tas_None.values.tolist() == [10, 11]
        assert ds.pr_None.values.tolist() == [100, 110]
        assert len(ds.data_vars) == 2


def test_get_dataset_single_variable():
    """
    Test that _get_dataset still works for a single variable.

    This ensures backward compatibility.
    """
    from app.models.time_series_params import TimeseriesParams

    params = TimeseriesParams(
        dataset="ERA5", region_set="NUTS-0", region_name="Spain", variable="tas_None"
    )

    mock_mapping = {
        ("tas", "None", "ERA5", "NUTS-0"): {"local": "tas.zarr", "s3": "s3://tas.zarr"},
    }

    with patch("app.load._build_dataset_mapping", return_value=mock_mapping), patch(
        "app.load._open_zarr_local",
        return_value=xr.Dataset({"tas": (("time",), [10])}, coords={"time": [1]}),
    ):
        datasets = get_datasets(params)
        ds = datasets[0]
        assert "tas_None" in ds.data_vars
        assert len(ds.data_vars) == 1


def test_get_dataset_semicolon_list():
    """Test that _get_dataset handles semicolon-separated lists."""
    from app.models.time_series_params import TimeseriesParams

    params = TimeseriesParams(
        dataset="ERA5",
        region_set="NUTS-0",
        region_name="Spain",
        variable="tas_None; pr_None ",
    )

    # Mock mapping with two variables
    mock_mapping = {
        ("tas", "None", "ERA5", "NUTS-0"): {"local": "tas.zarr", "s3": "s3://tas.zarr"},
        ("pr", "None", "ERA5", "NUTS-0"): {"local": "pr.zarr", "s3": "s3://pr.zarr"},
    }

    # Mock opening local Zarr files
    def mock_open_zarr_local(path):
        if "tas" in path:
            return xr.Dataset({"tas": (("time",), [10])}, coords={"time": [1]})
        if "pr" in path:
            return xr.Dataset({"pr": (("time",), [100])}, coords={"time": [1]})
        return xr.Dataset()

    with patch("app.load._build_dataset_mapping", return_value=mock_mapping), patch(
        "app.load._open_zarr_local", side_effect=mock_open_zarr_local
    ):
        datasets = get_datasets(params)
        ds = xr.merge(datasets)
        assert "tas_None" in ds.data_vars
        assert "pr_None" in ds.data_vars
        assert len(ds.data_vars) == 2
