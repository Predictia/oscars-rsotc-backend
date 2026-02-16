"""
Data loading module for the application.

This module provides functions to load xarray datasets from either local
storage or S3 based on request parameters. It includes caching mechanisms
to optimize dataset access.
"""
import logging
import os
from functools import lru_cache
from typing import Tuple, Union

import fsspec
import xarray as xr

from app.config import (
    INPUT_DATA_DIR,
    S3_ACCESS_KEY,
    S3_BUCKET_NAME,
    S3_ENDPOINT_URL,
    S3_REGION,
    S3_SECRET_KEY,
)
from app.models.annual_cycle_params import AnnualCycleParams
from app.models.climatology_map_params import ClimatologyMapParams
from app.models.extreme_values_params import ExtremeValuesParams
from app.models.histograms_params import HistogramsParams
from app.models.summary_stats_params import SummaryStatsParams
from app.models.time_series_params import TimeseriesParams
from app.utils.timings import log_execution_time

RequestParams = Union[
    AnnualCycleParams,
    TimeseriesParams,
    ClimatologyMapParams,
    HistogramsParams,
    ExtremeValuesParams,
    SummaryStatsParams,
]


logger = logging.getLogger(__name__)


# Full set of available variables and indices
BASE_VARIABLES = [
    "pr_None",
    "sfcWind_None",
    "tas_None",
    "tasmax_None",
    "tasmin_None",
]

DERIVED_INDICES = [
    "fd_None",
    "r1mm_None",
    "r20mm_None",
    "r95ptot_None",
    "tr20_None",
    "tr25_None",
    "tx30_None",
    "tx35_None",
    "tx40_None",
]

ALL_AVAILABLE_VARIABLES = BASE_VARIABLES + DERIVED_INDICES


@lru_cache(maxsize=1)
def _s3_storage_options() -> dict:
    """
    Get storage options for S3 access.

    Returns
    -------
    dict
        A dictionary containing S3 storage configuration.
    """
    client_kwargs = {"endpoint_url": S3_ENDPOINT_URL}
    if S3_REGION:
        client_kwargs["region_name"] = S3_REGION

    return {
        "anon": False,
        "key": S3_ACCESS_KEY,
        "secret": S3_SECRET_KEY,
        "client_kwargs": client_kwargs,
        "default_fill_cache": False,
        "use_listings_cache": True,
        "config_kwargs": {"max_pool_connections": 64},
    }


@lru_cache(maxsize=1)
@log_execution_time
def _build_dataset_mapping() -> dict[Tuple[str, str, str, str], dict]:
    """
    Build a mapping from dataset attributes to their storage paths.

    The mapping includes both local and S3 URIs for each dataset.
    If INPUT_DATA_DIR is provided and exists, it scans that directory.
    Otherwise, it lists the configured S3 bucket.

    Returns
    -------
    dict[Tuple[str, str, str, str], dict]
        A dictionary where keys are (variable, level, dataset, region_set)
        and values are dictionaries containing "local" and "s3" paths.
    """
    mapping: dict[Tuple[str, str, str, str], dict] = {}

    if INPUT_DATA_DIR and os.path.exists(INPUT_DATA_DIR):
        logger.info(f"Scanning local directory for datasets: {INPUT_DATA_DIR}")
        entries = [
            f
            for f in os.listdir(INPUT_DATA_DIR)
            if os.path.isdir(os.path.join(INPUT_DATA_DIR, f)) and f.endswith(".zarr")
        ]
        for name in entries:
            # name is already something like tas_None_ERA5_NUTS-0.zarr
            parts = name[:-5].split("_")  # strip .zarr
            if len(parts) != 4:
                continue
            variable, level, dataset, region_set = parts

            mapping[(variable, level, dataset, region_set)] = {
                "local": os.path.join(INPUT_DATA_DIR, name),
                "s3": f"s3://{S3_BUCKET_NAME}/{name}",
            }
    else:
        logger.info(f"Scanning S3 bucket for datasets: {S3_BUCKET_NAME}")
        fs = fsspec.filesystem("s3", **_s3_storage_options())
        entries = fs.ls(S3_BUCKET_NAME)

        for path in entries:
            if not path.endswith(".zarr"):
                continue
            name = path.rsplit("/", 1)[-1][:-5]  # strip .zarr
            parts = name.split("_")
            if len(parts) != 4:
                continue
            variable, level, dataset, region_set = parts

            local_path = (
                os.path.join(INPUT_DATA_DIR, f"{name}.zarr") if INPUT_DATA_DIR else None
            )
            s3_path = f"s3://{path}"

            mapping[(variable, level, dataset, region_set)] = {
                "local": local_path,
                "s3": s3_path,
            }

    logger.info(f"Built dataset mapping with {len(mapping)} entries")
    return mapping


