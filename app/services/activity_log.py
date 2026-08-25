import uuid
from sqlalchemy.orm import Session
from app.models.activity_log import ActivityLogModel


def log_activity(
    db: Session,
    user_id: uuid.UUID,
    action: str,
    description: str,
    club_id: uuid.UUID | None = None,
):
    log_entry = ActivityLogModel(
        user_id=user_id,
        club_id=club_id,
        action=action,
        description=description,
    )
    db.add(log_entry)


def get_club_activity_logs_sv(club_id: uuid.UUID, db: Session):
    return (
        db.query(ActivityLogModel)
        .filter(ActivityLogModel.club_id == club_id)
        .order_by(ActivityLogModel.created_at.desc())
        .all()
    )