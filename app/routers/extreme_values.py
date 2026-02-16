"""Extreme values router module."""
from typing import Annotated

import xarray as xr
from fastapi import APIRouter, Body, Depends

from app.load import get_datasets
from app.models.extreme_values import ExtremeValues
from app.models.extreme_values_params import ExtremeValuesParams
from app.services.extreme_values import get_extreme_values

router = APIRouter(prefix="/extreme_values")


@router.post("")
def _get_extreme_values(
    dataset: Annotated[list[xr.Dataset], Depends(get_datasets)],
    params: Annotated[ExtremeValuesParams, Body(...)],
) -> ExtremeValues:
    """
    Handle POST request for extreme values calculation.

    Parameters
    ----------
    params : ExtremeValuesParams
        The parameters for the extreme values calculation.
    dataset : list[xr.Dataset]
        The dataset(s) loaded via dependency.

    Returns
    -------
    ExtremeValues
        The calculated extreme values data.
    """
    return get_extreme_values(dataset, params)
