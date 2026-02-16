import logging

import xarray as xr

from app.utils.time_filtering_indices import get_time_filter_name

logger = logging.getLogger(__name__)


def get_single_dataset(dataset: list[xr.Dataset]) -> xr.Dataset:
    """
    Validate that the dataset list contains only one dataset and return it.

    Parameters
    ----------
    dataset : list[xr.Dataset]
        List of datasets.

    Returns
    -------
    xr.Dataset
        The single dataset in the list.

    Raises
    ------
    ValueError
        If the list contains more than one dataset.
    """
    if len(dataset) > 1:
        raise ValueError("Multiple datasets not supported for this operation")
    return dataset[0]


def handle_precomputed_time_filter(
    da: xr.DataArray, season_filter: str, variable: str
) -> xr.DataArray:
    """
    Select the appropriate time filter from a DataArray.

    The DataArray should have a precomputed 'time_filter' dimension.
    Falls back to 'Annual' if the requested filter is not found.

    Parameters
    ----------
    da : xr.DataArray
        The DataArray containing the 'time_filter' dimension.
    season_filter : str
        The requested season filter (e.g., 'DJF', 'MAM').
    variable : str
        The name of the variable (for logging purposes).

    Returns
    -------
    xr.DataArray
        The DataArray selected for the specific time filter.
    """
    tf_name = get_time_filter_name(season_filter)
    if tf_name not in da.time_filter.values:
        logger.warning(
            f"Season {season_filter} (mapped to {tf_name}) not found "
            f"for index {variable}. Falling back to 'Annual'."
        )
        tf_name = "Annual"

    return da.sel(time_filter=tf_name).dropna(dim="time")


def filter_by_period(da: xr.DataArray, period: str) -> xr.DataArray:
    """
    Filter the DataArray by a time period string.

    The format should be 'start-end', or return copy if 'all'.

    Parameters
    ----------
    da : xr.DataArray
        The DataArray to filter.
    period : str
        The period string (e.g., '1981-2010' or 'all').

    Returns
    -------
    xr.DataArray
        The filtered DataArray.
    """
    if period != "all":
        start, end = period.split("-")
        return da.sel(time=slice(start, end))
    return da.copy()
