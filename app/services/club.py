import os  # thư viện chuẩn python để giao tiếp với hệ điều hành
import shutil
from fastapi import HTTPException, status, Request, UploadFile
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from app.schemas.club_schemas import *
from app.models.club import ClubModel
from app.models.club_members import ClubMemberModel
from app.schemas.enum_schemas import *
from app.models.user import *
from app.models.role import ClubRoleModel
from app.core.security import *
from app.schemas.auth import *
from app.schemas.clubmember_schemas import *
# dùng để ghi log các hoạt động của OWNER
from app.services.activity_log import log_activity
from app.schemas.club_activity_schemas import *
from app.models.activity import ClubActivityModel


# CẤU HÌNH CHO VIỆC UPLOAD THƯ MỤC
ALLOWED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".pdf", ".docx"]
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 Megabytes (tính theo byte)
UPLOAD_DIR = "uploads/activities"


# =============================== Tạo câu lạc bộ ===============================


def new_clubs_sv(club_inp: ClubCreate, db: Session, current_user: UserModel):

    # kiểm tra xem tên clb đã tồn tại chưa
    exists_club = db.query(ClubModel).filter(
        ClubModel.name == club_inp.name).first()

    if exists_club:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tên câu lạc bộ {club_inp.name.title()} đã tồn tại"
        )

    # ổn thì tạo
    try:
        # thêm thông tin ở club và cả ở club_member
        club_dict = club_inp.model_dump()

        club_dict["owner_id"] = current_user.id

        club_data = ClubModel(**club_dict)

        db.add(club_data)
        db.flush()  # lấy id tạm thời của club để gán cho club_id bên club_member

        member_data = ClubMemberModel(
            user_id=current_user.id,
            club_id=club_data.id,
            role_id=1
        )

        db.add(member_data)

        # ghi log hoạt động
        log_activity(
            db=db,
            user_id=current_user.id,
            club_id=club_data.id,
            action="CREATE_CLUB",
            description=f"User {current_user.email} đã tạo CLB '{club_data.name}'",
        )

        db.commit()
        db.refresh(club_data)

        return club_data
    except Exception as e:
        db.rollback()
        raise e

# =============================== END REGION ===============================


# =============================== Xem danh sách câu lạc bộ mà user là owner/member===============================

def get_clubs_sv(club_name: str | None, current_user: UserModel, db: Session):
    # 1. Join với bảng club_members để chỉ lấy CLB mà user là thành viên hoặc owner
    query = (
        db.query(ClubModel)
        .join(ClubMemberModel, ClubModel.id == ClubMemberModel.club_id)
        .filter(
            ClubMemberModel.user_id == current_user.id,
            ClubModel.is_deleted == False,
        )
    )

    # 2. Hỗ trợ tìm kiếm theo tên câu lạc bộ nếu có truyền query param
    if club_name:
        query = query.filter(ClubModel.name.ilike(f"%{club_name.strip()}%"))

    # 3. Trả về danh sách (nếu chưa tham gia CLB nào sẽ tự trả về [])
    return query.order_by(ClubModel.created_at.desc()).all()

# =============================== END REGION ===============================


# =============================== Xem chi tiết câu lạc bộ, chỉ thành viên mới xem được ===============================
def get_club_detail_sv(id: uuid.UUID, current_user: UserModel, db: Session):

    # kiểm tra em user có phải là tv clb ch
    is_club_member = (
        db.query(ClubMemberModel)
        .filter(
            ClubMemberModel.club_id == id,
            ClubMemberModel.user_id == current_user.id,
        )
        .first()
    )

    if not is_club_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn chưa phải là thành viên CLB"
        )

    # tìm club theo uuid
    club_data = (
        db.query(ClubModel)
        .filter(ClubModel.id == id, ClubModel.is_deleted == False)
        .first()
    )

    if not club_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy câu lạc bộ có id: {id}"
        )

    return club_data

# =============================== END REGION ===============================


# ======================================================================
# =============================== CHỨC NĂNG CỦA ADMIN ===============================
# ======================================================================


