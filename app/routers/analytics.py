from fastapi import APIRouter

from app.core.database import get_db
from app.services.analytics_service import (
    get_error_rate,
    get_hourly_errors,
    get_log_levels,
    get_logs_hourly,
    get_services,
    get_summary,
    get_top_services,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/levels")
async def level_statistics():
    with get_db() as db:
        return get_log_levels(db)


@router.get("/services")
async def service_statistics():
    with get_db() as db:
        return get_services(db)


@router.get("/errors/hourly")
async def hourly_error_statistics():
    with get_db() as db:
        return get_hourly_errors(db)


@router.get("/summary")
async def summary():
    with get_db() as db:
        return get_summary(db)


@router.get("/error-rate")
async def error_rate():
    with get_db() as db:
        return get_error_rate(db)


@router.get("/top-services")
async def top_services(limit: int = 5):
    with get_db() as db:
        return get_top_services(db, limit)


@router.get("/logs/hourly")
async def logs_hourly():
    with get_db() as db:
        return get_logs_hourly(db)
