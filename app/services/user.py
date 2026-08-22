from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user import UserResponse, UserBase, UserCreate, UserUpdate
from app.models.user import *
from app.schemas.role_schemas import *
from app.core.security import *


# =============================== LỌC RA DANH SÁCH USERS CHO ADMIN ===============================
def get_users_sv(db: Session, full_name: str | None = None,
                 email: str | None = None,
                 status: bool | None = None):

    query = db.query(UserModel)

    if full_name:

        query = query.filter(UserModel.full_name.ilike(f"%{full_name}%"))

    if email:
        query = query.filter(UserModel.email.ilike(f"%{email}%"))

    if status:
        query = query.filter(UserModel.is_active == status)

    return query.all()
# =============================== END REGION ===============================
