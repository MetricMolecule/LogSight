from sqlalchemy import asc, desc, select

from app.models import Log


def save_log(db, log):
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def save_logs_bulk(db, logs):
    db.add_all(logs)
    db.commit()


def get_logs(
    db,
    service: str | None = None,
    level: str | None = None,
    page: int = 1,
    limit: int = 20,
    sort: str = "desc",
):
    stmt = select(Log)

    if service:
        stmt = stmt.where(Log.service == service)

    if level:
        stmt = stmt.where(Log.level == level)

    if sort == "asc":
        stmt = stmt.order_by(asc(Log.timestamp))
    else:
        stmt = stmt.order_by(desc(Log.timestamp))

    stmt = stmt.offset((page - 1) * limit)
    stmt = stmt.limit(limit)

    return db.execute(stmt).scalars().all()
