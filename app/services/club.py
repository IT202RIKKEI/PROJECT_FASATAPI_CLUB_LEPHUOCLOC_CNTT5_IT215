from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.club_schemas import ClubCreate, ClubResponse, ClubUpdate
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
    club_dict = club_inp.model_dump()

    club_dict["owner_id"] = current_user.id

    club_data = ClubModel(**club_dict)

    db.add(club_data)
    db.commit()
    db.refresh(club_data)

    return club_data

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
