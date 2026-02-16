"""Annual cycle router module."""
from typing import Annotated

import xarray as xr
from fastapi import APIRouter, Body, Depends

from app.load import get_datasets
from app.models.annual_cycle import AnnualCycle
from app.models.annual_cycle_params import AnnualCycleParams
from app.services.annual_cycle import get_annual_cycle

router = APIRouter(prefix="/annual_cycle")


@router.post("")
def _get_annual_cycle(
    params: Annotated[AnnualCycleParams, Body(...)],
    dataset: Annotated[list[xr.Dataset], Depends(get_datasets)],
) -> AnnualCycle:
    """
    Handle POST request for annual cycle calculation.

    Parameters
    ----------
    params : AnnualCycleParams
        The parameters for the annual cycle calculation.
    dataset : list[xr.Dataset]
        The dataset(s) loaded via dependency.

    Returns
    -------
    AnnualCycle
        The calculated annual cycle data.
    """
    return get_annual_cycle(dataset, params)
