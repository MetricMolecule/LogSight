from fastapi import APIRouter, status

from app.models import Log

router = APIRouter(
    prefix="/logs",
    tags=["Logs"],
)


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
)
async def ingest_log(log: Log):
    return {
        "status": "accepted",
        "log": log.model_dump(),
    }
