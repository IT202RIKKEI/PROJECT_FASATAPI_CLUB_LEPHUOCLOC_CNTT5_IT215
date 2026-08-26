from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserResponse, UserBase, UserCreate, UserUpdate
from app.schemas.enum_schemas import *
from app.models.user import *
from app.core.security import *
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from app.schemas.auth import *


# =============================== LOGIC ĐĂNG KÍ TÀI KHOẢN ===============================


def register_account_sv(user_inp: UserCreate, db: Session):

    exists_email = db.query(UserModel).filter(
        UserModel.email == user_inp.email).first()

    if exists_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email đã tồn tại trong hệ thống!",
        )

    # ỔN THÌ TẠO
    # user_dict = user_inp.model_dump(exclude={"password"})

    # password_hash = get_password_hash(user_inp.password)

    # user_dict["password_hash"] = password_hash
    # user_dict["role_id"] = "2"

    user_data = UserModel(**user_inp.model_dump(exclude={"password"}),
                          password_hash=get_password_hash(user_inp.password),
                          role_id=2)

    try:

        db.add(user_data)
        db.commit()
        db.refresh(user_data)

        return user_data

    except Exception as e:
        db.rollback()
        raise e

# =============================== END REGION ===============================


# =============================== LOGIC ĐĂNG NHẬP ===============================
def login_account_sv(email: str, password: str, db: Session):

    user = db.query(UserModel).filter(UserModel.email == email).first()

    #  Nếu không có user HOẶC sai mật khẩu
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,  
            detail="Email hoặc mật khẩu không chính xác!",
        )

    # Kiểm tra xem tài khoản có bị khóa không
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản của bạn đã bị khóa!",
        )
    # ổn thì tạo payload
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role_id": user.role_id
    }

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": "1800",
        "users": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": "ADMIN" if user.role_id == 1 else "USER"
        }
    }

# =============================== END REGION ===============================


# 2. Nghiệp vụ Refresh: Nhận Refresh Token -> Trả về Access Token MỚI
# =============================== REGION ===============================
def refresh_access_token_sv(refresh_token: str, db: Session) -> dict:

    try:
        # giải mã token
        payload = jwt.decode(refresh_token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])

        # chặn nếu ai cố tình quăng access token vào
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không đúng loại (yêu cầu Refresh Token)!",
            )

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token thiếu định danh người dùng!",
            )

        user_uuid = uuid.UUID(user_id_str)
        user = db.query(UserModel).filter(UserModel.id == user_uuid).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Người dùng không tồn tại hoặc đã bị khóa!",
            )

        # tạo access token mới với thời hạn 30p
        new_payload = {
            "sub": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role_id": user.role_id
        }

        new_access_token = create_access_token(new_payload)
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    except HTTPException:
        raise
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token đã hết hạn. Vui lòng đăng nhập lại!",
        )
    except (InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không hợp lệ hoặc bị giả mạo!",
        )


# =============================== END REGION ===============================
