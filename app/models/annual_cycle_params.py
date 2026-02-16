"""Annual cycle request parameter models."""
from typing import Optional

from pydantic import BaseModel


class AnnualCycleParams(BaseModel, extra="ignore"):
    """
    Parameters for annual cycle calculation requests.

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
    period : Optional[str]
        The period of interest (default is '2024-2024').
    reference_period : Optional[str]
        The reference period for climatology (default is '1940-2023').
    """

    dataset: str
    region_set: str
    region_name: str
    variable: str
    resample_freq: Optional[str] = "MS"
    period: Optional[str] = "2024-2024"
    reference_period: Optional[str] = "1940-2023"
