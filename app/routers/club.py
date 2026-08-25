from fastapi import APIRouter, status, Depends, Request, HTTPException, dependencies, Form
from app.dependencies.dependencies import get_current_user
from app.models.club import ClubModel
from app.schemas.club_schemas import *
from app.schemas.clubmember_schemas import *
from app.models.user import UserModel
from app.utils.utils import create_response
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.dependencies.dependencies import ClubRoleChecker, RoleSystemChecker
from app.services.club import *
from app.schemas.activity_log_schemas import ActivityLogResponse
from app.services.activity_log import get_club_activity_logs_sv
from app.schemas.club_activity_schemas import *


# tính năng bắt buộc đăng nhập tài khoản
isLoginRequired = RoleSystemChecker(["admin", "user"])
OWNER_ONLY = ClubRoleChecker(["owner"])
FULL_ACCESS = ClubRoleChecker(["owner", "member"])


club_router = APIRouter(
    prefix="/clubs",
    tags=["QUẢN LÝ CÂU LẠC BỘ"]
)


# =============================== TẠO CÂU LẠC BỘ MỚI ===============================


@club_router.post("/", status_code=status.HTTP_201_CREATED,
                  dependencies=[Depends(isLoginRequired)])
def new_club(req: Request,
             club_inp: ClubCreate = Form(...),
             db: Session = Depends(get_db),
             current_user: UserModel = Depends(get_current_user)):

    try:

        club_data = new_clubs_sv(club_inp, db, current_user)

        safety_club_data = ClubResponse.model_validate(
            club_data).model_dump(mode='json')

        return create_response(status.HTTP_201_CREATED, "Tạo câu lạc bộ mới thành công", req, data=safety_club_data)

    except HTTPException:
        raise
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

        return create_response(status.HTTP_200_OK, "Lấy dữ liệu câu lạc bộ thành công", req, data=list_safety_clubs)

    except HTTPException:
        raise
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

        return create_response(status.HTTP_200_OK, "Lấy dữ liệu câu lạc bộ thành công", req, data=safety_club_data)

    except HTTPException:
        raise
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
                    update_data: ClubPutUpdate = Form(...),
                    current_user: UserModel = Depends(get_current_user),
                    db: Session = Depends(get_db)):

    try:

        new_club_data = put_update_club_sv(
            update_data, club_id, current_user, db)

        safety_club_data = ClubResponse.model_validate(
            new_club_data).model_dump(mode="json")

        return create_response(status.HTTP_201_CREATED, "Cập nhật câu lạc bộ thành công", req, data=safety_club_data)

    except HTTPException:
        raise
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
                      update_data: ClubPatchUpdate = Form(...),
                      current_user: UserModel = Depends(get_current_user),
                      db: Session = Depends(get_db)):

    try:

        new_club_data = patch_update_club_sv(
            update_data, club_id, current_user, db)

        safety_club_data = ClubResponse.model_validate(
            new_club_data).model_dump(mode="json")

        return create_response(status.HTTP_201_CREATED, "Cập nhật câu lạc bộ thành công", req, data=safety_club_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi: {e}"
        )
# =============================== END REGION ===============================


# =============================== XÓA CÂU LẠC BỘ (OWNER ONLY) ===============================
@club_router.delete("/{club_id}",
                    status_code=status.HTTP_200_OK,
                    dependencies=[Depends(isLoginRequired), Depends(OWNER_ONLY)])
def delete_club(req: Request, club_id: uuid.UUID, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):

    try:
        result = delete_club_sv(club_id, current_user, db)

        if result:
            return create_response(status.HTTP_201_CREATED, "Xóa câu lạc bộ thành công", req)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi: {e}"
        )
# =============================== END REGION ===============================

# ============================================================================================================================================
# ============================================================================================================================================
# =============================== QUẢN LÝ THÀNH VIÊN CÂU LẠC BỘ (CLUB_MEMBER, OWNER_ONLY) ===============================
# ============================================================================================================================================
# ============================================================================================================================================


# =============================== THÊM THÀNH VIÊN VÀO CLB (OWNER_ONLY) ===============================
@club_router.post("/{club_id}/members",
                  status_code=status.HTTP_201_CREATED,
                  dependencies=[Depends(isLoginRequired), Depends(OWNER_ONLY)])
def new_member(req: Request,
               club_id: uuid.UUID,
               member_data: ClubMemberCreate = Form(...),
               current_user: UserModel = Depends(get_current_user),
               db: Session = Depends(get_db)):

    try:

        return_data = new_member_sv(club_id=club_id,
                                    member_data=member_data,
                                    current_user=current_user,
                                    db=db)

        safety_member_data = ClubMemberResponse.model_validate(
            return_data).model_dump(mode="json")

        return create_response(status.HTTP_201_CREATED, "Thêm thành viên mới thành công", req, data=safety_member_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi: {e}"
        )
# =============================== END REGION ===============================


# =============================== XÓA THÀNH VIÊN (CLUB_MEMBER, OWNER) ===============================
@club_router.delete("/{club_id}/members/{user_id}", status_code=status.HTTP_200_OK,
                    dependencies=[Depends(isLoginRequired), Depends(OWNER_ONLY)])
def delete_member(req: Request,
                  club_id: uuid.UUID,
                  user_id: uuid.UUID,
                  current_user: UserModel = Depends(get_current_user),
                  db: Session = Depends(get_db)):

    try:

        delete_result = delete_member_sv(club_id, user_id, current_user, db)

        return create_response(status.HTTP_201_CREATED, "Xóa thành viên câu lạc bộ thành công", req)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi: {e}"
        )

# =============================== END REGION ===============================


