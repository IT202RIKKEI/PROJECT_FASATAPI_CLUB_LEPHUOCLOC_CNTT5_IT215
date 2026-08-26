from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    status_code: int
    message: str
    error: Any | None = None
    data: T | None = None
    timestamp: str
    path: str

    class Config:
        from_attributes = True
