from sqlalchemy import asc, desc, func, select

from app.models import Log


def save_log(db, log_data: dict):
    log = Log(
        service=log_data["service"],
        level=log_data["level"],
        message=log_data["message"],
        timestamp=log_data["timestamp"],
        request_id=log_data["request_id"],
        user_id=log_data["user_id"],
        log_metadata=log_data["metadata"],
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


def get_logs(
    db,
    service=None,
    level=None,
    page=1,
    limit=20,
    sort="desc",
    start_time=None,
    end_time=None,
):
    stmt = select(Log)
    count_stmt = select(func.count()).select_from(Log)

    filters = []

    if service:
        filters.append(Log.service == service)

    if level:
        filters.append(Log.level == level)

    if start_time:
        filters.append(Log.timestamp >= start_time)

    if end_time:
        filters.append(Log.timestamp <= end_time)

    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)

    if sort == "asc":
        stmt = stmt.order_by(asc(Log.timestamp))
    else:
        stmt = stmt.order_by(desc(Log.timestamp))

    offset = (page - 1) * limit

    stmt = stmt.offset(offset).limit(limit)

    logs = db.execute(stmt).scalars().all()

    total = db.execute(count_stmt).scalar_one()

    return logs, total
