from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.api.auth.dependencies import get_current_user
from backend.utils.utils import validate_user
from backend.features.photo_event.upload_service import save_uploaded_file
from backend.features.photo_event.upload_schemas import UploadResponse

router = APIRouter()

@router.post("/photo", response_model=UploadResponse, responses={
    200: {"description": "画像アップロード成功"},
    400: {"description": "画像ファイルが必要です"},
    401: {"description": "認証されていません"},
    500: {"description": "サーバーエラー"}
})
def upload_photo(
    user_id: int,
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    validate_user(user_id, current_user.id)

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="画像ファイルを指定してください")

    filename, url = save_uploaded_file(file)
    # 必要ならここで `db` を使って filename をDB登録
    

    return UploadResponse(filename=filename, url=url)
