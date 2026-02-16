"""Summary stats router module."""
from typing import Annotated

import xarray as xr
from fastapi import APIRouter, Body, Depends

from app.load import get_datasets
from app.models.summary_stats import SummaryStats
from app.models.summary_stats_params import SummaryStatsParams
from app.services.summary_stats import get_summary_stats

router = APIRouter(prefix="/summary_stats")


@router.post("")
def _get_summary_stats(
    dataset: Annotated[list[xr.Dataset], Depends(get_datasets)],
    params: Annotated[SummaryStatsParams, Body(...)],
) -> SummaryStats:
    """Generate a summary stats for a given region."""
    result = get_summary_stats(dataset, params)

    return SummaryStats(**result)
