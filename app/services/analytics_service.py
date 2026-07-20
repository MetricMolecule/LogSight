from sqlalchemy import desc, func, select

from app.models import Log


def group_count(db, column):
    stmt = select(
        column,
        func.count(Log.id),
    ).group_by(column)

    rows = db.execute(stmt).all()

    return {value: count for value, count in rows}


def get_log_levels(db):
    return group_count(db, Log.level)


def get_services(db):
    return group_count(db, Log.service)


def get_hourly_errors(db):
    stmt = (
        select(
            func.date_trunc("hour", Log.timestamp).label("hour"),
            func.count(Log.id).label("count"),
        )
        .where(Log.level == "ERROR")
        .group_by(func.date_trunc("hour", Log.timestamp))
        .order_by(func.date_trunc("hour", Log.timestamp))
    )

    rows = db.execute(stmt).all()

    return [
        {
            "hour": hour.isoformat(),
            "count": count,
        }
        for hour, count in rows
    ]


def get_summary(db):
    total_logs = db.scalar(select(func.count(Log.id)))

    errors = db.scalar(select(func.count(Log.id)).where(Log.level == "ERROR"))

    warnings = db.scalar(select(func.count(Log.id)).where(Log.level == "WARN"))

    services = db.scalar(select(func.count(func.distinct(Log.service))))

    users = db.scalar(select(func.count(func.distinct(Log.user_id))))

    return {
        "total_logs": total_logs,
        "errors": errors,
        "warnings": warnings,
        "services": services,
        "users": users,
    }


def get_error_rate(db):
    total_logs = db.scalar(select(func.count(Log.id)))

    errors = db.scalar(select(func.count(Log.id)).where(Log.level == "ERROR"))

    rate = 0

    if total_logs:
        rate = round((errors / total_logs) * 100, 2)

    return {
        "error_rate": rate,
    }


def get_top_services(db, limit=5):
    stmt = (
        select(
            Log.service,
            func.count(Log.id).label("count"),
        )
        .group_by(Log.service)
        .order_by(desc("count"))
        .limit(limit)
    )

    rows = db.execute(stmt).all()

    return [
        {
            "service": service,
            "count": count,
        }
        for service, count in rows
    ]


def get_logs_hourly(db):
    stmt = (
        select(
            func.date_trunc("hour", Log.timestamp).label("hour"),
            func.count(Log.id).label("count"),
        )
        .group_by(func.date_trunc("hour", Log.timestamp))
        .order_by(func.date_trunc("hour", Log.timestamp))
    )

    rows = db.execute(stmt).all()

    return [
        {
            "hour": hour.isoformat(),
            "count": count,
        }
        for hour, count in rows
    ]
