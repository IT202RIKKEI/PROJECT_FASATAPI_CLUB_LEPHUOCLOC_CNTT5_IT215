from fastapi import APIRouter, HTTPException, Depends, status, Form, Request, dependencies, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.auth import *
from app.schemas.auth import *
from app.utils.utils import create_response
from app.schemas.response_schemas import BaseResponse
from app.dependencies.dependencies import get_current_user, RoleSystemChecker
from app.core.limiter import limiter

auth_router = APIRouter(
    prefix="/auth",
    tags=["QUẢN LÝ XÁC THỰC"]
)

# Cấu hình Role cho AMDIN
ADMIN_AUTH = RoleSystemChecker(["admin"])
USER_AUTH = RoleSystemChecker(["admin", "user"])

# =============================== ĐĂNG KÍ TÀI KHOẢN ===============================


@auth_router.post(
    "/register",
    response_model=BaseResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới",
    description="Tạo tài khoản người dùng mới trong hệ thống.",
)
def register_account(request: Request, user_inp: UserCreate = Form(...),
                     db: Session = Depends(get_db)):
    try:

        result = register_account_sv(user_inp, db)
        user_json = UserResponse.model_validate(result).model_dump(mode="json")

        # ổn thì trả về object
        return create_response(status_code=status.HTTP_201_CREATED,
                               message="Đăng kí tài khoản thành công",
                               request=request,
                               data=user_json)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi: {e}"
        )

# =============================== END REGION ===============================


# =============================== ĐĂNG NHẬP/ CẤP TOKEN ===============================
@auth_router.post(
    "/login",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập tài khoản",
    description="Xác thực người dùng qua email và mật khẩu, trả về Access Token và Refresh Token.",
)
@limiter.limit("5/minute")
def login_account(request: Request, email: str = Form(...),
                  password: str = Form(...),
                  db: Session = Depends(get_db)):

    try:

        result = login_account_sv(email, password, db)

        # ổn thì trả về object
        return create_response(status_code=status.HTTP_200_OK,
                               message="Đăng nhập thành công",
                               request=request,
                               data=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi: {e}"
        )

# =============================== END REGION ===============================


# =============================== REFRESH_TOKEN ===============================
@auth_router.post(
    "/Refresh_token",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Làm mới Access Token",
    description="Sử dụng Refresh Token hợp lệ để cấp lại Access Token mới.",
)
def Refresh_token(req: Request, payload: RefreshTokenRequest = Form(...), db: Session = Depends(get_db)):

    try:
        new_access_token = refresh_access_token_sv(payload.refresh_token, db)

        return create_response(
            status_code=status.HTTP_200_OK,
            message="Cấp lại Access Token mới thành công",
            request=req,
            data=new_access_token,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi: {e}"
        )
# =============================== END REGION ===============================
