import bcrypt
import jwt
from app.core.config import settings
from datetime import datetime, timedelta, timezone

# =============================== hash password ===============================


def get_password_hash(password: str) -> str:

    salt = bcrypt.gensalt()

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

    return hashed_password.decode("utf-8")


# =============================== VERIFY MẬT KHẨU ===============================
def verify_password(password: str, hashed_password: str) -> bool:

    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# cấp token
def create_access_token(data: dict) -> str:

    to_encode = data.copy()

    expire_time = datetime.now(
        timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire_time, "type": "access"})

    token = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)

    return token


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + \
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
    to_encode.update({"exp": expire, "type": "refresh"})
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
