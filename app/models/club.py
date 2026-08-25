import uuid
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, Text, Uuid
from sqlalchemy.orm import mapped_column, Mapped, joinedload, relationship
from datetime import datetime, timezone
from app.db.database import Base


class ClubModel(Base):

    __tablename__ = "clubs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True)
    name: Mapped[str] = mapped_column(
        String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # soft delete
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Khóa ngoại liên kết tới bảng role
    owner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False)

    # mối quan N - 1 Voi Users, 1 clb chỉ có 1 chủ
    owner = relationship("UserModel", back_populates="clubs_owned")

    # Quan hệ 1-N tới bảng trung gian: Danh sách thành viên trong CLB
    members = relationship(
        "ClubMemberModel", back_populates="club",
        cascade="all, delete-orphan"
    )

    # mqh nguojc với activity 1 club có nhiều hoạt động
    activities = relationship("ClubActivityModel", back_populates="club")
