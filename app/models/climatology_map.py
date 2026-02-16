"""Climatology map response models."""

from pydantic import BaseModel


class ClimatologyMap(BaseModel):
    """
    Model for climatology map data.

    This model represents average values across different regions for a given
    period and variable.

    Attributes
    ----------
    region : list[str]
        List of region identifiers.
    data : list[float]
        List of climatological values corresponding to each region.
    """

    region: list[str]
    data: list[float]
