from starlette.testclient import TestClient

from app.app import app

client = TestClient(app)


def test_time_series_invalid_params():
    """
    Test that /api/time_series returns 422 for missing parameters.

    Verify that Unprocessable Entity is returned for missing required parameters.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    # Missing required 'dataset', 'variable', etc.
    response = client.post("/api/time_series", json={"dataset": "ERA5"})
    assert response.status_code == 422


def test_climatology_map_invalid_params():
    """
    Test that /api/climatology_map returns 422 for invalid parameters.

    Verify that Unprocessable Entity is returned for invalid parameters.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    # Missing required parameters
    response = client.post("/api/climatology_map", json={})
    assert response.status_code == 422


def test_annual_cycle_invalid_params():
    """
    Test that /api/annual_cycle returns 422 for missing parameters.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    response = client.post("/api/annual_cycle", json={"variable": "tas"})
    assert response.status_code == 422