@log_execution_time
def _open_zarr_local(path: str) -> xr.Dataset:
    """
    Open a Zarr dataset from local storage.

    Parameters
    ----------
    path : str
        The local file path to the Zarr dataset.

    Returns
    -------
    xr.Dataset
        The loaded xarray Dataset.

    Raises
    ------
    FileNotFoundError
        If the specified local path does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError
    ds = xr.open_dataset(
        path,
        engine="zarr",
        chunks="auto",
        decode_timedelta=True,
        backend_kwargs={"consolidated": True},
    )
    return ds


@lru_cache(maxsize=None)
@log_execution_time
def _open_zarr_s3(zarr_uri: str) -> xr.Dataset:
    """
    Open a Zarr dataset from S3 storage.

    Parameters
    ----------
    zarr_uri : str
        The S3 URI (s3://...) to the Zarr dataset.

    Returns
    -------
    xr.Dataset
        The loaded xarray Dataset.

    Raises
    ------
    AssertionError
        If the URI does not start with "s3://".
    """
    assert zarr_uri.startswith("s3://"), f"Expected s3:// URI, got: {zarr_uri}"
    ds = xr.open_dataset(
        zarr_uri,
        engine="zarr",
        chunks="auto",
        decode_timedelta=True,
        backend_kwargs={"consolidated": True},
        storage_options=_s3_storage_options(),
    )
    return ds


@log_execution_time
def get_datasets(params: RequestParams) -> Union[xr.Dataset, list[xr.Dataset]]:
    """
    Retrieve xarray Dataset(s) based on request parameters.

    This function attempts to load the dataset for each requested variable
    from local storage first, falling back to S3. It returns a single Dataset
    if only one variable is requested, or a list of Datasets for multiple variables.

    Parameters
    ----------
    params : RequestParams
        The parameters containing variable(s), dataset, and region_set info.

    Returns
    -------
    Union[xr.Dataset, list[xr.Dataset]]
        The loaded xarray Dataset(s).

    Raises
    ------
    ValueError
        If required parameters are missing or if no datasets are found.
    """
    required = ["dataset", "region_set"]
    for f in required:
        if not hasattr(params, f):
            raise ValueError(f"Missing required parameter '{f}' in request model.")

    dataset_name = getattr(params, "dataset")
    region_set = getattr(params, "region_set")

    mapping = _build_dataset_mapping()

    # Determine which variables to load
    raw_variable = getattr(params, "variable", None)

    if raw_variable:
        # Support semicolon-separated list or single value
        if ";" in raw_variable:
            variables_to_load = [
                v.strip() for v in raw_variable.split(";") if v.strip()
            ]
        else:
            variables_to_load = [raw_variable.strip()]
    else:
        # If no variable is requested, try to load all defined available variables
        # filtered by what's actually present in the mapping for this dataset/region_set
        available_in_mapping = {
            f"{var}_{lev}"
            for (var, lev, d, rs) in mapping.keys()
            if d == dataset_name and rs == region_set
        }
        variables_to_load = [
            v for v in ALL_AVAILABLE_VARIABLES if v in available_in_mapping
        ]

        # If none of the defined available variables are found,
        # fallback to anything found in mapping
        if not variables_to_load:
            variables_to_load = list(available_in_mapping)

    if not variables_to_load:
        logger.error(
            f"No variables found for dataset={dataset_name}, region_set={region_set}"
        )
        raise ValueError(
            f"No variables found for dataset={dataset_name}, region_set={region_set}"
        )

    datasets = []
    for combined_variable in variables_to_load:
        if "_" not in combined_variable:
            logger.info(
                f"Variable '{combined_variable}' does not have a level: giving None"
            )
            varname, level = combined_variable, "None"
        else:
            varname, level = combined_variable.rsplit("_", 1)

        try:
            paths = mapping[(varname, level, dataset_name, region_set)]
            ds = None

            # Try local loading first if local path exists
            if paths.get("local"):
                try:
                    logger.info(
                        f"Loading local dataset for {combined_variable} "
                        f"from {paths['local']}"
                    )
                    ds = _open_zarr_local(paths["local"])
                except Exception as e:
                    logger.debug(
                        f"Local open failed for {combined_variable}: {e}. Trying S3..."
                    )

            # Fallback to S3 if local failed or was not available
            if ds is None and paths.get("s3"):
                ds = _open_zarr_s3(paths["s3"])

            if ds is None:
                logger.error(f"Failed to load dataset for {combined_variable}")
                continue

            if varname in ds.data_vars:
                # Transform sfcWind from m/s to km/h
                if varname == "sfcWind":
                    ds[varname] = ds[varname] * 3.6
                    ds[varname].attrs["units"] = "km/h"
                ds = ds.rename({varname: combined_variable})
                logger.debug(f"Renamed variable '{varname}' to '{combined_variable}'")

            datasets.append(ds)
        except KeyError:
            logger.warning(f"Dataset not found for variable={varname}, level={level}")
            continue
        except Exception as e:
            logger.error(f"Failed to load variable {combined_variable}: {e}")
            continue

    if not datasets:
        raise ValueError(
            f"Failed to load any variables for {dataset_name}/{region_set}"
        )

    logger.info(f"Loaded {len(datasets)} datasets for {dataset_name}/{region_set}")

    return datasets
