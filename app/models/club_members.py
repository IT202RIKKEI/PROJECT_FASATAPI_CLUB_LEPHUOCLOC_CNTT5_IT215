import uuid
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, Text, Uuid
from sqlalchemy.orm import mapped_column, Mapped, joinedload, relationship
from datetime import datetime, timezone
from app.db.database import Base


class ClubMemberModel(Base):

    __tablename__ = "club_members"

    club_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("clubs.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("club_roles.id"), nullable=False)

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    club_role = relationship("ClubRoleModel", back_populates="club_members")

    # MQH trỏ ngược về user và club
    user = relationship("UserModel", back_populates="clubs_joined")
    club = relationship("ClubModel", back_populates="members")
