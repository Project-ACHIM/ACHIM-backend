# backend/features/photo_event/upload/upload_router.py

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.features.auth.auth_dependencies import get_current_user
from backend.features.groups.group_crud import is_user_joined_in_week
from backend.features.weeks.week_service import get_week_for_join
from backend.features.photo_event.upload.upload_service import save_uploaded_file
from backend.db.models.tables.uploaded_photos import UploadedPhoto
from backend.features.photo_event.upload.upload_schemas import UploadResponse
from backend.features.photo_event.photo.photo_service import list_photos_by_group_and_date
from backend.features.photo_event.photo.photo_schemas import UploadedPhotoResponse
from backend.utils.utils import validate_user

router = APIRouter()

@router.post("/", response_model=UploadResponse, responses={
    200: {"description": "画像アップロード成功"},
    400: {"description": "画像ファイルが必要です / 既に本日投稿済みです"},
    401: {"description": "認証されていません"},
    403: {"description": "アクセス権がありません"},
    500: {"description": "サーバーエラー"}
})
def upload_photo(
    user_id: int = Query(..., description="アップロードするユーザーのID"),
    group_id: int = Query(..., description="投稿先のグループID"),
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1) 権限チェック：user_id とトークンのユーザーID が一致
    validate_user(user_id, current_user.id)

    # 2) 本日１回制限
    today = date.today()
    already = (
        db.query(UploadedPhoto)
          .filter(
              UploadedPhoto.user_id == current_user.id,
              UploadedPhoto.upload_date == today
          )
          .first()
    )
    if already:
        raise HTTPException(400, "今日はすでに投稿済みです（１日１回まで）")

    # 3) グループ参加チェック
    week = get_week_for_join(db)
    if not is_user_joined_in_week(db, current_user.id, week.id):
        raise HTTPException(403, "そのグループに参加していないため投稿できません")

    # 4) ファイル種別チェック
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "画像ファイルを指定してください")

    # 5) ファイル保存
    filename = save_uploaded_file(file)

    # 6) DB登録
    photo = UploadedPhoto(
        group_id   = group_id,
        user_id    = current_user.id,
        filename   = filename,
        url        = "",    # 保護付き配信を利用
        is_demo    = False,
        upload_date= today
    )
    try:
        db.add(photo)
        db.commit()
        db.refresh(photo)
    except:
        db.rollback()
        raise HTTPException(500, "投稿情報の保存中にエラーが発生しました")

    # 7) 保護付きURLを返却
    return UploadResponse(
        filename=photo.filename,
        url=f"/photo/file/{photo.id}"
    )


@router.get("/", response_model=List[UploadedPhotoResponse], responses={
    200: {"description": "画像一覧取得成功"},
    403: {"description": "グループ未参加のためアクセスできません"},
    404: {"description": "該当する画像がありません"},
})
def get_photos(
    group_id: int = Query(..., description="対象のグループID"),
    date_filter: Optional[date] = Query(None, alias="date", description="投稿日フィルター"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1) グループ参加チェック
    week = get_week_for_join(db)
    if not is_user_joined_in_week(db, current_user.id, week.id):
        raise HTTPException(403, "グループ未参加のためアクセスできません")

    # 2) 取得
    photos = list_photos_by_group_and_date(db, group_id, date_filter)
    if not photos:
        raise HTTPException(404, "該当する画像がありません")

    return photos
