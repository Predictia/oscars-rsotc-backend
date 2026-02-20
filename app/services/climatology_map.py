"""
Climatology map service module.

This module provides the logic for calculating climatological averages and
anomalies across multiple regions.
"""
import logging

import xarray as xr

from app.models.climatology_map_params import ClimatologyMapParams
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
def get_climatology_map(
    dataset: list[xr.Dataset], params: ClimatologyMapParams
) -> dict:
    """
    Calculate the climatology map for specified regions and period.

    This function applies temporal filtering, resampling, and optionally
    calculates anomalies relative to a reference period. The results are
    averaged over the selection.

    Parameters
    ----------
    dataset : list[xr.Dataset]
        The xarray Datasets containing the climate data.
    params : ClimatologyMapParams
        Parameters for the calculation, including regions, periods, and variable.

    Returns
    -------
    dict
        A dictionary containing:
        - region: List of region names.
        - data: List of averaged values for each region.
    """
    logger.info(
        f"Calculating climatology map for variable: {params.variable}, "
        f"region(s): {params.region_name}"
    )

    # Validate and get single dataset
    ds = get_single_dataset(dataset)
    # Select regions
    regions = params.region_name.split(";")
    logger.info(f"Selecting {len(regions)} regions")
    ds = ds.sel(region=regions)
    ds = ensure_float(ds)
    ds = transform_units(ds)

    logger.info(f"Loading data variable: {params.variable}")
    da_raw = ds.data_vars[params.variable].load()
    logger.info(f"Raw data shape: {da_raw.shape}")

    if "time_filter" in da_raw.dims:
        logger.info("Using precomputed time filter")
        da = handle_precomputed_time_filter(
            da_raw, params.season_filter, params.variable
        )
        yearly_filtered_data = filter_by_period(da, params.period)
    else:
        logger.info("Calculating temporal filtering (no precomputed filter found)")
        if params.resample_freq:
            logger.info(
                f"Resampling data to frequency: {params.resample_freq} "
                f"using {params.resample_func or 'mean'}"
            )
            da = getattr(
                da_raw.resample(time=params.resample_freq),
                params.resample_func or "mean",
            )()
        else:
            da = da_raw.copy()

        logger.info(f"Applying temporal filtering for period: {params.period}")

        filtered_data, yearly_filtered_data = TemporalFiltering(
            da,
            params.period,
            params.season_filter,
            params.season_filter_func,
        ).compute()

    if params.anomaly:
        logger.info(f"Calculating anomaly relative to: {params.reference_period}")
        if "time_filter" in da_raw.dims:
            # Use same season for reference
            ref_da = handle_precomputed_time_filter(
                da_raw, params.season_filter, params.variable
            )
            # Use filter_by_period to slice time, then mean
            logger.info(f"Filtering reference period: {params.reference_period}")
            ref_filtered = filter_by_period(ref_da, params.reference_period)
            ref_clim = ref_filtered.mean("time")
            yearly_filtered_data = yearly_filtered_data - ref_clim
        else:
            ref_filtered_data, ref_filtered_yearly_data = TemporalFiltering(
                da,
                params.reference_period,
                params.season_filter,
                params.season_filter_func,
            ).compute()
            ref_clim = ref_filtered_yearly_data.mean("time")
            yearly_filtered_data = yearly_filtered_data - ref_clim

    final_points = (
        len(yearly_filtered_data.time) if "time" in yearly_filtered_data.dims else "N/A"
    )
    logger.info(f"Final data points after filtering: {final_points}")

    climatology_filtered_data = yearly_filtered_data.mean("time")
    region_values = yearly_filtered_data.region.values

    logger.info(
        f"Climatology map calculation complete. Returning {len(region_values)} regions."
    )
    return dict(
        region=list(region_values),
        data=climatology_filtered_data.values.reshape(-1).tolist(),
    )