# =============================== CẬP NHẬT CÂU LẠC BỘ TẤT CẢ THUỘC TÍNH (OWNER_ONLY) ===============================
def put_update_club_sv(update_data: ClubPutUpdate, club_id: uuid.UUID, current_user: UserModel, db: Session):

    current_club = db.query(ClubModel).filter(ClubModel.id == club_id).first()

    if not current_club:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy câu lạc bộ với id: {club_id}"
        )

    # kiểm tra quyền sở hữu trên chính clb này
    if current_club.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền chỉnh sửa câu lạc bộ này!",
        )

    try:
        main_update_data = update_data.model_dump()

        for k, v in main_update_data.items():

            setattr(current_club, k, v)

        # ghi log hoạt động
        log_activity(
            db=db,
            user_id=current_user.id,
            club_id=current_club.id,
            action="UPDATE_CLUB_PUT",
            description=f"User {current_user.email} đã cập nhật '{current_club.name}'",
        )

        db.commit()
        db.refresh(current_club)

        return current_club
    except Exception as e:
        db.rollback()
        raise e

# =============================== END REGION ===============================


# =============================== CẬP NHẬT CÂU LẠC BỘ TẤT CẢ THUỘC TÍNH (OWNER_ONLY) ===============================
def patch_update_club_sv(update_data: ClubPatchUpdate, club_id: uuid.UUID, current_user: UserModel, db: Session):

    current_club = db.query(ClubModel).filter(ClubModel.id == club_id).first()

    if not current_club:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy câu lạc bộ với id: {club_id}"
        )

    # kiểm tra quyền sở hữu trên chính clb này
    if current_club.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền chỉnh sửa câu lạc bộ này!",
        )

    try:
        main_update_data = update_data.model_dump()

        for k, v in main_update_data.items():

            setattr(current_club, k, v)

        # ghi log hoạt động
        log_activity(
            db=db,
            user_id=current_user.id,
            club_id=current_club.id,
            action="UPDATE_CLUB_PATCH",
            description=f"User {current_user.email} đã cập nhật '{current_club.name}'",
        )

        db.commit()
        db.refresh(current_club)

        return current_club
    except Exception as e:
        db.rollback()
        raise e

# =============================== END REGION ===============================


# =============================== XÓA CÂU LẠC BỘ (OWNER ONLY) ===============================
def delete_club_sv(club_id: uuid.UUID, current_user: UserModel, db: Session) -> bool:

    # kiểm tra xem club có tồn tại không
    club = db.query(ClubModel).filter(ClubModel.id == club_id).first()

    if not club:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy câu lạc bộ để xóa"
        )

    # kiểm tra xem có còn ai ở trong clb không

    other_members = db.query(ClubMemberModel).filter(
        ClubMemberModel.club_id == club_id,
        ClubMemberModel.user_id != current_user.id).first()

    if other_members:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Câu lạc bộ vẫn còn thành viên không thể xóa"
        )

    # ổn thì delete
    try:

        log_activity(
            db=db,
            user_id=current_user.id,
            club_id=club_id,
            action="DELETE_CLUB",
            description=f"User {current_user.email} đã giải tán CLB '{club.name}'",
        )

        club.is_deleted = True
        club.deleted_at = datetime.now(timezone.utc)

        db.commit()

        return True
    except Exception as e:
        db.rollback()
        raise e

# =============================== END REGION ===============================


# ======================================================================
# =============================== QUẢN LÝ THÀNH VIÊN CÂU LẠC BỘ (CLUB_MEMBER, OWNER_ONLY) ===============================
# ======================================================================


