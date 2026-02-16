"""Summary text request parameter models."""
from pydantic import BaseModel


class SummaryStatsParams(BaseModel, extra="ignore"):
    """
    Parameters for summary text generation requests.

    Attributes
    ----------
    dataset : str
        The name of the dataset.
    region_set : str
        The region set identifier.
    region_name : str
        The specific region name.
    period : str
        The period range (e.g., '2025-2025').
    season_filter : str
        The season range (e.g., '01-12').
    """

    dataset: str = "ERA5"
    region_set: str = "NUTS-0"
    region_name: str
    period: str = "2024-2024"
    season_filter: str = "01-12"
