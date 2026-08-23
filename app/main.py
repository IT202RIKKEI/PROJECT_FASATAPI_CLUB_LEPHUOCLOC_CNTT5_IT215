from fastapi import FastAPI, status, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException, RequestValidationError
from app.models.activity import *
from app.models.club_members import *
from app.models.club import *
from app.models.role import *
from app.models.user import *
from app.db.database import Base, Engine
from app.routers.auth import auth_router
from app.routers.users import user_router
from app.routers.club import club_router
from app.utils.utils import create_response
from app.core.limiter import limiter
from slowapi.errors import RateLimitExceeded


app = FastAPI(title="Club Management API",
              version="1.0.0")

# Gắn limit vào app để thông báo lỗi nếu vượt quá số lần


app.state.limiter = limiter

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(club_router)

Base.metadata.create_all(Engine)
# =============================== THIẾT LẬP GLOBAL EXCEPTIONS ===============================


# xử lí raise lỗi khi vượt quá giới hạn cho Limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_exceeded(request: Request, exc: RateLimitExceeded):
    return create_response(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        message="Bạn đã thực hiện quá nhiều yêu cầu! Vui lòng thử lại sau.",
        request=request,
        error="Quá giới hạn tần suất yêu cầu (Rate limit exceeded)",
    )

# 1. Bắt lỗi HTTPException (400, 401, 403, 404, 409,...)


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return create_response(
        status_code=exc.status_code,
        message="Yêu cầu không hợp lệ hoặc xảy ra lỗi logic",
        request=request,
        error=exc.detail,
    )


# 2. Bắt lỗi validate Pydantic (422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_list = [f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()]
    return create_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Dữ liệu đầu vào không đúng định dạng",
        request=request,
        error=error_list,
    )


# 3. Bắt lỗi 500 hệ thống (Ẩn chi tiết lỗi nội bộ)
@app.exception_handler(Exception)
async def global_generic_exception_handler(request: Request, exc: Exception):
    return create_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Đã xảy ra lỗi hệ thống phía server",
        request=request,
        error=str(exc),
    )

# =============================== END REGION ===============================


# =============================== HEALTH CHECK ===============================
@app.get("/api/v1/health_check", status_code=status.HTTP_200_OK)
def check_health():

    return {
        "message": "API STILL RUNNING PERFECTLY"
    }
