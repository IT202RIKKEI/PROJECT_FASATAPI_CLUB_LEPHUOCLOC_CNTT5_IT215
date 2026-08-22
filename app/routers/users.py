from fastapi import APIRouter, HTTPException, Depends, status, Form, Request, dependencies
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import *
from app.services.user import get_users_sv
from app.utils.utils import create_response
from app.dependencies.dependencies import get_current_user
from app.routers.auth import ADMIN_AUTH, USER_AUTH


user_router = APIRouter(
    prefix="/users",
    tags=["QUẢN LÝ NGƯỜI DÙNG"]
)


# =============================== LẤY RA THÔNG TIN NGƯỜI DÙNG ===============================
@user_router.get("/me", status_code=status.HTTP_200_OK, dependencies=[Depends(ADMIN_AUTH)])
def get_current_user(req: Request, user=Depends(get_current_user)):

    try:
        safety_user = UserResponse.model_validate(user).model_dump(mode="json")

        return create_response(status_code=status.HTTP_200_OK,
                               message="Xem thông tin cá nhân thành công",
                               request=req,
                               data=safety_user)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi: {e}"
        )
# =============================== END REGION ===============================


# =============================== LỌC RA DANH SÁCH NGƯỜI DÙNG CHO ADMIN ===============================
@user_router.get("/users", status_code=status.HTTP_200_OK, dependencies=[Depends(ADMIN_AUTH)])
def get_users(req: Request,
              full_name: str | None = None,
              email: str | None = None,
              status_in: bool | None = None,
              db: Session = Depends(get_db)):
    try:

        users_data = get_users_sv(db, full_name, email, status_in)

        # Chuẩn hóa list dữ liệu
        users_json = [UserResponse.model_validate(
            u).model_dump(mode="json") for u in users_data]

        return create_response(status_code=status.HTTP_200_OK,
                               message="Lấy dữ liệu người dùng thành công",
                               request=req,
                               data=users_json)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi: {e}"
        )

# =============================== END REGION ===============================
