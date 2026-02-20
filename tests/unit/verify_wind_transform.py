import numpy as np
import pandas as pd
import xarray as xr

from app.models.summary_stats_params import SummaryStatsParams
from app.services.summary_stats import get_summary_stats


def test_sfcWind_transformation():
    # Create a dummy dataset with sfcWind in m/s
    data = np.array([10.0, 20.0, 30.0])
    times = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
    # The service expects internal_var names like sfcWind_None
    ds = xr.Dataset(
        {"sfcWind_None": (("time", "region"), data.reshape(-1, 1), {"units": "m/s"})},
        coords={"time": times, "region": ["Spain"]},
    )

    params = SummaryStatsParams(
        region_name="Spain",
        period="2024-2024",
        season_filter="01-12",
        dataset="dataset",
        region_set="region_set",
    )

    # Call the service which should apply ensure_float and transform_units
    result = get_summary_stats(ds, params)
    stats = result["stats"]

    # Check sfcWind_mean (one of the IDs generated for sfcWind)
    assert "sfcWind_mean" in stats
    sfc_stat = stats["sfcWind_mean"]

    # Check if values are multiplied by 3.6
    # The mean of [10, 20, 30] is 20. 20 * 3.6 = 72.0
    expected_value = 20.0 * 3.6
    assert sfc_stat["value"] == expected_value

    # Check if units are updated
    assert sfc_stat["unit"] == "km/h"


def test_other_variable_no_transformation():
    # Create a dummy dataset with another variable
    data = np.array([10.0, 20.0, 30.0])
    times = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
    ds = xr.Dataset(
        {"tas_None": (("time", "region"), data.reshape(-1, 1), {"units": "K"})},
        coords={"time": times, "region": ["Spain"]},
    )

    params = SummaryStatsParams(
        region_name="Spain",
        period="2024-2024",
        season_filter="01-12",
        dataset="dataset",
        region_set="region_set",
    )

    result = get_summary_stats(ds, params)
    stats = result["stats"]

    assert "tas" in stats
    tas_stat = stats["tas"]

    # Check if values are NOT changed
    # Mean of 10, 20, 30 is 20
    assert tas_stat["value"] == 20.0

    # Check if units are NOT updated (summary stats might use its own units map,
    # but let's see what the service does)
    # Actually, tas unit is °C in the fallback map of summary_stats service.
    # But it should take it from attrs if present.
    assert tas_stat["unit"] == "K"


if __name__ == "__main__":
    try:
        test_sfcWind_transformation()
        print("sfcWind transformation test PASSED")
        test_other_variable_no_transformation()
        print("Other variable test PASSED")
    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"Test FAILED: {e}")
        exit(1)
