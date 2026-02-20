"""
Histograms service module.

This module provides the logic for calculating histograms and comparing the
distribution of climate variables between two periods.
"""
import logging

import numpy as np
import xarray as xr

from app.models.histograms_params import HistogramsParams
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
def get_histograms(dataset: list[xr.Dataset], params: HistogramsParams) -> dict:
    """
    Calculate histograms for comparing two climate periods.

    This function computes density histograms using common bins for both a
    period of interest and a reference period. It also identifies the top 3
    extreme values and their dates for both periods.

    Parameters
    ----------
    dataset : list[xr.Dataset]
        The xarray Dataset(s) containing the climate data.
    params : HistogramsParams
        Parameters for the calculation, including region, periods, and variable.

    Returns
    -------
    dict
        A dictionary containing:
        - bins: Centers of the histogram bins.
        - value_period: Histogram density for the period of interest.
        - value_reference: Histogram density for the reference period.
        - max_value_period: Top 3 extreme values for the period of interest.
        - max_value_reference: Top 3 extreme values for the reference period.
        - max_date_period: Dates of top 3 extremes for the period of interest.
        - max_date_reference: Dates of top 3 extremes for the reference period.
    """
    logger.info(
        f"Calculating histograms for variable: {params.variable}, "
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
        # Pre-select season once
        da_season = handle_precomputed_time_filter(
            da_raw, params.season_filter, params.variable
        )
        # Filter by periods
        logger.info(
            f"Filtering by periods: {params.period} and {params.reference_period}"
        )
        da = filter_by_period(da_season, params.period)
        da_reference = filter_by_period(da_season, params.reference_period)
    else:
        logger.info("Calculating temporal filtering (no precomputed filter found)")
        # Filter both periods
        da = TemporalFiltering(
            da_raw,
            params.period,
            params.season_filter,
        ).sel_time_filter()

        da_reference = TemporalFiltering(
            da_raw,
            params.reference_period,
            params.season_filter,
        ).sel_time_filter()

    logger.info(
        f"Filtered data points - Period: {len(da.time)}, "
        f"Reference: {len(da_reference.time)}"
    )
    # Aplanar y eliminar NaNs
    data = da.values.flatten()
    data_reference = da_reference.values.flatten()

    times = da.time.values.flatten()
    times_reference = da_reference.time.values.flatten()

    logger.debug("Calculating common bins and density histograms")
    # Calcular bins comunes
    combined = np.concatenate([data, data_reference])
    bins = np.histogram_bin_edges(combined, bins="auto")
    bins = np.round(bins, decimals=1)
    bin_centers = 0.5 * (bins[1:] + bins[:-1])

    # Histogramas con densidad
    hist_period, _ = np.histogram(data, bins=bins, density=True)
    hist_reference, _ = np.histogram(data_reference, bins=bins, density=True)

    # Top 3 extremos y sus fechas
    top_indices = np.argsort(data)[-3:][::-1]
    top_extremes_period = data[top_indices]

    top_indices_ref = np.argsort(data_reference)[-3:][::-1]
    top_extremes_reference = data_reference[top_indices_ref]

    top_dates_period = [
        str(np.datetime_as_string(times[i], unit="D")) for i in top_indices
    ]
    top_dates_reference = [
        str(np.datetime_as_string(times_reference[i], unit="D"))
        for i in top_indices_ref
    ]

    return dict(
        bins=bin_centers.tolist(),
        value_period=hist_period.tolist(),
        value_reference=hist_reference.tolist(),
        max_value_period=top_extremes_period.tolist(),
        max_value_reference=top_extremes_reference.tolist(),
        max_date_period=top_dates_period,
        max_date_reference=top_dates_reference,
    )
