from fastapi import APIRouter, status, Depends, Request, HTTPException, dependencies
from app.dependencies.dependencies import get_current_user
from app.models.club import ClubModel
from app.schemas.club_schemas import *
from app.models.user import UserModel
from app.utils.utils import create_response
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.dependencies.dependencies import ClubRoleChecker, RoleSystemChecker
from app.services.club import *

# tính năng bắt buộc đăng nhập tài khoản
isLoginRequired = RoleSystemChecker(["admin", "user"])

club_router = APIRouter(
    prefix="/clubs",
    tags=["QUẢN LÝ CÂU LẠC BỘ"]
)


OWNER_ONLY = ClubRoleChecker(["owner"])

# =============================== TẠO CÂU LẠC BỘ MỚI ===============================


@club_router.post("/", status_code=status.HTTP_201_CREATED,
                  dependencies=[Depends(isLoginRequired)])
def new_club(req: Request,
             club_inp: ClubCreate,
             db: Session = Depends(get_db),
             current_user: UserModel = Depends(get_current_user)):

    try:

        club_data = new_clubs_sv(club_inp, db, current_user)

        safety_club_data = ClubResponse.model_validate(
            club_data).model_dump(mode='json')

        return create_response(status.HTTP_201_CREATED, "Tạo câu lạc bộ mới thành công", req, data=safety_club_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi: {e}"
        )
# =============================== END REGION ===============================


# =============================== Xem danh sách câu lạc bộ ===============================
@club_router.get("/", status_code=status.HTTP_200_OK, dependencies=[Depends(isLoginRequired)])
def get_clubs(req: Request,
              club_name: str | None = None,
              current_user: UserModel = Depends(get_current_user),
              db: Session = Depends(get_db)):

    try:
        list_clubs = get_clubs_sv(club_name, current_user, db)

        list_safety_clubs = [ClubResponse.model_validate(
            club).model_dump(mode="json") for club in list_clubs]

        return create_response(status.HTTP_201_CREATED, "Lấy dữ liệu câu lạc bộ thành công", req, data=list_safety_clubs)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi: {e}"
        )
# =============================== END REGION ===============================


# =============================== Xem chi tiết câu lạc bộ, chỉ thành viên mới xem được ===============================
@club_router.get("/{id}", status_code=status.HTTP_200_OK, dependencies=[Depends(isLoginRequired)])
def get_club_detail(req: Request,
                    id: uuid.UUID,
                    current_user: UserModel = Depends(get_current_user),
                    db: Session = Depends(get_db)):

    try:

        club_data = get_club_detail_sv(id, current_user, db)

        safety_club_data = ClubResponse.model_validate(
            club_data).model_dump(mode="json")

        return create_response(status.HTTP_201_CREATED, "Lấy dữ liệu câu lạc bộ thành công", req, data=safety_club_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi: {e}"
        )
# =============================== END REGION ===============================


# ======================================================================
# =============================== CHỨC NĂNG CỦA ADMIN ===============================
# ======================================================================

# =============================== CẬP NHẬT CÂU LẠC BỘ TẤT CẢ THUỘC TÍNH (OWNER_ONLY) ===============================
@club_router.put("/{club_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(isLoginRequired), Depends(OWNER_ONLY)])
def put_update_club(req: Request,
                    club_id: uuid.UUID,
                    update_data: ClubPutUpdate,
                    current_user: UserModel = Depends(get_current_user),
                    db: Session = Depends(get_db)):

    try:

        new_club_data = put_update_club_sv(
            update_data, club_id, current_user, db)

        safety_club_data = ClubResponse.model_validate(
            new_club_data).model_dump(mode="json")

        return create_response(status.HTTP_201_CREATED, "Cập nhật câu lạc bộ thành công", req, data=safety_club_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi: {e}"
        )
# =============================== END REGION ===============================


# =============================== CẬP NHẬT CÂU LẠC BỘ TÙY CHỌN THUỘC TÍNH (OWNER_ONLY) ===============================
@club_router.patch("/{club_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(isLoginRequired), Depends(OWNER_ONLY)])
def patch_update_club(req: Request,
                      club_id: uuid.UUID,
                      update_data: ClubPatchUpdate,
                      current_user: UserModel = Depends(get_current_user),
                      db: Session = Depends(get_db)):

    try:

        new_club_data = patch_update_club_sv(
            update_data, club_id, current_user, db)

        safety_club_data = ClubResponse.model_validate(
            new_club_data).model_dump(mode="json")

        return create_response(status.HTTP_201_CREATED, "Cập nhật câu lạc bộ thành công", req, data=safety_club_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi: {e}"
        )
# =============================== END REGION ===============================
