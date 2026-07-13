from sqlalchemy.orm import Session

from app.models import Log


def save_log(db: Session, fields: dict) -> None:
    log = Log(
        service=fields["service"],
        level=fields["level"],
        message=fields["message"],
        timestamp=fields["timestamp"],
        request_id=fields["request_id"],
        user_id=fields["user_id"],
        log_metadata=fields["metadata"],
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log
