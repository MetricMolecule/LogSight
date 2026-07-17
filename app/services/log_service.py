from datetime import datetime

from sqlalchemy import asc, desc, func, select

from app.models import Log


def save_log(db, log: Log):
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def save_logs_bulk(db, logs: list[Log]):
    db.add_all(logs)
    db.commit()


def get_logs(
    db,
    service: str | None = None,
    level: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    page: int = 1,
    limit: int = 20,
    sort: str = "desc",
):
    stmt = select(Log)

    if service:
        stmt = stmt.where(Log.service == service)

    if level:
        stmt = stmt.where(Log.level == level)

    if start_time:
        stmt = stmt.where(Log.timestamp >= start_time)

    if end_time:
        stmt = stmt.where(Log.timestamp <= end_time)

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(total_stmt).scalar()

    if sort.lower() == "asc":
        stmt = stmt.order_by(asc(Log.timestamp))
    else:
        stmt = stmt.order_by(desc(Log.timestamp))

    stmt = stmt.offset((page - 1) * limit).limit(limit)

    logs = db.execute(stmt).scalars().all()

    return logs, total
