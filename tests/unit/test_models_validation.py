import pytest
from pydantic import ValidationError

from app.models.annual_cycle_params import AnnualCycleParams
from app.models.time_series_params import TimeseriesParams


def test_timeseries_params_validation():
    """
    Test validation and default values for TimeseriesParams.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    # Valid input
    params = TimeseriesParams(
        dataset="ERA5", region_set="NUTS-0", region_name="Spain", variable="tas"
    )
    assert params.dataset == "ERA5"
    assert params.resample_freq == "MS"  # Default value
    assert params.anomaly is False  # Default value

    # Missing required field
    with pytest.raises(ValidationError):
        TimeseriesParams(dataset="ERA5")


def test_annual_cycle_params_validation():
    """
    Test validation and default values for AnnualCycleParams.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    # Valid input
    params = AnnualCycleParams(
        dataset="ERA5", region_set="NUTS-0", region_name="Spain", variable="tas"
    )
    assert params.period == "2024-2024"  # Default
    assert params.reference_period == "1940-2023"  # Default

    # Invalid type for variable (though pydantic might coerce it)
    # Extra fields should be ignored as per config
    params_extra = AnnualCycleParams(
        dataset="ERA5",
        region_set="NUTS-0",
        region_name="Spain",
        variable="tas",
        extra_field="ignore_me",
    )
    assert not hasattr(params_extra, "extra_field")
