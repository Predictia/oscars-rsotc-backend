import numpy as np
import pandas as pd
import xarray as xr

from app.models.annual_cycle_params import AnnualCycleParams
from app.services.annual_cycle import get_annual_cycle


def test_get_annual_cycle():
    # Create a mock dataset
    times = pd.date_range("1950-01-01", "2024-12-31", freq="D")
    data = np.random.rand(len(times))
    ds = xr.Dataset(data_vars={"tas": (("time",), data)}, coords={"time": times})
    ds = ds.expand_dims(region=["Spain", "France"])

    # Define parameters
    params = AnnualCycleParams(
        dataset="ERA5",
        region_set="NUTS-0",
        region_name="Spain",
        variable="tas",
        period="2024-2024",
        reference_period="1950-2023",
    )

    # Call the function
    get_annual_cycle([ds], params)
