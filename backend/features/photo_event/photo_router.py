from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date

from backend.db.session import get_db
from backend.features.auth.auth_dependencies import get_current_user
from backend.utils.utils import validate_user
from backend.features.photo_event.photo_schemas import UploadedPhotoResponse
# from backend.features.photo_event.photo_router import get_photos_by_group_and_date

router = APIRouter()

@router.get("/photo", response_model=List[UploadedPhotoResponse], responses={
    200: {"description": "画像一覧取得成功"},
    403: {"description": "不正なアクセス"},
    500: {"description": "サーバーエラー"}
})
def get_photos_by_group_and_date(
    group_id: int,
    date_filter: Optional[date] = Query(None, alias="date"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # バリデーション（必要に応じて）
    validate_user(current_user.id, current_user.id)

    photos = get_photos_by_group_and_date(db, group_id, date_filter)
    return photos
