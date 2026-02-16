import numpy as np
import pandas as pd
import xarray as xr

from app.models.climatology_map_params import ClimatologyMapParams
from app.services.climatology_map import get_climatology_map


def test_get_climatology_map():
    # Create a mock dataset with more than one time point for reference
    times = pd.date_range("1990-01-01", "2024-12-31", freq="D")
    data = np.random.rand(len(times))
    ds = xr.Dataset(data_vars={"tas": (("time",), data)}, coords={"time": times})
    ds = ds.expand_dims(region=["Spain", "France"])

    # Define parameters
    params = ClimatologyMapParams(
        dataset="test_dataset",
        region_set="NUTS-0",
        region_name="Spain;France",
        variable="tas",
        resample_freq="MS",
        resample_func="mean",
        period="2010-2020",
        season_filter="01-12",
        season_filter_func="mean",
        anomaly=True,
        reference_period="1990-2005",
    )

    # Call the function
    result = get_climatology_map([ds], params)

    assert "region" in result
    assert "data" in result
    assert result["region"] == ["Spain", "France"]
    assert isinstance(result["data"], list)
    assert len(result["data"]) == 2
