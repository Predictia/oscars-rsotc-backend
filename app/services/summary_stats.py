import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np
import xarray as xr

from app.models.summary_stats_params import SummaryStatsParams
from app.utils.ensure_data_type import ensure_float
from app.utils.time_filtering import TemporalFiltering
from app.utils.time_filtering_indices import get_time_filter_name
from app.utils.timings import log_execution_time

logger = logging.getLogger(__name__)


def calculate_trend(da_yearly: xr.DataArray, start_year: int = 1940) -> Optional[float]:
    """
    Calculate the linear trend per decade starting from a specific year.

    Parameters
    ----------
    da_yearly : xr.DataArray
        Yearly aggregated data.
    start_year : int, optional
        The year to start the trend calculation from, by default 1970.

    Returns
    -------
    Optional[float]
        The calculated trend per decade, or None if calculation fails.
    """
    try:
        da_yearly = ensure_float(da_yearly)
        da_slice = da_yearly.sel(time=slice(f"{start_year}", None))

        if len(da_slice) < 10:
            return None

        y = da_slice.values
        x = np.arange(len(y))

        # Remove NaNs
        mask = ~np.isnan(y)
        if not np.any(mask):
            return None

        slope, _ = np.polyfit(x[mask], y[mask], 1)
        return float(slope * 10)  # Trend per decade
    except Exception as e:
        logger.warning(f"Failed to calculate trend: {e}")
        return None


def get_ref_stats(
    da_yearly: xr.DataArray, target_value: Optional[float] = None
) -> Dict[str, Any]:
    """
    Calculate stats (mean, max, min, percentiles) for the 1991-2020 reference period.

    Parameters
    ----------
    da_yearly : xr.DataArray
        Yearly aggregated data.
    target_value : Optional[float], optional
        The value to calculate the percentile for, by default None.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing stats for the reference period.
    """
    start, end = 1991, 2020
    try:
        ref_da = da_yearly.sel(time=slice(f"{start}", f"{end}"))
        if len(ref_da) == 0:
            return {}

        mean_val = float(ref_da.mean().values)
        max_val = float(ref_da.max().values)
        min_val = float(ref_da.min().values)

        # Percentiles
        p10 = float(ref_da.quantile(0.1).values)
        p90 = float(ref_da.quantile(0.9).values)
        p95 = float(ref_da.quantile(0.95).values)

        res = {
            "mean": mean_val if not np.isnan(mean_val) else None,
            "max": max_val if not np.isnan(max_val) else None,
            "min": min_val if not np.isnan(min_val) else None,
            "percentiles": {
                "10": p10 if not np.isnan(p10) else None,
                "90": p90 if not np.isnan(p90) else None,
                "95": p95 if not np.isnan(p95) else None,
            },
        }

        # Calculate percentile of target_value
        if target_value is not None:
            # Simple percentile calculation: count values below target_value
            ref_values = ref_da.values
            ref_values = ref_values[~np.isnan(ref_values)]
            if len(ref_values) > 0:
                perc = (ref_values < target_value).sum() / len(ref_values) * 100
                res["percentile_rank"] = float(perc)

        return res
    except Exception as e:
        logger.warning(f"Failed to calculate ref stats: {e}")
        return {}


def _calculate_variable_stats(
    da_full: xr.DataArray,
    short_name: str,
    unit: str,
    long_name: str,
    params: SummaryStatsParams,
    agg_value: Optional[str] = None,
) -> Tuple[str, Dict[str, Any]]:
    """
    Calculate stats for a single variable for a specific period and season.

    Parameters
    ----------
    da_full : xr.DataArray
        Full resolution data for the variable.
    short_name : str
        Short name of the variable (e.g., 'tas').
    unit : str
        Unit of the variable.
    long_name : str
        Descriptive long name.
    params : SummaryStatsParams
        Request parameters containing period and season_filter.
    agg_value : Optional[str], optional
        Manual aggregation value, if any.

    Returns
    -------
    Tuple[str, Dict[str, Any]]
        A tuple containing the short_name and a dictionary of calculated stats.
    """
    is_index = "time_filter" in da_full.dims
    if is_index:
        time_filter = get_time_filter_name(params.season_filter)
        if time_filter not in da_full.time_filter.values:
            return short_name, {
                "error": (
                    f"Filter {params.season_filter} not available "
                    f"for index {short_name}"
                )
            }
        # Indices are already aggregated. We need yearly data for this filter.
        da_yearly = da_full.sel(time_filter=time_filter).dropna(dim="time")
        # Ensure time is YS for consistent handling if it's not
        da_yearly = da_yearly.sortby("time").resample(time="YS").mean()
    else:
        # For ERA5, we use TemporalFiltering to get yearly aggregates
        tf = TemporalFiltering(
            dataset=da_full.to_dataset(name=short_name),
            period_range="all",
            time_filter=params.season_filter,
            statistical=agg_value,
        )
        _, da_yearly_ds = tf.compute()
        da_yearly = da_yearly_ds[short_name]

    # Ensure we work with floats (days) instead of raw timedeltas
    da_yearly = ensure_float(da_yearly)

    # Target period value
    try:
        start_p, end_p = params.period.split("-")
        target_val = float(da_yearly.sel(time=slice(start_p, end_p)).mean().values)
        if np.isnan(target_val):
            target_val = None
    except Exception:
        target_val = None

    ref_stats = get_ref_stats(da_yearly, target_value=target_val)
    trend = calculate_trend(da_yearly, start_year=1940)

    anomalies = {}
    anomalies_as_perc = {}
    ref_means = {}
    ref_maxs = {}
    ref_mins = {}
    ref_percentiles = {}

    if ref_stats:
        ref_val = ref_stats.get("mean")
        ref_period = "1991_2020"
        ref_means[ref_period] = ref_val
        ref_maxs[ref_period] = ref_stats.get("max")
        ref_mins[ref_period] = ref_stats.get("min")
        ref_percentiles[ref_period] = ref_stats.get("percentiles", {})

        if target_val is not None and ref_val is not None:
            anomalies[ref_period] = target_val - ref_val
            # Calculate percentage change if ref_val is not zero
            if ref_val != 0:
                anomalies_as_perc[ref_period] = (
                    (target_val - ref_val) / abs(ref_val)
                ) * 100
        else:
            anomalies[ref_period] = None
            anomalies_as_perc[ref_period] = None

    return short_name, {
        "long_name": long_name,
        "unit": unit,
        "value": target_val,
        "anomalies": anomalies,
        "anomalies_as_perc": anomalies_as_perc,
        "ref_means": ref_means,
        "ref_maxs": ref_maxs,
        "ref_mins": ref_mins,
        "ref_percentiles": ref_percentiles,
        "trend": trend,
    }


