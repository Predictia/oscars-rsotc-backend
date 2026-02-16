"""
Time filtering utility module.

This module provides the TemporalFiltering class for slicing and aggregating
climate data based on specific periods and seasonal filters.
"""
from calendar import monthrange
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy
import xarray

mapping_statistics = {
    "mean": numpy.mean,
    "max": numpy.max,
    "min": numpy.min,
    "std": numpy.std,
    "median": numpy.median,
    "sum": numpy.sum,
}

mapping_months = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


@dataclass
class TemporalFiltering:
    """
    A class for computing time filtering for a given period range and season.

    Attributes
    ----------
    dataset : xarray.Dataset
        The input dataset containing the data to be aggregated.
    period_range : str
        The period range to compute the climatology for,
        in the format 'start_year-end_year' or 'all'.
    time_filter : str
        The season to aggregate over, in the format 'start_month-end_month'.
    statistical : Optional[str]
        The statistical function to apply (mean, max, min, std, median, sum).
        Default is 'mean'.
    """

    dataset: xarray.Dataset
    period_range: str
    time_filter: str
    statistical: Optional[str] = "mean"

    def sel_time_filter(self):
        """
        Apply the time filter to the dataset.

        Returns
        -------
        xarray.Dataset
            The dataset filtered by the specified period and season.
        """
        # Parse the season string into start and end months
        start_month, end_month = self.time_filter.split("-")

        # Select the temporal range of interest
        if self.period_range == "all":
            period_range_start = numpy.datetime_as_string(
                self.dataset.time.values[0], unit="Y"
            )
            period_range_end = numpy.datetime_as_string(
                self.dataset.time.values[-1], unit="Y"
            )
        else:
            period_range_start, period_range_end = self.period_range.split("-")

        data_for_seasons = []

        for year in range(int(period_range_start), int(period_range_end) + 1):
            # Select the data for the current year and season
            if int(start_month) <= int(end_month):
                num_days = monthrange(year, int(end_month))
                season_range = slice(
                    f"{year}-{start_month}-01", f"{year}-{end_month}-{num_days[1]}"
                )
            else:
                num_days = monthrange(year, int(end_month))
                season_range = slice(
                    f"{year - 1}-{start_month}-01", f"{year}-{end_month}-{num_days[1]}"
                )

            data_for_season = self.dataset.sel(time=season_range)
            data_for_seasons.append(data_for_season)

        data_for_period = xarray.concat(data_for_seasons, dim="time")
        return data_for_period

    def compute(self) -> Tuple[xarray.Dataset, xarray.Dataset]:
        """
        Compute the climatology for the specified period range.

        Returns
        -------
        data_for_period : xarray.Dataset
            The data for the period range with the time_filter applied.
        yearly_data_for_period : xarray.Dataset
            The aggregated (e.g., mean) data for each year in the period range.
        """
        data_for_period = self.sel_time_filter()
        statistical_function = mapping_statistics[self.statistical]
        start_month = int(self.time_filter.split("-")[0])
        end_month = int(self.time_filter.split("-")[-1])
        time_agg_product = (
            data_for_period.sortby("time")
            .resample(time=f"YS-{mapping_months[start_month].upper()}")
            .reduce(statistical_function, "time")
        )

        if start_month > end_month:
            time_agg_product["time"] = (
                time_agg_product["time"].values.astype("datetime64[Y]")
                + numpy.timedelta64(1, "Y")
            ).astype("datetime64[ns]")

        yearly_data_for_period = (
            time_agg_product.sortby("time")
            .resample(time="YS")
            .reduce(mapping_statistics["mean"], "time")
        )
        return data_for_period, yearly_data_for_period
