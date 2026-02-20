"""
Time series service module.

This module provides the logic for calculating time series and anomalies
for climate variables.
"""
import logging

import xarray as xr

from app.models.time_series_params import TimeseriesParams
from app.utils.dataset_helpers import filter_by_period, handle_precomputed_time_filter
from app.utils.time_filtering import TemporalFiltering
from app.utils.timings import log_execution_time
from app.utils.transformation import ensure_float, transform_units

logger = logging.getLogger(__name__)


def _process_single_dataset(ds: xr.Dataset, params: TimeseriesParams) -> xr.DataArray:
    """
    Process a single dataset to extract the yearly filtered data.

    Parameters
    ----------
    ds : xr.Dataset
        The input dataset to process.
    params : TimeseriesParams
        Parameters containing region, period, and filtering options.

    Returns
    -------
    xr.DataArray
        The processed and filtered data array.
    """
    logger.info(f"Processing dataset for region: {params.region_name}")
    ds = ds.sel(region=params.region_name)
    ds = ensure_float(ds)
    ds = transform_units(ds)
    data_var = list(ds.data_vars)[0]
    da_raw = ds[data_var].load()
    logger.info(f"Loaded data variable: {data_var} with shape: {da_raw.shape}")

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
                f"Resampling data to: {params.resample_freq} "
                f"using {params.resample_func or 'mean'}"
            )
            da = getattr(
                da_raw.resample(time=params.resample_freq),
                params.resample_func or "mean",
            )()
        else:
            da = da_raw.copy()

        filtered_data, yearly_filtered_data = TemporalFiltering(
            da,
            params.period,
            params.season_filter,
            params.season_filter_func,
        ).compute()

    if params.anomaly:
        logger.info(f"Calculating anomaly relative to: {params.reference_period}")
        ref_filtered_data, ref_filtered_yearly_data = TemporalFiltering(
            da,
            params.reference_period,
            params.season_filter,
            params.season_filter_func,
        ).compute()
        ref_clim = ref_filtered_yearly_data.mean("time")
        yearly_filtered_data = yearly_filtered_data - ref_clim

    logger.info(
        f"Finished processing dataset. "
        f"Resulting time points: {len(yearly_filtered_data.time)}"
    )
    return yearly_filtered_data


@log_execution_time
def get_time_series(dataset: list[xr.Dataset], params: TimeseriesParams) -> dict:
    """
    Calculate the time series for a given variable and region.

    This function applies temporal filtering, resampling, and optionally
    calculates anomalies relative to a reference period.

    Parameters
    ----------
    dataset : list[xr.Dataset]
        The xarray Datasets containing the climate data.
    params : TimeseriesParams
        Parameters for the calculation, including region, period, and variable.

    Returns
    -------
    dict
        A dictionary containing:
        - date: List of dates in the time series.
        - value: List of values for each date.
    """
    logger.info(
        f"Calculating time series for variable: {params.variable}, "
        f"region: {params.region_name}"
    )

    yearly_filtered_data_list = [_process_single_dataset(ds, params) for ds in dataset]

    yearly_filtered_data = xr.merge(yearly_filtered_data_list)

    time_values = yearly_filtered_data.time.dt.strftime("%Y-%m-%d").values

    value_dict = {
        str(var): yearly_filtered_data[var].values.tolist()
        for var in yearly_filtered_data.data_vars
    }

    logger.info(
        f"Time series calculation complete. Returning {len(time_values)} points."
    )
    return dict(date=list(time_values), value=value_dict)