# =============================== THÊM THÀNH VIÊN VÀO CLB (OWNER_ONLY) ===============================
def new_member_sv(club_id: uuid.UUID, member_data: ClubMemberCreate,
                  current_user: UserModel,
                  db: Session):

    # kiểm tra người dùng có tài khoản không
    is_user = db.query(UserModel).filter(
        UserModel.id == member_data.user_id).first()

    if not is_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại trong hệ thống"
        )

    # kiểm tra xem thành viên đã là thành viên chưa
    is_member = db.query(ClubMemberModel).filter(ClubMemberModel.club_id == club_id,
                                                 ClubMemberModel.user_id == member_data.user_id
                                                 ).first()

    if is_member:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Người này đã là thành viên của câu lạc bộ"
        )

    try:

        # Thêm người dùng vào câu lạc bộ
        # member_dict = member_data.model_dump()
        # member_dict["club_id"] = club_id
        member_model_data = ClubMemberModel(**member_data.model_dump(),
                                            club_id=club_id)
        db.add(member_model_data)

        log_activity(
            db=db,
            user_id=current_user.id,
            club_id=club_id,
            action="ADD_MEMBER",
            description=f"User {current_user.email} đã thêm User ID '{member_data.user_id}' vào CLB",
        )

        db.commit()
        db.refresh(member_model_data)

        return member_model_data

    except Exception as e:
        db.rollback()
        raise e

# =============================== END REGION ===============================


# =============================== XÓA THÀNH VIÊN (CLUB_MEMBER, OWNER) ===============================

def delete_member_sv(club_id: uuid.UUID,
                     user_id: uuid.UUID,
                     current_user: UserModel,
                     db: Session):

    # lấy ra thành viên trong club
    target_member = db.query(ClubMemberModel).filter(ClubMemberModel.club_id == club_id,
                                                     ClubMemberModel.user_id == user_id
                                                     ).first()

    if not target_member:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thành viên không tồn tại trong câu lạc bộ này!"
        )

    # logic chặn xóa owner cuối cùng
    owner_role = db.query(ClubRoleModel).filter(
        ClubRoleModel.name.ilike("owner")).first()

    if owner_role and target_member.role_id == owner_role.id:

        # đếm số lượng owner trong clb
        total_owner = db.query(ClubMemberModel).filter(
            ClubMemberModel.club_id == club_id,
            ClubMemberModel.role_id == owner_role.id
        ).count()

        if total_owner <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể xóa owner cuối cùng của câu lạc bộ"
            )

    try:

        log_activity(
            db=db,
            user_id=current_user.id,
            club_id=club_id,
            action="REMOVE_MEMBER",
            description=f"User {current_user.email} đã xóa User ID '{user_id}' khỏi CLB",
        )

        # xóa mềm
        target_member.is_deleted = True
        target_member.deleted_at = datetime.now(timezone.utc)

        db.commit()

        return True

    except Exception as e:
        db.rollback()
        raise e

# =============================== END REGION ===============================


# =============================== lấy ra danh sách thành viên (CLUB_MEMBER, OWNER) ===============================
def get_club_members_sv(club_id: uuid.UUID, db: Session):

    target_club = db.query(ClubModel).filter(ClubModel.id == club_id).first()

    if not target_club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Câu lạc bộ này không tồn tại"
        )

    # lấy ra danh sách members trong clb

    list_members = (
        db.query(ClubMemberModel)
        .filter(
            ClubMemberModel.club_id == club_id,
            ClubMemberModel.is_deleted == False,
        )
        .all()
    )

    return list_members

# =============================== END REGION ===============================


# ============================================================================================================================================
# ============================================================================================================================================
# =============================== QUẢN LÝ HOẠT ĐỘNG CỦA CÂU LẠC BỘ (CLUB_ACTIVITIES) ===============================
# ============================================================================================================================================
# ============================================================================================================================================
# ============================================================================================================================================

# =============================== THÊM HOẠT ĐỘNG MỚI CHO CLB (FULL_ACCESS) ===============================