# =============================== lấy ra danh sách thành viên (CLUB_MEMBER, OWNER) ===============================
@club_router.get("/{club_id}/members", status_code=status.HTTP_200_OK,
                 dependencies=[Depends(isLoginRequired), Depends(OWNER_ONLY)])
def get_club_members(req: Request, club_id: uuid.UUID, db: Session = Depends(get_db)):

    try:
        list_members = get_club_members_sv(club_id, db)

        safety_list_members = [
            ClubMemberResponse.model_validate(u).model_dump(mode="json") for u in list_members]

        return create_response(status.HTTP_201_CREATED, "Lấy danh sách thành viên thành công", req, data=safety_list_members)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi: {e}"
        )

# =============================== END REGION ===============================


# =============================== XEM LỊCH SỬ THAO TÁC CỦA CLB (OWNER ONLY) ===============================
@club_router.get(
    "/{club_id}/activity-logs",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(isLoginRequired), Depends(OWNER_ONLY)],
)
def get_club_activity_logs(
    req: Request,
    club_id: uuid.UUID,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        logs = get_club_activity_logs_sv(club_id=club_id, db=db)
        safety_logs = [
            ActivityLogResponse.model_validate(log).model_dump(mode="json")
            for log in logs
        ]

        return create_response(
            status_code=status.HTTP_200_OK,
            message="Lấy lịch sử thao tác thành công",
            request=req,
            data=safety_logs,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi: {e}",
        )
# ==============================  END REGION  ========================================

# ============================================================================================================================================
# ============================================================================================================================================
# =============================== QUẢN LÝ HOẠT ĐỘNG CỦA CÂU LẠC BỘ (CLUB_ACTIVITIES) ===============================
# ============================================================================================================================================
# ============================================================================================================================================
# ============================================================================================================================================


# =============================== THÊM HOẠT ĐỘNG MỚI CHO CLB (FULL_ACCESS) ===============================
@club_router.post("/{club_id}/activities", status_code=status.HTTP_201_CREATED,
                  dependencies=[Depends(isLoginRequired),
                                Depends(FULL_ACCESS)])
def new_club_activity(req: Request,
                      club_id: uuid.UUID,
                      activity_data: ClubActivityCreate = Form(...),
                      current_user: UserModel = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    try:

        club_activity_data = new_club_activity_sv(club_id,
                                                  activity_data,
                                                  current_user,
                                                  db)
        safety_activity_data = ClubActivityResponse.model_validate(
            club_activity_data).model_dump(mode="json")

        return create_response(
            status_code=status.HTTP_201_CREATED,
            message="Tạo hoạt động mới thành công",
            request=req,
            data=safety_activity_data,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi: {e}",
        )
# =============================== END REGION ===============================


# =============================== LẤY RA DANH SÁCH HOẠT ĐỘNG CỦA CÂU LẠC BỘ (FULL_ACCESS) ===============================
@club_router.get("/{club_id}/activities", status_code=status.HTTP_200_OK,
                 dependencies=[Depends(isLoginRequired),
                               Depends(FULL_ACCESS)])
def get_club_activities(req: Request, club_id: uuid.UUID, db: Session = Depends(get_db)):

    try:
        club_activities_data = get_club_activities_sv(club_id, db)

        safety_activites_data = [ClubActivityResponse.model_validate(
            club_activity).model_dump(mode="json") for club_activity in club_activities_data]

        return create_response(
            status_code=status.HTTP_201_CREATED,
            message="Xem danh sách hoạt động câu lạc bộ thành công",
            request=req,
            data=safety_activites_data,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi: {e}",
        )
# =============================== END REGION ===============================


# =============================== CHI TIẾT HOẠT ĐỘNG CÂU LẠC BỘ ===============================
@club_router.get(
    "/activities/{id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(isLoginRequired)],
)
def get_activity_detail(
    req: Request,
    id: uuid.UUID,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        activity_data = get_activity_detail_sv(
            id=id, current_user=current_user, db=db
        )

        safety_activity = ClubActivityResponse.model_validate(
            activity_data
        ).model_dump(mode="json")

        return create_response(
            status_code=status.HTTP_200_OK,
            message="Lấy thông tin chi tiết hoạt động thành công",
            request=req,
            data=safety_activity,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi xảy ra: {e}",
        )


# =============================== END REGION ===============================


# =============================== CẬP NHẬT HOẠT ĐỘNG CÂU LẠC BỘ (FULL_ACCESS) ===============================
@club_router.patch("/activities/{id}",
                   status_code=status.HTTP_200_OK,
                   dependencies=[Depends(isLoginRequired)])
def update_club_activity(req: Request,
                         id: uuid.UUID,
                         update_data: ClubActivityUpdate = Form(...),
                         current_user: UserModel = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    try:
        activity_data = update_club_activity_sv(
            activity_id=id,
            update_data=update_data,
            current_user=current_user,
            db=db,
        )

        safety_activity = ClubActivityResponse.model_validate(
            activity_data
        ).model_dump(mode="json")

        return create_response(
            status_code=status.HTTP_200_OK,
            message="Cập nhật hoạt động câu lạc bộ thành công",
            request=req,
            data=safety_activity,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi xảy ra: {e}",
        )


# =============================== END REGION ===============================


# =============================== XÓA HOẠT ĐỘNG CÂU LẠC BỘ ===============================
@club_router.delete(
    "/activities/{id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(isLoginRequired)],
)
def delete_club_activity(
    req: Request,
    id: uuid.UUID,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        delete_club_activity_sv(
            activity_id=id, current_user=current_user, db=db)

        return create_response(
            status_code=status.HTTP_200_OK,
            message="Xóa hoạt động câu lạc bộ thành công",
            request=req,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi xảy ra: {e}",
        )
# =============================== END REGION ===============================
