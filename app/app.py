"""
Main FastAPI application module.

This module initializes the FastAPI application, configures CORS middleware,
and includes the API router.
"""
import logging
import os

import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api_router import api_router

logger = logging.getLogger(__name__)

app = fastapi.FastAPI(
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Documentation path
# It should be relative to the app directory to work both locally and in Docker
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPHINX_DIR = os.path.join(BASE_DIR, "docs", "_build", "html")

if os.path.isdir(SPHINX_DIR):
    logger.info(f"Mounting Sphinx documentation from {SPHINX_DIR} at /api/sphinx")
    app.mount(
        "/api/sphinx",
        StaticFiles(directory=SPHINX_DIR, html=True),
        name="sphinx-docs",
    )
else:
    logger.warning(f"Sphinx documentation directory not found at {SPHINX_DIR}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    """
    Root endpoint to check backend status.

    Returns
    -------
    dict
        A dictionary containing the status of the backend.
    """
    return {"status": "Backend is running"}
