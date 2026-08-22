import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.schemas.enum_schemas import *


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


# ==========================================
# 5. CLUB ACTIVITY SCHEMAS
# ==========================================
class ClubActivityBase(BaseModel):
    title: str
    description: str | None = None
    status: ActivityStatus = ActivityStatus.TODO
    priority: ActivityPriority = ActivityPriority.MEDIUM
    due_date: datetime | None = None
    assignee_id: uuid.UUID | None = None


class ClubActivityCreate(ClubActivityBase):
    pass


class ClubActivityUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: ActivityStatus | None = None
    priority: ActivityPriority | None = None
    due_date: datetime | None = None
    assignee_id: uuid.UUID | None = None


class ClubActivityResponse(ClubActivityBase):
    id: uuid.UUID
    club_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# AUTH SCHEMAS
class RefreshTokenRequest(BaseModel):
    refresh_token: str
