"""Summary text response models."""

from typing import Dict, Optional

from pydantic import BaseModel


class SummaryStatsItem(BaseModel):
    """Model for a single climate variable summary stats item."""

    variable: str
    id: str
    long_name: str
    unit: str
    value: Optional[float] = None
    anomalies: Dict[str, Optional[float]] = {}
    anomalies_as_perc: Dict[str, Optional[float]] = {}
    ref_means: Dict[str, Optional[float]] = {}
    ref_maxs: Dict[str, Optional[float]] = {}
    ref_mins: Dict[str, Optional[float]] = {}
    ref_percentiles: Dict[str, Dict[str, Optional[float]]] = {}
    trend: Optional[float] = None
    error: Optional[str] = None


class SummaryStats(BaseModel):
    """
    Model for summary stats data.

    Attributes
    ----------
    stats : Dict[str, SummaryStatsItem]
        The structured stats items.
    """

    stats: Dict[str, SummaryStatsItem]
