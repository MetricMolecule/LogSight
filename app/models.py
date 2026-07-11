from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Log(BaseModel):
    service: str = Field(..., description="Service generating the log")
    level: LogLevel = Field(..., description="Severity level")
    message: str = Field(..., description="Log message")

    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Time the log was created"
    )

    request_id: str | None = Field(
        default=None, description="Unique request identifier"
    )

    user_id: str | None = Field(
        default=None, description="User associated with the request"
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional log metadata"
    )
