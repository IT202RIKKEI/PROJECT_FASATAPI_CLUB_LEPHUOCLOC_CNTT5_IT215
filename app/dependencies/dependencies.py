from typing import Any
import jwt
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from app.core.config import settings
from app.models.user import UserModel
from app.models.role import SystemRoleModel, ClubRoleModel
from app.models.club import ClubModel
from app.models.club_members import ClubMemberModel
from app.db.database import get_db, SessionLocal
from sqlalchemy.orm import Session


security = HTTPBearer()


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):

    token = creds.credentials

    try:

        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])

        # lấy ra user

        # ép sub lại thành kiểu uuid, để có thể so sánh

        user_uuid = uuid.UUID(payload["sub"])

        user = db.query(UserModel).filter(UserModel.id == user_uuid).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng này trong hệ thống",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản này đã bị khóa",
            )

        return user

    except ExpiredSignatureError:
        # Bắt lỗi khi token quá hạn
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token đã hết hạn. Vui lòng đăng nhập lại!",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InvalidTokenError:
        # Bắt lỗi khi token giả mạo, sai secret key hoặc sai định dạng
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ!",
            headers={"WWW-Authenticate": "Bearer"},
        )


class RoleSystemChecker:
    def __init__(self, allowed_lists: list[str]):
        self.allowed_lists = allowed_lists

    def __call__(self, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)) -> UserModel:

        role_id = current_user.role_id

        current_role = db.query(SystemRoleModel).filter(
            SystemRoleModel.id == role_id).first()

        if not current_role or current_role.name.lower() not in self.allowed_lists:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bạn không có quyền hạn để truy cập chức năng này"
            )

        return current_user


class ClubRoleChecker:

    def __init__(self, allowed_lists: list[str]):
        self.allowed_lists = allowed_lists

    def __call__(self, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)) -> UserModel:

        role_id = current_user.role_id

        current_role = db.query(ClubRoleModel).filter(
            ClubRoleModel.id == role_id).first()

        if not current_role or current_role.name.lower() in self.allowed_lists:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bạn không có quyền hạn để truy cập chức năng này"
            )

        return current_user
