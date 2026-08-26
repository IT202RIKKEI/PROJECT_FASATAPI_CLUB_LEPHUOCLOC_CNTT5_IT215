from fastapi import (
    APIRouter,
    status,
    Depends,
    Request,
    HTTPException,
    dependencies,
    Form,
    Query,
    File,
    UploadFile
)
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
from app.schemas.response_schemas import BaseResponse
from app.services.activity_log import get_club_activity_logs_sv
from app.schemas.club_activity_schemas import *
from typing import Literal


# tính năng bắt buộc đăng nhập tài khoản
isLoginRequired = RoleSystemChecker(["admin", "user"])
OWNER_ONLY = ClubRoleChecker(["owner"])
FULL_ACCESS = ClubRoleChecker(["owner", "member"])


club_router = APIRouter(prefix="/clubs", tags=["QUẢN LÝ CÂU LẠC BỘ"])


# =============================== TẠO CÂU LẠC BỘ MỚI ===============================
@club_router.post(
    "/",
    response_model=BaseResponse[ClubResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Tạo câu lạc bộ mới",
    description="Người dùng đăng nhập tạo câu lạc bộ mới và tự động trở thành Chủ nhiệm (Owner).",
    dependencies=[Depends(isLoginRequired)],
)
def new_club(
    req: Request,
    club_inp: ClubCreate = Form(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):

    try:
        club_data = new_clubs_sv(club_inp, db, current_user)

        safety_club_data = ClubResponse.model_validate(club_data).model_dump(
            mode="json"
        )

        return create_response(
            status.HTTP_201_CREATED,
            "Tạo câu lạc bộ mới thành công",
            req,
            data=safety_club_data,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Có lỗi: {e}"
        )


# =============================== END REGION ===============================


# =============================== Xem danh sách câu lạc bộ ===============================
@club_router.get(
    "/",
    response_model=BaseResponse[list[ClubResponse]],
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách câu lạc bộ",
    description="Xem toàn bộ danh sách các câu lạc bộ trong hệ thống, hỗ trợ tìm kiếm theo tên.",
    dependencies=[Depends(isLoginRequired)],
)
def get_clubs(
    req: Request,
    club_name: str | None = None,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    try:
        list_clubs = get_clubs_sv(club_name, current_user, db)

        list_safety_clubs = [
            ClubResponse.model_validate(club).model_dump(mode="json")
            for club in list_clubs
        ]

        return create_response(
            status.HTTP_200_OK,
            "Lấy dữ liệu câu lạc bộ thành công",
            req,
            data=list_safety_clubs,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Có lỗi: {e}"
        )


# =============================== END REGION ===============================


# =============================== Xem chi tiết câu lạc bộ, chỉ thành viên mới xem được ===============================
@club_router.get(
    "/{id}",
    response_model=BaseResponse[ClubResponse],
    status_code=status.HTTP_200_OK,
    summary="Xem chi tiết câu lạc bộ",
    description="Chỉ thành viên thuộc câu lạc bộ mới có quyền xem thông tin chi tiết.",
    dependencies=[Depends(isLoginRequired)],
)
def get_club_detail(
    req: Request,
    id: uuid.UUID,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    try:
        club_data = get_club_detail_sv(id, current_user, db)

        safety_club_data = ClubResponse.model_validate(club_data).model_dump(
            mode="json"
        )

        return create_response(
            status.HTTP_200_OK,
            "Lấy dữ liệu câu lạc bộ thành công",
            req,
            data=safety_club_data,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Có lỗi: {e}"
        )


# =============================== END REGION ===============================


# ======================================================================
# =============================== CHỨC NĂNG CỦA ADMIN ===============================
# ======================================================================


# =============================== CẬP NHẬT CÂU LẠC BỘ TẤT CẢ THUỘC TÍNH (OWNER_ONLY) ===============================
@club_router.put(
    "/{club_id}",
    response_model=BaseResponse[ClubResponse],
    status_code=status.HTTP_200_OK,
    summary="Cập nhật toàn bộ thông tin CLB (PUT)",
    description="Chỉ Chủ nhiệm (Owner) mới có quyền cập nhật toàn bộ thuộc tính của CLB.",
    dependencies=[Depends(isLoginRequired), Depends(OWNER_ONLY)],
)
def put_update_club(
    req: Request,
    club_id: uuid.UUID,
    update_data: ClubPutUpdate = Form(...),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    try:
        new_club_data = put_update_club_sv(
            update_data, club_id, current_user, db)

        safety_club_data = ClubResponse.model_validate(new_club_data).model_dump(
            mode="json"
        )

        return create_response(
            status.HTTP_201_CREATED,
            "Cập nhật câu lạc bộ thành công",
            req,
            data=safety_club_data,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Có lỗi: {e}"
        )


# =============================== END REGION ===============================


# =============================== CẬP NHẬT CÂU LẠC BỘ TÙY CHỌN THUỘC TÍNH (OWNER_ONLY) ===============================
@club_router.patch(
    "/{club_id}",
    response_model=BaseResponse[ClubResponse],
    status_code=status.HTTP_200_OK,
    summary="Cập nhật từng phần thông tin CLB (PATCH)",
    description="Chỉ Chủ nhiệm (Owner) mới có quyền cập nhật tùy chọn các thuộc tính của CLB.",
    dependencies=[Depends(isLoginRequired), Depends(OWNER_ONLY)],
)
def patch_update_club(
    req: Request,
    club_id: uuid.UUID,
    update_data: ClubPatchUpdate = Form(...),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    try:
        new_club_data = patch_update_club_sv(
            update_data, club_id, current_user, db)

        safety_club_data = ClubResponse.model_validate(new_club_data).model_dump(
            mode="json"
        )

        return create_response(
            status.HTTP_201_CREATED,
            "Cập nhật câu lạc bộ thành công",
            req,
            data=safety_club_data,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Có lỗi: {e}"
        )


# =============================== END REGION ===============================


# =============================== XÓA CÂU LẠC BỘ (OWNER ONLY) ===============================
@club_router.delete(
    "/{club_id}",
    response_model=BaseResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Xóa câu lạc bộ (Soft Delete)",
    description="Chỉ Chủ nhiệm (Owner) mới có quyền thực hiện thao tác xóa câu lạc bộ.",
    dependencies=[Depends(isLoginRequired), Depends(OWNER_ONLY)],
)
def delete_club(
    req: Request,
    club_id: uuid.UUID,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    try:
        result = delete_club_sv(club_id, current_user, db)

        if result:
            return create_response(
                status.HTTP_200_OK, "Xóa câu lạc bộ thành công", req
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Có lỗi: {e}"
        )


# =============================== END REGION ===============================

# ============================================================================================================================================
# ============================================================================================================================================
# =============================== QUẢN LÝ THÀNH VIÊN CÂU LẠC BỘ (CLUB_MEMBER, OWNER_ONLY) ===============================
# ============================================================================================================================================
# ============================================================================================================================================


# =============================== THÊM THÀNH VIÊN VÀO CLB (OWNER_ONLY) ===============================
@club_router.post(
    "/{club_id}/members",
    response_model=BaseResponse[ClubMemberResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Thêm thành viên vào CLB",
    description="Chỉ Chủ nhiệm (Owner) mới có quyền mời hoặc thêm thành viên mới vào CLB.",
    dependencies=[Depends(isLoginRequired), Depends(OWNER_ONLY)],
)
def new_member(
    req: Request,
    club_id: uuid.UUID,
    member_data: ClubMemberCreate = Form(...),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    try:
        return_data = new_member_sv(
            club_id=club_id, member_data=member_data, current_user=current_user, db=db
        )

        safety_member_data = ClubMemberResponse.model_validate(return_data).model_dump(
            mode="json"
        )

        return create_response(
            status.HTTP_201_CREATED,
            "Thêm thành viên mới thành công",
            req,
            data=safety_member_data,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Có lỗi: {e}"
        )


# =============================== END REGION ===============================


# =============================== XÓA THÀNH VIÊN (CLUB_MEMBER, OWNER) ===============================
@club_router.delete(
    "/{club_id}/members/{user_id}",
    response_model=BaseResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Xóa thành viên khỏi CLB",
    description="Chỉ Chủ nhiệm (Owner) mới có quyền xóa hoặc loại thành viên khỏi CLB.",
    dependencies=[Depends(isLoginRequired), Depends(OWNER_ONLY)],
)
def delete_member(
    req: Request,
    club_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    try:
        delete_result = delete_member_sv(club_id, user_id, current_user, db)

        return create_response(
            status.HTTP_200_OK, "Xóa thành viên câu lạc bộ thành công", req
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Có lỗi: {e}"
        )


# =============================== END REGION ===============================


# =============================== lấy ra danh sách thành viên (CLUB_MEMBER, OWNER) ===============================
@club_router.get(
    "/{club_id}/members",
    response_model=BaseResponse[list[ClubMemberResponse]],
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách thành viên CLB",
    description="Xem danh sách tất cả các thành viên đang sinh hoạt trong câu lạc bộ.",
    dependencies=[Depends(isLoginRequired), Depends(OWNER_ONLY)],
)
def get_club_members(req: Request, club_id: uuid.UUID, db: Session = Depends(get_db)):

    try:
        list_members = get_club_members_sv(club_id, db)

        safety_list_members = [
            ClubMemberResponse.model_validate(u).model_dump(mode="json")
            for u in list_members
        ]

        return create_response(
            status.HTTP_200_OK,
            "Lấy danh sách thành viên thành công",
            req,
            data=safety_list_members,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Có lỗi: {e}"
        )


# =============================== END REGION ===============================


# =============================== XEM LỊCH SỬ THAO TÁC CỦA CLB (OWNER ONLY) ===============================
@club_router.get(
    "/{club_id}/activity-logs",
    response_model=BaseResponse[list[ActivityLogResponse]],
    status_code=status.HTTP_200_OK,
    summary="Xem lịch sử thao tác của CLB",
    description="Chỉ Chủ nhiệm (Owner) mới có quyền kiểm tra nhật ký hoạt động/thay đổi của CLB.",
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
@club_router.post(
    "/{club_id}/activities",
    response_model=BaseResponse[ClubActivityResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Tạo hoạt động mới cho CLB",
    description="Thành viên CLB có quyền tạo task/hoạt động mới. Tiêu đề không được trùng lặp trong CLB.",
    dependencies=[Depends(isLoginRequired), Depends(FULL_ACCESS)],
)
def new_club_activity(
    req: Request,
    club_id: uuid.UUID,
    activity_data: ClubActivityCreate = Form(...),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        club_activity_data = new_club_activity_sv(
            club_id, activity_data, current_user, db
        )
        safety_activity_data = ClubActivityResponse.model_validate(
            club_activity_data
        ).model_dump(mode="json")

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
@club_router.get(
    "/{club_id}/activities",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách hoạt động của CLB",
    description="Hỗ trợ tìm kiếm theo tiêu đề, lọc theo trạng thái/độ ưu tiên/assignee, sắp xếp và phân trang.",
    dependencies=[Depends(isLoginRequired), Depends(FULL_ACCESS)],
)
def get_club_activities(
    req: Request,
    club_id: uuid.UUID,

    # Tìm kiếm và Lọc
    title: str | None = Query(
        None, description="Tìm kiếm theo tiêu đề hoạt động"),
    status_activity: ActivityStatus | None = Query(
        None, description="Lọc theo trạng thái"),
    priority: ActivityPriority | None = Query(
        None, description="Lọc theo độ ưu tiên"),
    assignee_id: uuid.UUID | None = Query(
        None, description="Lọc theo người thực hiện"),
    # Phân trang
    page: int = Query(1, ge=1, description="Số trang (bắt đầu từ 1)"),
    size: int = Query(10, ge=1, le=100, description="Số bản ghi mỗi trang"),

    # sắp xếp theo created_at / due_date
    sort_by: Literal["created_at", "due_date"] = Query(
        "created_at", description="Trường sắp xếp"),
    sort_order: Literal["asc", "desc"] = Query(
        "asc", description="Kiểu sắp xếp"),
    db: Session = Depends(get_db),
):

    try:
        result = get_club_activities_sv(
            club_id=club_id,
            db=db,
            title=title,
            status_filter=status_activity,
            priority=priority,
            assignee_id=assignee_id,
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        safety_items = [
            ClubActivityResponse.model_validate(act).model_dump(mode="json")
            for act in result["items"]
        ]

        response_data = {
            "items": safety_items,
            "pagination": result["pagination"],
        }

        return create_response(
            status_code=status.HTTP_200_OK,  # 👈 Sửa 201 thành 200 OK
            message="Xem danh sách hoạt động câu lạc bộ thành công",
            request=req,
            data=response_data,
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
    response_model=BaseResponse[ClubActivityResponse],
    status_code=status.HTTP_200_OK,
    summary="Xem chi tiết hoạt động CLB",
    description="Chỉ thành viên trong câu lạc bộ chứa hoạt động đó mới có quyền xem chi tiết.",
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
            id=id, current_user=current_user, db=db)

        safety_activity = ClubActivityResponse.model_validate(activity_data).model_dump(
            mode="json"
        )

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
@club_router.patch(
    "/activities/{id}",
    response_model=BaseResponse[ClubActivityResponse],
    status_code=status.HTTP_200_OK,
    summary="Cập nhật hoạt động CLB",
    description="Chủ nhiệm (Owner) sửa được tất cả. Người được giao việc (Assignee) chỉ được cập nhật trạng thái (status).",
    dependencies=[Depends(isLoginRequired)],
)
def update_club_activity(
    req: Request,
    id: uuid.UUID,
    update_data: ClubActivityUpdate = Form(...),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        activity_data = update_club_activity_sv(
            activity_id=id,
            update_data=update_data,
            current_user=current_user,
            db=db,
        )

        safety_activity = ClubActivityResponse.model_validate(activity_data).model_dump(
            mode="json"
        )

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
    response_model=BaseResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Xóa hoạt động CLB",
    description="Chỉ Chủ nhiệm (Owner có role_id = 1) mới có quyền xóa hoạt động.",
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


# =============================== NÂNG CAO THÊM CMT CHO HOẠT ĐỘNG CLB ===============================
@club_router.post(
    "/activities/{id}/comments",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="Thêm trao đổi/bình luận cho hoạt động",
    description="Thành viên CLB có thể thêm trao đổi nội bộ dưới dạng danh sách bình luận.",
    dependencies=[Depends(isLoginRequired)],
)
def add_comment(
    req: Request,
    id: uuid.UUID,
    content: str = Form(..., description="Nội dung comment"),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        data = add_comment_sv(
            activity_id=id, content=content, current_user=current_user, db=db
        )
        return create_response(
            status_code=status.HTTP_201_CREATED,
            message="Thêm bình luận thành công",
            request=req,
            data=data,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi: {e}")
# =============================== END REGION ===============================


# =============================== TẢI LÊN FILE ĐÍNH KÈM / MINH CHỨNG ===============================
@club_router.post(
    "/activities/{id}/attachments",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="Tải lên file đính kèm/minh chứng cho hoạt động",
    description="Upload file minh chứng, hình ảnh hoạt động phong trào (tối đa 5MB, định dạng ảnh/PDF/Word).",
    dependencies=[Depends(isLoginRequired)],
)
def upload_activity_attachment(
    req: Request,
    id: uuid.UUID,
    file: UploadFile = File(..., description="File minh chứng hoặc hình ảnh"),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        attachment_data = upload_attachment_sv(
            activity_id=id,
            file=file,
            current_user=current_user,
            db=db,
        )

        return create_response(
            status_code=status.HTTP_201_CREATED,
            message="Tải lên minh chứng thành công",
            request=req,
            data=attachment_data,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Có lỗi xảy ra: {e}",
        )
# =============================== END REGION ===============================
