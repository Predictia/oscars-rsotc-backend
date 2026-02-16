import numpy as np
import pandas as pd
import xarray as xr

from app.models.histograms_params import HistogramsParams
from app.services.histograms import get_histograms


def test_get_histograms():
    # Create a mock dataset
    times = pd.date_range("2000-01-01", "2024-12-31", freq="D")
    data = np.random.rand(len(times))
    ds = xr.Dataset(data_vars={"tas": (("time",), data)}, coords={"time": times})
    ds = ds.expand_dims(region=["Spain", "France"])

    # Define parameters
    params = HistogramsParams(
        dataset="ERA5",
        region_set="NUTS-0",
        region_name="Spain",
        variable="tas",
        period="2010-2020",
        reference_period="2000-2005",
        season_filter="01-12",
    )

    # Call the function
    get_histograms([ds], params)
