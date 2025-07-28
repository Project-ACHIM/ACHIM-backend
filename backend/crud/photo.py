from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date
from backend.db.models.tables.uploaded_photos import UploadedPhoto

# groupe内でアップロードされた画像一覧取得
def get_photos_by_group_and_date(db: Session, group_id: int, date_filter: Optional[date] = None):
    query = db.query(UploadedPhoto).filter(UploadedPhoto.group_id == group_id)
    
    if date_filter:
        query = query.filter(UploadedPhoto.upload_date == date_filter)

    return query.order_by(UploadedPhoto.created_at.desc()).all()
