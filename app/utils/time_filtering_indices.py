"""Seasonal mapping utility for derived indices."""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

SEASON_TO_TIME_FILTER = {
    "01-12": "Annual",
    "01-01": "Jan",
    "02-02": "Feb",
    "03-03": "Mar",
    "04-04": "Apr",
    "05-05": "May",
    "06-06": "Jun",
    "07-07": "Jul",
    "08-08": "Aug",
    "09-09": "Sep",
    "10-10": "Oct",
    "11-11": "Nov",
    "12-12": "Dec",
    "12-02": "DecFeb",
    "03-05": "MarMay",
    "06-08": "JunAug",
    "09-11": "SepNov",
}


def get_time_filter_name(season: str) -> Optional[str]:
    """
    Map a season string (e.g., '01-12') to a time_filter name (e.g., 'Annual').

    Parameters
    ----------
    season : str
        The season string in 'MM-MM' format.

    Returns
    -------
    Optional[str]
        The corresponding time_filter name, or None if not found.
    """
    return SEASON_TO_TIME_FILTER.get(season)
