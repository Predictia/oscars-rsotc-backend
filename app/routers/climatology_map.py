"""Climatology map router module."""
from typing import Annotated

import xarray as xr
from fastapi import APIRouter, Body, Depends

from app.load import get_datasets
from app.models.climatology_map import ClimatologyMap
from app.models.climatology_map_params import ClimatologyMapParams
from app.services.climatology_map import get_climatology_map

router = APIRouter(prefix="/climatology_map")


@router.post("")
def _get_climatology_map(
    dataset: Annotated[list[xr.Dataset], Depends(get_datasets)],
    params: Annotated[ClimatologyMapParams, Body(...)],
) -> ClimatologyMap:
    """
    Handle POST request for climatology map calculation.

    Parameters
    ----------
    params : ClimatologyMapParams
        The parameters for the climatology map calculation.
    dataset : list[xr.Dataset]
        The dataset(s) loaded via dependency.

    Returns
    -------
    ClimatologyMap
        The calculated climatology map data.
    """
    return get_climatology_map(dataset, params)
