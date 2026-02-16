"""Histograms request parameter models."""
from typing import Optional

from pydantic import BaseModel


class HistogramsParams(BaseModel, extra="ignore"):
    """
    Parameters for histogram calculation requests.

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
    period : Optional[str]
        The period of interest (default is 'all').
    reference_period : Optional[str]
        The reference period for comparison (default is '1950-1990').
    season_filter : Optional[str]
        Month range for seasonal filtering (default is '01-12').
    """

    dataset: str
    region_set: str
    region_name: str
    variable: str
    period: Optional[str] = "all"
    reference_period: Optional[str] = "1950-1990"
    season_filter: Optional[str] = "01-12"
