from fastapi import APIRouter

from app.models import Log

router = APIRouter()


@router.post("/logs")
async def ingest_log(log: Log):
    return {
        "status": "received",
        "log": log,
    }
