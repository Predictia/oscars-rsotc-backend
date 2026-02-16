"""Annual cycle response models."""

from pydantic import BaseModel


class AnnualCycle(BaseModel):
    """
    Model for annual cycle data.

    This model represents the statistical distribution of values over an
    annual cycle, including percentiles and extremes.

    Attributes
    ----------
    date : list[str]
        List of dates (typically months).
    value : list[float]
        The mean or representative value for each date.
    percentile90 : list[float]
        The 90th percentile value.
    median : list[float]
        The median value.
    percentile10 : list[float]
        The 10th percentile value.
    min : list[float]
        The minimum value.
    max : list[float]
        The maximum value.
    higher_than_max : list[float]
        Values exceeding the historical maximum.
    lower_than_min : list[float]
        Values falling below the historical minimum.
    """

    date: list[str]
    value: list[float]
    percentile90: list[float]
    median: list[float]
    percentile10: list[float]
    min: list[float]
    max: list[float]
    higher_than_max: list[float]
    lower_than_min: list[float]
