from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LogCreate(BaseModel):
    service: str
    level: str
    message: str
    timestamp: datetime
    request_id: str
    user_id: str
    metadata: dict = Field(default_factory=dict)


class LogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service: str
    level: str
    message: str
    timestamp: datetime
    request_id: str
    user_id: str
    log_metadata: Any


class LogsResponse(BaseModel):
    page: int
    limit: int
    total: int
    logs: list[LogResponse]
