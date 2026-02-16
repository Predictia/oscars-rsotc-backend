"""Time series router module."""
from typing import Annotated

import xarray as xr
from fastapi import APIRouter, Body, Depends

from app.load import get_datasets
from app.models.time_series import TimeSeries
from app.models.time_series_params import TimeseriesParams
from app.services.time_series import get_time_series

router = APIRouter(prefix="/time_series")


@router.post("")
def _get_time_series(
    dataset: Annotated[list[xr.Dataset], Depends(get_datasets)],
    params: Annotated[TimeseriesParams, Body(...)],
) -> TimeSeries:
    """
    Handle POST request for time series calculation.

    Parameters
    ----------
    dataset : list[xr.Dataset]
        The dataset(s) loaded via dependency.
    params : TimeseriesParams
        The parameters for the time series calculation.

    Returns
    -------
    TimeSeries
        The calculated time series data.
    """
    return get_time_series(dataset, params)
