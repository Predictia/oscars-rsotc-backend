"""Extreme values response models."""

from pydantic import BaseModel


class ExtremeValues(BaseModel):
    """
    Model for extreme climate values.

    This model represents the minimum and maximum values found in a dataset
    for a given period and region.

    Attributes
    ----------
    date_min : list[str]
        List of dates when minimum values occurred.
    value_min : list[float]
        List of minimum values.
    date_max : list[str]
        List of dates when maximum values occurred.
    value_max : list[float]
        List of maximum values.
    """

    date_min: list[str]
    value_min: list[float]
    date_max: list[str]
    value_max: list[float]
