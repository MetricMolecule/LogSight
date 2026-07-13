from datetime import datetime

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True)

    service: Mapped[str] = mapped_column(String(100), index=True)

    level: Mapped[str] = mapped_column(String(20), index=True)

    message: Mapped[str] = mapped_column(String)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True,
    )

    request_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    user_id: Mapped[str] = mapped_column(String(100))

    log_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSON,
    )
