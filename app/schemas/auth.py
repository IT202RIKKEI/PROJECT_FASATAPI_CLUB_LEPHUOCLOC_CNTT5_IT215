from pydantic import BaseModel, EmailStr




class RefreshTokenRequest(BaseModel):
    refresh_token: str
