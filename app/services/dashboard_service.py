from sqlalchemy import func

from app.models import Log


def get_dashboard_stats(db):

    total_logs = db.query(func.count(Log.id)).scalar() or 0

    error_logs = db.query(func.count(Log.id)).filter(Log.level == "ERROR").scalar() or 0

    warning_logs = (
        db.query(func.count(Log.id)).filter(Log.level.in_(["WARN", "WARNING"])).scalar()
        or 0
    )

    services = db.query(func.count(func.distinct(Log.service))).scalar() or 0

    return {
        "total_logs": total_logs,
        "error_logs": error_logs,
        "warning_logs": warning_logs,
        "services": services,
    }


def get_log_levels(db):

    rows = (
        db.query(
            Log.level,
            func.count(Log.id),
        )
        .group_by(Log.level)
        .all()
    )

    return [
        {
            "level": level,
            "count": count,
        }
        for level, count in rows
    ]


def get_top_services(db):

    rows = (
        db.query(
            Log.service,
            func.count(Log.id),
        )
        .group_by(Log.service)
        .order_by(func.count(Log.id).desc())
        .limit(10)
        .all()
    )

    return [
        {
            "service": service,
            "count": count,
        }
        for service, count in rows
    ]


def get_logs_over_time(db):

    rows = (
        db.query(
            func.date_trunc(
                "hour",
                Log.timestamp,
            ),
            func.count(Log.id),
        )
        .group_by(
            func.date_trunc(
                "hour",
                Log.timestamp,
            )
        )
        .order_by(
            func.date_trunc(
                "hour",
                Log.timestamp,
            )
        )
        .all()
    )

    return [
        {
            "time": t.strftime("%H:%M"),
            "count": count,
        }
        for t, count in rows
    ]
