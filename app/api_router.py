"""
API router module.

This module aggregates all individual routers (time series, climatology map,
annual cycle, etc.) into a single API router for inclusion in the main app.
"""

from fastapi import APIRouter

from app.routers.annual_cycle import router as annual_cycle_router
from app.routers.climatology_map import router as climatology_map_router
from app.routers.extreme_values import router as extreme_values_router
from app.routers.histograms import router as histograms_router
from app.routers.summary_stats import router as summary_stats_router
from app.routers.time_series import router as time_series_router

api_router = APIRouter()
api_router.include_router(time_series_router)
api_router.include_router(climatology_map_router)
api_router.include_router(annual_cycle_router)
api_router.include_router(extreme_values_router)
api_router.include_router(histograms_router)
api_router.include_router(summary_stats_router)