@log_execution_time
def get_summary_stats(
    dataset: Union[xr.Dataset, list[xr.Dataset]], params: SummaryStatsParams
) -> Dict[str, Any]:
    """
    Generate a structured climate summary for a given region, period and season.

    Parameters
    ----------
    dataset : Union[xr.Dataset, list[xr.Dataset]]
        The climate dataset(s) containing the variables.
    params : SummaryStatsParams
        Request parameters including region, period, and seasonal filter.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing a list of 'items', each representing a
        variable's summary.
    """
    region = params.region_name
    logger.info(
        "Generating structured summary for region: %s, " "period: %s, season: %s",
        region,
        params.period,
        params.season_filter,
    )

    # Ensure dataset is a list for uniform iteration
    datasets = dataset if isinstance(dataset, list) else [dataset]

    # Dictionary to store calculated stats
    stats_dict = {}

    # Define variable mappings with potential multiple aggregations
    var_info = {
        "tas": [("mean", "mean temperature")],
        "tasmax": [
            ("mean", "average maximum temperature"),
            ("max", "maximum temperature"),
        ],
        "tasmin": [
            ("mean", "average minimum temperature"),
            ("min", "minimum temperature"),
        ],
        "pr": [("sum", "total precipitation"), ("max", "maximum precipitation")],
        "fd": [("mean", "number of frost days")],
        "tr20": [("mean", "number of tropical nights (>20°C)")],
        "tr25": [("mean", "number of warm tropical nights (>25°C)")],
        "tx30": [("mean", "number of hot days (>30°C)")],
        "tx35": [("mean", "number of very hot days (>35°C)")],
        "tx40": [("mean", "number of extremely hot days (>40°C)")],
        "r1mm": [("mean", "number of wet days (≥1mm)")],
        "r20mm": [("mean", "number of heavy precipitation days (≥20mm)")],
        "r95ptot": [("mean", "amount of precipitation from very wet days")],
        "sfcWind": [("mean", "wind speed"), ("max", "maximum wind speed")],
    }

    # Preparation for parallel execution
    tasks = []
    # Maintain order of variables as defined in var_info
    ordered_vars = list(var_info.keys())

    for var_name in ordered_vars:
        aggs = var_info[var_name]
        internal_var = f"{var_name}_None"

        # Find which dataset contains this variable
        ds_var = next((d for d in datasets if internal_var in d.data_vars), None)
        if ds_var is None:
            continue

        da = ds_var.sel(region=region)[internal_var].load()
        unit = ds_var[internal_var].attrs.get("units", "")
        if not unit:
            # Fallback units if not present in attrs
            units_map = {
                "tas": "°C",
                "tasmax": "°C",
                "tasmin": "°C",
                "pr": "mm",
                "sfcWind": "km/h",
            }
            unit = units_map.get(
                var_name,
                "days"
                if var_name
                in ["fd", "tr20", "tr25", "tx30", "tx35", "tx40", "r1mm", "r20mm"]
                else "",
            )

        for agg, long_name in aggs:
            tasks.append((da, var_name, unit, long_name, params, agg))

    if tasks:
        with ThreadPoolExecutor() as executor:
            # map maintains input order
            results = list(executor.map(lambda p: _calculate_variable_stats(*p), tasks))
            for short_name, var_stats in results:
                # Create a unique ID based on variable and index/aggregation
                # For primary variables with multiple aggs, use variable_agg
                # For indices, just use the variable name
                agg_type = ""
                # Find the aggregation that produced this result
                for v_name, aggs in var_info.items():
                    if v_name == short_name:
                        for agg, l_name in aggs:
                            if l_name == var_stats["long_name"]:
                                agg_type = agg
                                break

                # Assign a clean ID
                # If it's a primary variable with multiple aggs, distinguish them
                if (
                    short_name in ["tasmax", "tasmin", "pr", "sfcWind"]
                    and len(var_info[short_name]) > 1
                ):
                    stat_id = f"{short_name}_{agg_type}"
                else:
                    stat_id = short_name

                var_stats["variable"] = short_name
                var_stats["id"] = stat_id
                stats_dict[stat_id] = var_stats

    return {"stats": stats_dict}
