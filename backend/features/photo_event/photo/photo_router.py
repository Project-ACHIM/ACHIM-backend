# backend/features/photo_event/photo/photo_router.py

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
from fastapi.responses import FileResponse
import os

from backend.db.session import get_db
from backend.features.auth.auth_dependencies import get_current_user
from backend.features.groups.group_crud import is_user_joined_in_week
from backend.features.weeks.week_service import get_week_for_join
from backend.features.photo_event.photo.photo_schemas import UploadedPhotoResponse
from backend.features.photo_event.photo.photo_service import list_photos_by_group_and_date
from backend.db.models.tables.uploaded_photos import UploadedPhoto
from backend.db.models.tables.group_members import GroupMember

router = APIRouter()

@router.get("/", response_model=List[UploadedPhotoResponse], responses={
    200: {"description": "画像一覧取得成功"},
    403: {"description": "不正なアクセス"},
    404: {"description": "該当する画像がありません"},
})
def get_photos(
    group_id:     int,
    date_filter: Optional[date] = Query(None, alias="date"),
    current_user = Depends(get_current_user),
    db:      Session  = Depends(get_db),
):
    # 1) グループ参加チェック
    week = get_week_for_join(db)
    if not is_user_joined_in_week(db, current_user.id, week.id):
        raise HTTPException(403, "グループ未参加のためアクセスできません")

    # 2) 取得
    photos = list_photos_by_group_and_date(db, group_id, date_filter)
    if not photos:
        raise HTTPException(404, "該当する画像がありません")

    # 3) URL プレースホルダを実際のエンドポイントに置換
    for p in photos:
        p.url = f"/photo/file/{p.id}"

    return photos


@router.get("/file/{photo_id}", responses={
    200: {"description": "Protected file"},
    403: {"description": "アクセス権がありません"},
    404: {"description": "ファイルが見つかりません"},
})
def get_protected_photo(
    photo_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1) 投稿レコード取得
    photo = db.query(UploadedPhoto).filter(UploadedPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(404, "Photo not found")

    # 2) 同じグループのメンバーかチェック
    is_member = db.query(GroupMember).filter(
        GroupMember.group_id == photo.group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if not is_member:
        raise HTTPException(403, "You are not allowed to access this photo")

    # 3) ファイルパスを組み立て
    file_path = os.path.join(
        os.getcwd(),                # プロジェクトルート
        "backend", "static", "uploads",
        photo.filename
    )
    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found on disk")

    return FileResponse(path=file_path)
