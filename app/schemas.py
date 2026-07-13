from datetime import datetime

from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    service: str
    level: str
    message: str
    timestamp: datetime
    request_id: str
    user_id: str
    metadata: dict = Field(default_factory=dict)
