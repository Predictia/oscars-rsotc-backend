"""Histograms router module."""
from typing import Annotated

import xarray as xr
from fastapi import APIRouter, Body, Depends

from app.load import get_datasets
from app.models.histograms import Histograms
from app.models.histograms_params import HistogramsParams
from app.services.histograms import get_histograms

router = APIRouter(prefix="/histograms")


@router.post("")
def _get_histograms(
    dataset: Annotated[list[xr.Dataset], Depends(get_datasets)],
    params: Annotated[HistogramsParams, Body(...)],
) -> Histograms:
    """
    Handle POST request for histograms calculation.

    Parameters
    ----------
    params : HistogramsParams
        The parameters for the histograms calculation.
    dataset : list[xr.Dataset]
        The dataset(s) loaded via dependency.

    Returns
    -------
    Histograms
        The calculated histograms data.
    """
    return get_histograms(dataset, params)
