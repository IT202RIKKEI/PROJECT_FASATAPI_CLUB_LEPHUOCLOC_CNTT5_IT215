import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ==========================================
# 4. CLUB MEMBER SCHEMAS
# ==========================================
class ClubMemberBase(BaseModel):
    role_id: int = 2  # Mặc định là MEMBER role id


class ClubMemberCreate(ClubMemberBase):
    user_id: uuid.UUID


class ClubMemberUpdate(BaseModel):
    role_id: int | None = None


class ClubMemberResponse(ClubMemberBase):
    club_id: uuid.UUID
    user_id: uuid.UUID
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)
