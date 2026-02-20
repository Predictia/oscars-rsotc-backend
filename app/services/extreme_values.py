"""
Extreme values service module.

This module provides the logic for retrieving the top 5 maximum and minimum
values for a climate variable in a specific region and period.
"""
import logging

import xarray as xr

from app.models.extreme_values_params import ExtremeValuesParams
from app.utils.dataset_helpers import (
    filter_by_period,
    get_single_dataset,
    handle_precomputed_time_filter,
)
from app.utils.time_filtering import TemporalFiltering
from app.utils.timings import log_execution_time
from app.utils.transformation import ensure_float, transform_units

logger = logging.getLogger(__name__)


@log_execution_time
def get_extreme_values(dataset: list[xr.Dataset], params: ExtremeValuesParams) -> dict:
    """
    Retrieve the top 5 maximum and minimum values for a given selection.

    Parameters
    ----------
    dataset : list[xr.Dataset]
        The xarray Dataset(s) containing the climate data.
    params : ExtremeValuesParams
        Parameters for the calculation, including region, period, and variable.

    Returns
    -------
    dict
        A dictionary containing:
        - date_min: Dates of the top 5 minimum values.
        - value_min: Top 5 minimum values.
        - date_max: Dates of the top 5 maximum values.
        - value_max: Top 5 maximum values.
    """
    logger.info(
        f"Retrieving extreme values for variable: {params.variable}, "
        f"region: {params.region_name}"
    )

    ds = get_single_dataset(dataset)
    logger.info(f"Selecting region: {params.region_name}")
    ds = ds.sel(region=params.region_name)
    ds = ensure_float(ds)
    ds = transform_units(ds)

    data_var = (
        params.variable if "_" not in params.variable else params.variable.split("_")[0]
    )
    logger.info(f"Loading data variable: {data_var}")
    da_raw = ds.data_vars[data_var].load()
    logger.info(f"Raw data shape: {da_raw.shape}")

    if "time_filter" in da_raw.dims:
        logger.info("Using precomputed time filter")
        da = handle_precomputed_time_filter(
            da_raw, params.season_filter, params.variable
        )
        da = filter_by_period(da, params.period)
    else:
        logger.info("Calculating temporal filtering (no precomputed filter found)")
        da = TemporalFiltering(
            da_raw,
            params.period,
            params.season_filter,
        ).sel_time_filter()

    logger.info(f"Filtered data points: {len(da.time)}")

    df = da.to_dataframe().reset_index()
    df = df.sort_values(by=[params.variable], ascending=False)

    logger.debug("Selecting top 5 max and min values")
    df_maxs = df.iloc[0:5]
    df_mins = df.iloc[-5:]

    return dict(
        date_min=df_mins["time"].dt.strftime("%Y-%m-%d").to_list(),
        value_min=df_mins[params.variable].to_list(),
        date_max=df_maxs["time"].dt.strftime("%Y-%m-%d").to_list(),
        value_max=df_maxs[params.variable].to_list(),
    )
