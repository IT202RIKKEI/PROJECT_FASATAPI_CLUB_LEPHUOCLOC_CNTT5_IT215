from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # khai báo các biến cần lấy từ .env, pydantic giúp tự động đọc và tìm các biến môi trường có tên trùng khớp
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# lru cache giúp việc khi đọc lần đầu tiên, thì nó sẽ lưu vị trí đọc lại trên ram, khi lần đọc thứ 2 nó sẽ lấy thẳng ra dùng mà không cần đi kiếm lại nữa
@lru_cache
def get_settings() -> Settings:
    return Settings()


# khởi tạo đối tượng Settings để dùng khắp dự án
settings = get_settings()
