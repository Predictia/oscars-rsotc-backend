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
    logger.info(f"Handling precomputed time filter: {tf_name} for variable: {variable}")

    if tf_name not in da.time_filter.values:
        logger.warning(
            f"Season {season_filter} (mapped to {tf_name}) not found "
            f"for index {variable}. Falling back to 'Annual'."
        )
        tf_name = "Annual"

    selected_da = da.sel(time_filter=tf_name).dropna(dim="time")
    logger.info(
        f"Selected time filter '{tf_name}'. "
        f"Data points remaining: {len(selected_da.time)}"
    )
    return selected_da


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
        try:
            start, end = period.split("-")
            logger.info(f"Filtering by period: {start} to {end}")

            # Log time index properties to help debug non-monotonic issues
            if not da.indexes["time"].is_monotonic_increasing:
                logger.warning("Time index is not monotonic increasing!")

            time_range = da.time.values
            if len(time_range) > 0:
                logger.info(
                    f"Available time range: {time_range[0]} to {time_range[-1]}"
                )
            else:
                logger.warning(
                    "DataArray has an empty time dimension before filtering."
                )

            return da.sel(time=slice(start, end))
        except Exception as e:
            logger.error(f"Error filtering by period '{period}': {str(e)}")
            raise
    return da.copy()
