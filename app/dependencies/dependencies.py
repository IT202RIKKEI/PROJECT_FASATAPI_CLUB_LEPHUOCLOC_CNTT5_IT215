from typing import Any
import jwt
import uuid
from fastapi import Depends, HTTPException, status, dependencies, Request
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

    def __call__(self, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):

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

    def __call__(self,
                 req: Request,
                 current_user: UserModel = Depends(get_current_user),
                 db: Session = Depends(get_db)):

        # lấy club_id từ path parameter
        club_id_str = req.path_params.get("club_id")
        if not club_id_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không tìm thấy club_id trên đường dẫn!",
            )

        # chuyển thành dạng uuid, để so sánh với database lấy ra chính xác club của ng dùng hiện tại
        club_uuid = uuid.UUID(club_id_str)

        club_member = db.query(ClubMemberModel).filter(
            ClubMemberModel.user_id == current_user.id,
            ClubMemberModel.club_id == club_uuid  # Lọc chính xác cb của ng dùng hiện tại
        ).first()

        if not club_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn chưa tham gia vào câu lạc bộ này!",
            )

        current_role_in_club = db.query(ClubRoleModel).filter(
            ClubRoleModel.id == club_member.role_id).first()

        if not current_role_in_club or current_role_in_club.name.lower() not in self.allowed_lists:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bạn không có quyền hạn để truy cập chức năng này"
            )

        return current_user