def new_club_activity_sv(club_id: uuid.UUID, activity_data: ClubActivityCreate, current_user: UserModel, db: Session):

    # kiểm tra xem title đã tồn tại chưa
    exists_club = db.query(ClubActivityModel).filter(
        ClubActivityModel.title == activity_data.title,
        ClubActivityModel.club_id == club_id).first()

    if exists_club:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tiêu đề hoạt động đã tồn tại: {activity_data.title}"
        )

    # ổn thì tạo
    try:

        activity_model_data = ClubActivityModel(**activity_data.model_dump(),
                                                club_id=club_id)
        db.add(activity_model_data)

        log_activity(
            db=db,
            user_id=current_user.id,
            club_id=club_id,
            action="CREATE_ACTIVITY",
            description=f"User {current_user.email} đã thêm hoạt động '{activity_data.title}' vào CLB: {club_id}",
        )

        db.commit()
        db.refresh(activity_model_data)

        return activity_model_data

    except Exception as e:
        db.rollback()
        raise e
# =============================== END REGION ===============================


# =============================== LẤY RA DANH SÁCH HOẠT ĐỘNG CỦA CÂU LẠC BỘ (FULL_ACCESS) ===============================
def get_club_activities_sv(
    club_id: uuid.UUID,
    db: Session,
    title: str | None = None,
    status_filter: ActivityStatus | None = None,
    priority: ActivityPriority | None = None,
    assignee_id: uuid.UUID | None = None,
    page: int = 1,
    size: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):

    # kiểm tra xem clb có tồn tại không
    club = db.query(ClubModel).filter(ClubModel.id == club_id).first()

    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Câu lạc bộ không tồn tại"
        )

    # query lọc theo club id:
    query = db.query(ClubActivityModel).filter(
        ClubActivityModel.club_id == club_id)

    # lọc theo filter/ title

    if title:
        query = query.filter(ClubActivityModel.title.ilike(f"%{title}%"))

    if status_filter:
        query = query.filter(ClubActivityModel.status == status_filter)

    if priority:
        query = query.filter(ClubActivityModel.priority == priority)

    if assignee_id:
        query = query.filter(ClubActivityModel.assignee_id == assignee_id)

    # đếm ra tổng số bảng ghi lấy ra được

    total_items = query.count()

    # sắp xếp
    sort_col = (ClubActivityModel.created_at
                if sort_by == "created_at"
                else ClubActivityModel.due_date)

    order_function = asc if sort_order == "asc" else desc

    query = query.order_by(order_function(sort_col))

    # phân trang/pagination

    offset = (page - 1) * size  # số lượng bản ghi cần bỏ qua
    items = query.offset(offset).limit(size).all()

    total_pages = (total_items + size - 1) // size if total_items > 0 else 1

    return {
        "items": items,
        "pagination": {
            "page": page,
            "size": size,
            "total_items": total_items,
            "total_pages": total_pages,
        },
    }


# =============================== END REGION ===============================


# =============================== CHI TIẾT HOẠT ĐỘNG CÂU LẠC BỘ (CHỈ THÀNH VIÊN MỚI XEM ĐƯỢC) ===============================

def get_activity_detail_sv(id: uuid.UUID, current_user: UserModel, db: Session):

    current_activity = db.query(ClubActivityModel).filter(
        ClubActivityModel.id == id).first()

    if not current_activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="không tìm thấy hoạt động câu lạc bộ"
        )

    # kiểm tra xem người dùng có phải là thành viên câu lạc bộ không

    is_member = db.query(ClubMemberModel).filter(ClubMemberModel.club_id == current_activity.club_id,
                                                 ClubMemberModel.user_id == current_user.id).first()

    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải là thành viên của câu lạc bộ"
        )

    return current_activity

# =============================== END REGION ===============================


