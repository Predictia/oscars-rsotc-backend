"""Climatology map request parameter models."""
from typing import Optional

from pydantic import BaseModel


class ClimatologyMapParams(BaseModel, extra="ignore"):
    """
    Parameters for climatology map calculation requests.

    Attributes
    ----------
    dataset : str
        The name of the dataset.
    region_set : str
        The region set identifier.
    region_name : str
        The specific region name.
    variable : str
        The climate variable (e.g., 'tas_None').
    resample_freq : Optional[str]
        The resampling frequency.
    resample_func : Optional[str]
        The function used for resampling (default is 'mean').
    period : Optional[str]
        The period of interest (default is 'all').
    season_filter : str
        Month range for seasonal filtering (default is '01-12').
    season_filter_func : Optional[str]
        Function used for seasonal filtering (default is 'mean').
    anomaly : Optional[bool]
        Whether to calculate anomalies (default is False).
    reference_period : Optional[str]
        The reference period for climatology.
    """

    dataset: str
    region_set: str
    region_name: str
    variable: str
    resample_freq: Optional[str] = None
    resample_func: Optional[str] = "mean"
    period: Optional[str] = "all"
    season_filter: str = "01-12"
    season_filter_func: Optional[str] = "mean"
    anomaly: Optional[bool] = False
    reference_period: Optional[str] = None
