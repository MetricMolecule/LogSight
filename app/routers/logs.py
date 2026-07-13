import json

from fastapi import APIRouter, status

from app.core.redis import redis
from app.schemas import LogEntry

router = APIRouter(
    prefix="/logs",
    tags=["Logs"],
)

STREAM_NAME = "logs"


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def ingest_log(log: LogEntry):

    payload = log.model_dump(mode="json")

    payload["metadata"] = json.dumps(payload["metadata"])

    await redis.xadd(
        STREAM_NAME,
        payload,
    )

    return {"status": "accepted"}
