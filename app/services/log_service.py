from datetime import datetime

from sqlalchemy import asc, desc, func, or_, select

from app.models import Log


def save_log(db, log: Log):
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def save_logs_bulk(db, logs: list[Log]):
    db.add_all(logs)
    db.commit()


def build_logs_query(
    service: str | None = None,
    level: str | None = None,
    search: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    sort: str = "desc",
):
    stmt = select(Log)

    if service:
        stmt = stmt.where(Log.service == service)

    if level:
        stmt = stmt.where(Log.level == level)

    if search:
        search_pattern = f"%{search}%"

        stmt = stmt.where(
            or_(
                Log.message.ilike(search_pattern),
                Log.request_id.ilike(search_pattern),
                Log.user_id.ilike(search_pattern),
            )
        )

    if start_time:
        stmt = stmt.where(Log.timestamp >= start_time)

    if end_time:
        stmt = stmt.where(Log.timestamp <= end_time)

    if sort.lower() == "asc":
        stmt = stmt.order_by(asc(Log.timestamp))
    else:
        stmt = stmt.order_by(desc(Log.timestamp))

    return stmt


def get_logs(
    db,
    service: str | None = None,
    level: str | None = None,
    search: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    page: int = 1,
    limit: int = 20,
    sort: str = "desc",
):
    page = max(page, 1)
    limit = min(max(limit, 1), 100)

    base_stmt = build_logs_query(
        service=service,
        level=level,
        search=search,
        start_time=start_time,
        end_time=end_time,
        sort=sort,
    )

    total_stmt = select(func.count()).select_from(base_stmt.order_by(None).subquery())

    total = db.execute(total_stmt).scalar() or 0

    stmt = base_stmt.offset((page - 1) * limit).limit(limit)

    logs = db.execute(stmt).scalars().all()

    return logs, total


def get_logs_for_export(
    db,
    service: str | None = None,
    level: str | None = None,
    search: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    sort: str = "desc",
    limit: int = 50000,
):
    stmt = build_logs_query(
        service=service,
        level=level,
        search=search,
        start_time=start_time,
        end_time=end_time,
        sort=sort,
    )

    stmt = stmt.limit(limit)

    return db.execute(stmt).scalars().all()