# =============================== CẬP NHẬT HOẠT ĐỘNG CÂU LẠC BỘ (FULL_ACCESS) ===============================
def update_club_activity_sv(activity_id: uuid.UUID, update_data: ClubActivityUpdate,
                            current_user: UserModel,
                            db: Session):

    # tìm hoạt động cần sửa
    current_activity = db.query(ClubActivityModel).filter(
        ClubActivityModel.id == activity_id
    ).first()

    if not current_activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hoạt động để cập nhật!",
        )

    # kiểm tra xem ng dùng có thuộc câu lạc bộ này không
    member_record = db.query(ClubMemberModel).filter(
        ClubMemberModel.club_id == current_activity.club_id,
        ClubMemberModel.user_id == current_user.id,
        ClubMemberModel.is_deleted == False
    ).first()

    if not member_record:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của câu lạc bộ này!",
        )

    # xác định vai trò và phân quyền
    is_owner = member_record.role_id == 1
    is_assignee = current_activity.assignee_id == current_user.id

    # Nếu không phải Owner và cũng không phải Assignee -> Không có quyền sửa
    if not is_owner and not is_assignee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Chủ nhiệm hoặc Người được giao việc mới có quyền cập nhật hoạt động này!",
        )

    # lấy dữ liệu người dùng gửi lên (loại trừ None)
    update_dict = update_data.model_dump(exclude_unset=True)

    # NẾU LÀ ASSIGNEE -> CHỈ ĐC SỬA STATUS
    if is_assignee and not is_owner:
        restricted_fields = {
            "title",
            "description",
            "due_date",
            "assignee_id",
            "priority",
        }

        if any(field in update_dict for field in restricted_fields):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Người được giao việc chỉ có quyền cập nhật trạng thái (status)!",
            )

    # nếu cập nhật assignee_id thì kiểm tra ng được giao có phải là tv clb hem
    if "assignee_id" in update_dict and update_dict["assignee_id"] is not None:
        target_assignee = (
            db.query(ClubMemberModel)
            .filter(
                ClubMemberModel.club_id == current_activity.club_id,
                ClubMemberModel.user_id == update_dict["assignee_id"],
                ClubMemberModel.is_deleted == False
            ).first()
        )

        if not target_assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người được phân công không thuộc câu lạc bộ này!",
            )

    # Nếu có cập nhật title, kiểm tra trùng tên trong cùng CLB
    if "title" in update_dict:
        exists_title = (
            db.query(ClubActivityModel)
            .filter(
                ClubActivityModel.club_id == current_activity.club_id,
                ClubActivityModel.title == update_dict["title"],
                ClubActivityModel.id != current_activity.id,
            )
            .first()
        )
        if exists_title:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tiêu đề hoạt động '{update_dict['title']}' đã tồn tại trong CLB!",
            )

    # WORKFLOW CHO CẬP NHẬT STATUS
    if "status" in update_dict and update_dict["status"] != current_activity.status:
        INVALID_STEPS = (
            # Cấm TODO nhảy thẳng lên DONE
            (ActivityStatus.TODO, ActivityStatus.DONE),
            # Cấm DONE nhảy lùi về TODO
            (ActivityStatus.DONE, ActivityStatus.TODO),
        )

        if (current_activity.status, update_dict["status"]) in INVALID_STEPS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Không thể chuyển trạng thái từ {current_activity.status} sang {update_dict["status"].value}!"
            )

    try:
        for key, value in update_dict.items():
            setattr(current_activity, key, value)

        log_activity(
            db=db,
            user_id=current_user.id,
            club_id=current_activity.club_id,
            action="UPDATE_ACTIVITY",
            description=f"User {current_user.email} đã cập nhật hoạt động '{current_activity.title}'",
        )

        db.commit()
        db.refresh(current_activity)
        return current_activity
    except Exception as e:
        db.rollback()
        raise e
# =============================== END REGION ===============================


# =============================== XOA HOẠT ĐỘNG CLB (FULL_ACCESSS) ===============================
def delete_club_activity_sv(
    activity_id: uuid.UUID, current_user: UserModel, db: Session
) -> bool:
    # Tìm hoạt động
    activity = (
        db.query(ClubActivityModel)
        .filter(ClubActivityModel.id == activity_id)
        .first()
    )

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hoạt động để xóa!",
        )

    # KIỂM TRA QUYỀN: Phải là OWNER của CLB chứa hoạt động này
    owner_record = (
        db.query(ClubMemberModel)
        .filter(
            ClubMemberModel.club_id == activity.club_id,
            ClubMemberModel.user_id == current_user.id,
            ClubMemberModel.role_id == 1,
            ClubMemberModel.is_deleted == False,
        )
        .first()
    )

    if not owner_record:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Chủ nhiệm câu lạc bộ (Owner) mới có quyền xóa hoạt động!",
        )

    # tiến hành xóa
    try:
        activity_title = activity.title
        club_id = activity.club_id

        # Ghi log hoạt động
        log_activity(
            db=db,
            user_id=current_user.id,
            club_id=club_id,
            action="DELETE_ACTIVITY",
            description=f"User {current_user.email} đã xóa hoạt động '{activity_title}'",
        )

        db.delete(activity)
        db.commit()
        return True

    except Exception as e:
        db.rollback()
        raise e
