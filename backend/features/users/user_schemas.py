from pydantic import BaseModel
from datetime import datetime, time

class UserResponse(BaseModel):
    id: int
    name: str | None
    email: str
    profile_image: str | None
    created_at: datetime
    region_id: int
    wake_up_time: time | None
    notification_enabled: bool

    class Config:
        orm_mode = True

class UserUpdateRequest(BaseModel):
    name: str | None = None
    region_id: str | None = None
    wake_up_time: time | None = None
    notification_enabled: bool | None = None

class PubProfileResponse(BaseModel):
    id: int
    name: str | None
    profile_image: str | None
    region_id: int