import enum
import uuid
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, Text, Uuid, Enum, JSON
from sqlalchemy.orm import mapped_column, Mapped, joinedload, relationship
from datetime import datetime, timezone, timedelta
from app.db.database import Base


# ==========================================
# 1. ENUM ĐỊNH NGHĨA TRẠNG THÁI & ĐỘ ƯU TIÊN
# ==========================================
class ActivityStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class ActivityPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# ==========================================
# 2. MODEL CLUB_ACTIVITIES
# ==========================================
class ClubActivityModel(Base):
    __tablename__ = "club_activities"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 🏢 Thuộc CLB nào (bắt buộc, xóa CLB thì xóa hoạt động)
    club_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False
    )

    # 👤 Người được giao (có thể NULL nếu chưa phân công, xóa User thì set NULL)
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # ⚙️ Trạng thái và Độ ưu tiên
    status: Mapped[ActivityStatus] = mapped_column(
        Enum(ActivityStatus), default=ActivityStatus.TODO, nullable=False
    )
    priority: Mapped[ActivityPriority] = mapped_column(
        Enum(ActivityPriority), default=ActivityPriority.MEDIUM, nullable=False
    )

    # Thời gian
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )

    # nâng cao
    comments = mapped_column(JSON, default=list)
    attachments = mapped_column(JSON, default=list)

    # Quan hệ
    club = relationship(
        "ClubModel", back_populates="activities")
    assignee = relationship(
        "UserModel", back_populates="assigned_activities")
