"""Time series request parameter models."""
from typing import Optional

from pydantic import BaseModel


class TimeseriesParams(BaseModel, extra="ignore"):
    """
    Parameters for time series calculation requests.

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
        The resampling frequency (default is 'M' for monthly).
    resample_func : Optional[str]
        The function used for resampling (default is 'mean').
    period : Optional[str]
        The period of interest (default is 'all').
    season_filter : Optional[str]
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
    resample_freq: Optional[str] = "MS"
    resample_func: Optional[str] = "mean"
    period: Optional[str] = "all"
    season_filter: Optional[str] = "01-12"
    season_filter_func: Optional[str] = "mean"
    anomaly: Optional[bool] = False
    reference_period: Optional[str] = None
