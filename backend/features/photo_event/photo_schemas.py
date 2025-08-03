from pydantic import BaseModel
from datetime import datetime, date

class UploadedPhotoResponse(BaseModel):
    id: int
    group_id: int
    user_id: int
    filename: str
    url: str
    upload_date: date
    created_at: datetime

    class Config:
        orm_mode = True
