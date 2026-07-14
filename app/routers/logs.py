import json
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, status

from app.core.database import get_db
from app.core.redis import redis
from app.schemas import LogCreate, LogsResponse
from app.services.log_service import get_logs

router = APIRouter(
    prefix="/logs",
    tags=["Logs"],
)

STREAM_NAME = "logs"


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def ingest_log(log: LogCreate):

    payload = log.model_dump(mode="json")

    payload["metadata"] = json.dumps(payload["metadata"])

    await redis.xadd(
        STREAM_NAME,
        payload,
    )

    return {"status": "accepted"}


@router.get(
    "",
    response_model=LogsResponse,
)
async def get_logs_endpoint(
    service: str | None = None,
    level: str | None = None,
    page: int = 1,
    limit: int = 20,
    sort: Literal["asc", "desc"] = "desc",
    start_time: datetime | None = None,
    end_time: datetime | None = None,
):
    with get_db() as db:
        logs, total = get_logs(
            db=db,
            service=service,
            level=level,
            page=page,
            limit=limit,
            sort=sort,
            start_time=start_time,
            end_time=end_time,
        )

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "logs": logs,
    }
