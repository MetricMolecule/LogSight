import csv
import io
import json
from datetime import datetime

from fastapi import APIRouter, Query, status
from fastapi.responses import StreamingResponse

from app.core.database import get_db
from app.core.redis import redis
from app.schemas import LogCreate, LogsResponse
from app.services.log_service import (
    get_logs,
    get_logs_for_export,
)

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
    search: str | None = None,
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    page: int = 1,
    limit: int = 20,
    sort: str = "desc",
):
    with get_db() as db:
        logs, total = get_logs(
            db=db,
            service=service,
            level=level,
            search=search,
            start_time=start_time,
            end_time=end_time,
            page=page,
            limit=limit,
            sort=sort,
        )

    return {
        "logs": logs,
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/export")
async def export_logs(
    service: str | None = None,
    level: str | None = None,
    search: str | None = None,
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    sort: str = "desc",
):
    with get_db() as db:
        logs = get_logs_for_export(
            db=db,
            service=service,
            level=level,
            search=search,
            start_time=start_time,
            end_time=end_time,
            sort=sort,
        )

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow(
        [
            "id",
            "timestamp",
            "service",
            "level",
            "message",
            "request_id",
            "user_id",
            "metadata",
        ]
    )

    for log in logs:
        writer.writerow(
            [
                log.id,
                log.timestamp.isoformat() if log.timestamp else "",
                log.service,
                log.level,
                log.message,
                log.request_id,
                log.user_id,
                json.dumps(
                    log.metadata,
                    default=str,
                ),
            ]
        )

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=logsight-logs.csv"},
    )
