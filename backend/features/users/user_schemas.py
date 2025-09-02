from typing import Optional
from datetime import datetime, time, date
from pydantic import BaseModel, ConfigDict, field_serializer

from pydantic import BaseModel, ConfigDict, field_serializer
from datetime import datetime, time
from typing import Optional

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Optional[str] = None
    email: str
    profile_image: Optional[str] = None
    created_at: datetime
    region_id: int
    wake_up_time: Optional[time] = None
    notification_enabled: bool
    is_profile_completed: bool

    @field_serializer("wake_up_time", when_used="json")
    def _ser_time(self, t: Optional[time]):
        return t.strftime("%H:%M:%S") if t else None

    @field_serializer("created_at", when_used="json")
    def _ser_datetime(self, dt: datetime):
        return dt.isoformat()  # 例: "2025-08-14T10:15:30"


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    birth_date: Optional[date] = None
    region_id: Optional[int] = None
    wake_up_time: Optional[time] = None
    notification_enabled: Optional[bool] = None

class PubProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: Optional[str] = None
    profile_image: Optional[str] = None
    region_id: int