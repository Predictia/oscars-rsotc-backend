"""Histograms response models."""

from pydantic import BaseModel


class Histograms(BaseModel):
    """
    Model for histogram data.

    This model represents the distribution of climate values for a period
    of interest compared to a reference period.

    Attributes
    ----------
    bins : list[float]
        The bin edges for the histogram.
    value_period : list[float]
        The histogram values for the period of interest.
    value_reference : list[float]
        The histogram values for the reference period.
    max_value_period : list[float]
        The maximum values during the period of interest.
    max_value_reference : list[float]
        The maximum values during the reference period.
    max_date_period : list[str]
        The dates of maximum values during the period of interest.
    max_date_reference : list[str]
        The dates of maximum values during the reference period.
    """

    bins: list[float]
    value_period: list[float]
    value_reference: list[float]
    max_value_period: list[float]
    max_value_reference: list[float]
    max_date_period: list[str]
    max_date_reference: list[str]
