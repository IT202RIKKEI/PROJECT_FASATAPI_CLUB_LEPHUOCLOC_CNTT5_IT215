from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict


class ActivityLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    club_id: uuid.UUID | None = None
    action: str
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)