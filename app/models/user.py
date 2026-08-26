import uuid
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import mapped_column, Mapped, joinedload, relationship
from datetime import datetime, timezone
from app.db.database import Base


class UserModel(Base):

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )

    # Khóa ngoại liên kết tới bảng role
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("system_roles.id"), default=1)

    system_role = relationship("SystemRoleModel", back_populates="users")

    # mối quan hệ N-1 với club
    clubs_owned = relationship("ClubModel", back_populates="owner")

    # 👥 Quan hệ 1-N tới bảng trung gian: Danh sách các lần tham gia CLB
    clubs_joined = relationship(
        "ClubMemberModel", back_populates="user"
    )

    # mối quan hệ ngc với activity 1 người được giao nhiều Hoạt động
    assigned_activities = relationship(
        "ClubActivityModel", back_populates="assignee")
