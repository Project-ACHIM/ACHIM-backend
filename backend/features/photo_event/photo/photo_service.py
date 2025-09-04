# backend/features/photo_event/photo/photo_service.py

from sqlalchemy.orm import Session
from backend.db.models.tables.uploaded_photos import UploadedPhoto
from typing import List, Optional
from datetime import date

def list_photos_by_group_and_date(
    db: Session,
    group_id: int,
    date_filter: Optional[date] = None,
    include_demo: bool = True,            # ← デフォルトは True
) -> List[UploadedPhoto]:
    q = db.query(UploadedPhoto).filter(UploadedPhoto.group_id == group_id)

    if date_filter:
        q = q.filter(UploadedPhoto.upload_date == date_filter)

    if not include_demo:
        q = q.filter(UploadedPhoto.is_demo == False)

    return q.order_by(UploadedPhoto.uploaded_at).all()
