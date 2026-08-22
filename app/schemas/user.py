import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# ==========================================
# 2. USER SCHEMAS
# ==========================================


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True
    role_id: int = 1


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role_id: int = 1

    # validate dữ liệu
    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        cleaned_name = value.strip()

        if not cleaned_name:
            raise ValueError("Họ và tên không được để trống!")

        # duyệt từng kí tự để, kiểm tra xem có kí tự đặc biệt k, chỉ chấp nhận space và chữ cái
        for char in cleaned_name:

            if not char.isalpha() and not char.isspace():
                raise ValueError(
                    "Họ và tên chỉ được chứa chữ cái và khoảng trắng, không chứa số hay ký tự đặc biệt!")

        return cleaned_name

    # kiểm tra mật khẩu bằng any
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:

        # có ít nhất 1 chữ cái
        has_letter = any(char.isalpha() for char in value)

        # có ít nhất 1 kí tự đặc biệt
        has_special = any(char.isalnum() for char in value)

        if not has_letter or not has_special:
            raise ValueError(
                "Mật khẩu phải chứa ít nhất 1 chữ cái và 1 kí tự đặc biệt!")

        return value


class UserUpdate(BaseModel):
    full_name: str | None = None
    password: str | None = None
    is_active: bool | None = None
    role_id: int | None = None


class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
