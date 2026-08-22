from typing import List, Optional
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


# ==========================================
# 1. BẢNG SYSTEM_ROLES
# ==========================================
class SystemRoleModel(Base):
    __tablename__ = "system_roles"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False  # Ví dụ: "USER", "ADMIN"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    # 🔗 Quan hệ 1-N: Một system role có thể gán cho nhiều User
    users = relationship(
        "UserModel", back_populates="system_role"
    )


# ==========================================
# 2. BẢNG CLUB_ROLES
# ==========================================
class ClubRoleModel(Base):
    __tablename__ = "club_roles"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False  # Ví dụ: "OWNER", "MEMBER"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    # 🔗 Quan hệ 1-N: Một club role có thể gán cho nhiều thành viên trong các CLB
    club_members = relationship(
        "ClubMemberModel", back_populates="club_role"
    )
