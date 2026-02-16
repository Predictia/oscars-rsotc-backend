"""
Configuration module for the application.

This module loads environment variables and defines global configuration
constants used throughout the application, particularly for S3 access.
"""

import os

from dotenv import load_dotenv

load_dotenv()

S3_BUCKET_NAME = "oscars-rsotc-data"
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
