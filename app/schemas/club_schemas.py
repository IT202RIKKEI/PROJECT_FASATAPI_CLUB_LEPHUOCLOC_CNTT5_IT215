import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ==========================================
# 3. CLUB SCHEMAS
# ==========================================
class ClubBase(BaseModel):
    name: str
    description: str | None = None


class ClubCreate(ClubBase):
    created_at: datetime
    # owner_id: uuid.UUID


class ClubUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    owner_id: uuid.UUID | None = None


class ClubResponse(ClubBase):
    id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
