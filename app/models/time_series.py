"""Time series response models."""

from pydantic import BaseModel


class TimeSeries(BaseModel):
    """
    Model for time series data.

    This model represents a sequence of values over time for a given
    variable and region.

    Attributes
    ----------
    date : list[str]
        List of dates in the time series.
    value : dict[str, list[float]]
        Dictionary of values corresponding to each date.
    """

    date: list[str]
    value: dict[str, list[float]]
