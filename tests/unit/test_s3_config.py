from unittest.mock import patch

from app.load import _s3_storage_options


def test_s3_storage_options_includes_region():
    """Test that _s3_storage_options correctly includes S3_REGION."""
    with patch("app.load.S3_ACCESS_KEY", "test-key"), patch(
        "app.load.S3_SECRET_KEY", "test-secret"
    ), patch("app.load.S3_ENDPOINT_URL", "https://test-endpoint.com"), patch(
        "app.load.S3_REGION", "test-region"
    ):
        options = _s3_storage_options.__wrapped__()  # Bypass lru_cache for testing

        assert options["client_kwargs"]["region_name"] == "test-region"
        assert options["client_kwargs"]["endpoint_url"] == "https://test-endpoint.com"
        assert options["key"] == "test-key"
        assert options["secret"] == "test-secret"


def test_s3_storage_options_no_region():
    """
    Test that _s3_storage_options does not include region_name.

    Specifically when S3_REGION is None.
    """
    with patch("app.load.S3_ACCESS_KEY", "test-key"), patch(
        "app.load.S3_SECRET_KEY", "test-secret"
    ), patch("app.load.S3_ENDPOINT_URL", "https://test-endpoint.com"), patch(
        "app.load.S3_REGION", None
    ):
        options = _s3_storage_options.__wrapped__()  # Bypass lru_cache for testing

        assert "region_name" not in options["client_kwargs"]
        assert options["client_kwargs"]["endpoint_url"] == "https://test-endpoint.com"
