import logging
from typing import Union

import numpy as np
import xarray as xr

logger = logging.getLogger(__name__)


def transform_units(ds: xr.Dataset) -> xr.Dataset:
    """
    Transform units of the dataset.

    Currently handles conversion of 'sfcWind' from m/s to km/h.

    Parameters
    ----------
    ds : xr.Dataset
        The input dataset containing climate variables.

    Returns
    -------
    xr.Dataset
        The dataset with transformed units.
    """
    for var in ["sfcWind", "sfcWind_None"]:
        if var in ds.data_vars:
            logger.info(f"Transforming units of '{var}' from m/s to km/h")
            ds[var] = ds[var] * 3.6
            ds[var].attrs["units"] = "km/h"

    return ds


def ensure_float(data: xr.Dataset) -> xr.Dataset:
    """
    Ensure the Dataset contains float values.

    If it contains timedelta64, convert it to float days. All variables
    are cast to float64.

    Parameters
    ----------
    data : xr.Dataset
        The input dataset to be processed.

    Returns
    -------
    xr.Dataset
        The processed dataset with float values.
    """
    for data_var in list(data.data_vars):
        if np.issubdtype(data[data_var].dtype, np.timedelta64):
            logger.info(
                f"Transforming units of '{data_var}' from timedelta64 to float days"
            )
            data[data_var] = data[data_var] / np.timedelta64(1, "D")
        data[data_var] = data[data_var].astype(float)

    return data