from fastapi import APIRouter

from app.core.database import get_db
from app.services.dashboard_service import (
    get_dashboard_stats,
    get_log_levels,
    get_logs_over_time,
    get_top_services,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/stats")
async def stats():

    with get_db() as db:
        return get_dashboard_stats(db)


@router.get("/log-levels")
async def log_levels():

    with get_db() as db:
        return get_log_levels(db)


@router.get("/top-services")
async def top_services():

    with get_db() as db:
        return get_top_services(db)


@router.get("/logs-over-time")
async def logs_over_time():

    with get_db() as db:
        return get_logs_over_time(db)