# =============================== END REGION ===============================


# =============================== NÂNG CAO THÊM COMMENT CHO HOẠT ĐỘNG ===============================

def add_comment_sv(activity_id: uuid.UUID, content: str, current_user: UserModel, db: Session):

    activity = (
        db.query(ClubActivityModel)
        .filter(ClubActivityModel.id == activity_id)
        .first()
    )

    if not activity:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy hoạt động!")

    # Kiểm tra có phải thành viên CLB không

    member = (
        db.query(ClubMemberModel)
        .filter(ClubMemberModel.club_id == activity.club_id,
                ClubMemberModel.user_id == current_user.id,
                ClubMemberModel.is_deleted == False)
    ).first()

    if not member:
        raise HTTPException(
            status_code=403, detail="Bạn không phải thành viên CLB này!"
        )

    # tạo commemt
    new_comment = {
        "user_id": str(current_user.id),
        "user_email": current_user.email,
        "content": content,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # thêm vào list và lưu lại
    current_comments = list(activity.comments or [])
    current_comments.append(new_comment)
    activity.comments = current_comments

    try:
        db.commit()
        db.refresh(activity)
        return new_comment
    except Exception as e:
        db.rollback()
        raise e

# =============================== END REGION ===============================

# =============================== NÂNG CAO UPLOAD FILE ĐÍNH KÈM  ===============================


def upload_attachment_sv(
    activity_id: uuid.UUID,
    file: UploadFile,
    current_user: UserModel,
    db: Session,
):

    # lấy ra hoạt động và kiểm tra quyền thành viên clb
    activity = (
        db.query(ClubActivityModel)
        .filter(ClubActivityModel.id == activity_id)
        .first()
    )
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hoạt động không tồn tại!",
        )

    member = (
        db.query(ClubMemberModel)
        .filter(
            ClubMemberModel.club_id == activity.club_id,
            ClubMemberModel.user_id == current_user.id,
            ClubMemberModel.is_deleted == False,
        )
        .first()
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải là thành viên của câu lạc bộ này!",
        )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên file không hợp lệ!",
        )

    # kiểm tra đuôi file và kích thước file
    # lấy đuôi file
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Loại file không hợp lệ! Chỉ chấp nhận: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # đọc kích thước file
    # đưa con trỏ đến cuối file để đọc kích thước
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)  # đưa về đầu file để lưu

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kích thước file quá lớn (tối đa 5MB)!",
        )

    # lưu file vào db và tạo thư mục trên máy
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # tạo tên file kèm uuid
    saved_filename = f"{uuid.uuid4()}_{file.filename}"

    # gộp thành đường dẫn hoàn chỉnh để lưu
    file_save_path = os.path.join(UPLOAD_DIR, saved_filename)

    # tiến hành lưu file
    with open(file_save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # lưu thông tin vào db
    new_attachment = {
        "id": str(uuid.uuid4()),
        "file_name": file.filename,
        "file_path": file_save_path.replace("\\", "/"),  # Chuẩn hóa đường dẫn
        "file_size": file_size,
        "uploader_email": current_user.email,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    current_attachments = list(activity.attachments or [])
    current_attachments.append(new_attachment)
    activity.attachments = current_attachments

    try:
        db.commit()
        db.refresh(activity)
        return new_attachment
    except Exception as e:
        db.rollback()
        raise e
# =============================== END REGION ===============================
