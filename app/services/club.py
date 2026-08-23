from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.club_schemas import *
from app.models.club import ClubModel
from app.models.club_members import ClubMemberModel
from app.schemas.enum_schemas import *
from app.models.user import *
from app.core.security import *
from app.schemas.auth import *


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
        club_dict = club_inp.model_dump()

        club_dict["owner_id"] = current_user.id

        club_data = ClubModel(**club_dict)

        db.add(club_data)
        db.commit()
        db.refresh(club_data)

        return club_data
    except Exception as e:
        db.rollback()
        raise e

# =============================== END REGION ===============================


# =============================== Xem danh sách câu lạc bộ ===============================

def get_clubs_sv(club_name: str | None, current_user: UserModel, db: Session):

    # kiểm tra xem người dùng có là chủ hay có phải là thành viên câu lạc bộ chưa
    user_id = current_user.id

    is_joined_club = db.query(ClubMemberModel).filter(
        ClubMemberModel.user_id == user_id).first()

    is_owner = db.query(ClubModel).filter(
        ClubModel.owner_id == user_id).first()

    if not is_joined_club and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn chưa phải là thành viên CLB hoặc là chủ CLB"
        )

    query = db.query(ClubModel)

    if club_name:
        query = query.filter(ClubModel.name.ilike(f"%{club_name}%"))

    return query.all()

# =============================== END REGION ===============================


# =============================== Xem chi tiết câu lạc bộ, chỉ thành viên mới xem được ===============================
def get_club_detail_sv(id: uuid.UUID, current_user: UserModel, db: Session):

    # kiểm tra em user có phải là tv clb ch
    is_club_member = db.query(ClubMemberModel).filter(
        ClubMemberModel.user_id == current_user.id).first()

    if not is_club_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn chưa phải là thành viên CLB hoặc là chủ CLB"
        )

    # tìm club theo uuid
    club_data = db.query(ClubModel).filter(ClubModel.id == id).first()

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

        db.commit()
        db.refresh(current_club)

        return current_club
    except Exception as e:
        db.rollback()
        raise e

# =============================== END REGION ===============================
