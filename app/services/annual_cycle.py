"""
Annual cycle service module.

This module provides the logic for calculating the annual cycle of a climate
variable, including historical statistics and smoothing.
"""
import logging

import numpy as np
import pandas as pd
import xarray as xr

from app.models.annual_cycle_params import AnnualCycleParams
from app.utils.ensure_data_type import ensure_float
from app.utils.timings import log_execution_time

logger = logging.getLogger(__name__)


@log_execution_time
def get_annual_cycle(
    dataset: list[xr.Dataset], params: AnnualCycleParams
) -> dict[str, np.ndarray]:
    """
    Calculate the annual cycle statistics for a specific region and period.

    This function computes the daily stats (percentiles, median, min, max)
    over a reference period, applies a 5-day rolling mean smoothing, and
    compares the current period's data against these statistics.

    Parameters
    ----------
    dataset : list[xr.Dataset]
        The xarray Datasets containing the climate data.
    params : AnnualCycleParams
        Parameters for the calculation, including region, periods, and variable.

    Returns
    -------
    dict[str, np.ndarray]
        A dictionary containing the calculated annual cycle data series:
        - date: List of dates in YYYY-MM-DD format.
        - value: Current period values.
        - percentile90, median, percentile10: Smoothed reference statistics.
        - min, max: Reference period extremes.
        - higher_than_max, lower_than_min: Boolean indicators (as ints).
    """
    logger.info(
        f"Calculating annual cycle for variable: {params.variable}, "
        f"region: {params.region_name}"
    )

    if len(dataset) > 1:
        raise ValueError("Multiple datasets not supported for annual cycle calculation")
    else:
        ds = dataset[0].sel(region=params.region_name)

    da_raw = ds.data_vars[
        params.variable if "_" not in params.variable else params.variable.split("_")[0]
    ].load()

    if "time_filter" in da_raw.dims:
        raise NotImplementedError("Annual cycle calculation for indices not possible")

    data = da_raw.sel(time=slice(*params.period.split("-")))
    reference_data = da_raw.sel(time=slice(*params.reference_period.split("-")))

    data = ensure_float(data)
    reference_data = ensure_float(reference_data)

    df_data = data.to_dataframe(name="value").reset_index()
    df_reference = reference_data.to_dataframe(name="value").reset_index()

    df_data["dayofyear"] = df_data["time"].dt.strftime("%m-%d")
    df_reference["dayofyear"] = df_reference["time"].dt.strftime("%m-%d")

    logger.debug(f"Calculating stats for reference period: {params.reference_period}")

    stats = (
        df_reference.groupby("dayofyear")["value"]
        .agg(
            percentile90=lambda x: np.nanpercentile(x, 90),
            median="median",
            percentile10=lambda x: np.nanpercentile(x, 10),
            min="min",
            max="max",
        )
        .reset_index()
    )
    stats = stats.sort_values("dayofyear").reset_index(drop=True)

    extended = pd.concat([stats.iloc[-2:], stats, stats.iloc[:2]], ignore_index=True)

    logger.debug("Applying 5-day rolling mean smoothing")
    for col in ["percentile90", "median", "percentile10"]:
        smoothed = (
            extended[col]
            .rolling(window=5, center=True, min_periods=1)
            .mean()
            .iloc[2:-2]
            .values
        )
        stats[col] = smoothed

    merged = pd.merge(df_data, stats, on="dayofyear", how="left")

    merged["higher_than_max"] = (merged["value"] > merged["max"]).astype(int)
    merged["lower_than_min"] = (merged["value"] < merged["min"]).astype(int)

    logger.info(f"Annual cycle calculation complete. Returning {len(merged)} records.")
    return dict(
        date=merged["time"].dt.strftime("%Y-%m-%d").tolist(),
        value=merged["value"].tolist(),
        percentile90=merged["percentile90"].tolist(),
        median=merged["median"].tolist(),
        percentile10=merged["percentile10"].tolist(),
        min=merged["min"].tolist(),
        max=merged["max"].tolist(),
        higher_than_max=merged["higher_than_max"].tolist(),
        lower_than_min=merged["lower_than_min"].tolist(),
    )
