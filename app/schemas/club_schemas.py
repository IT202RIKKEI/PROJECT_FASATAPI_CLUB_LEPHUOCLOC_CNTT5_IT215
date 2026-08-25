import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ==========================================
# 3. CLUB SCHEMAS
# ==========================================
class ClubBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Tên CLB từ 1 đến 255 ký tự",
    )
    description: str | None = Field(
        default=None, description="Mô tả CLB (không bắt buộc)"
    )

    @field_validator("name")
    @classmethod
    def validate_name_not_empty(cls, v: str) -> str:
        clean_name = v.strip()
        if not clean_name:
            raise ValueError(
                "Tên câu lạc bộ không được chỉ chứa khoảng trắng!")
        return clean_name


# 1. Tạo mới: Kế thừa ClubBase, không cần truyền created_at từ body
class ClubCreate(ClubBase):
    pass


# 2. Cập nhật toàn bộ (PUT): Bắt buộc gửi name, description có thể None
class ClubPutUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name_not_empty(cls, v: str) -> str:
        clean_name = v.strip()
        if not clean_name:
            raise ValueError(
                "Tên câu lạc bộ không được chỉ chứa khoảng trắng!")
        return clean_name


# 3. Cập nhật một phần (PATCH): Tất cả đều là Optional
class ClubPatchUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name_not_empty(cls, v: str | None) -> str | None:
        if v is not None:
            clean_name = v.strip()
            if not clean_name:
                raise ValueError(
                    "Tên câu lạc bộ không được chỉ chứa khoảng trắng!"
                )
            return clean_name
        return v


# 4. Trả về cho Client
class ClubResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    owner_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
