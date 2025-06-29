from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from backend.db.session import get_db
from backend.db.models.tables.auth_providers import AuthProvider
from backend.schemas.user import UserResponse
from backend.api.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/profile", response_model=UserResponse, responses={
    200: {"description": "プロフィール情報取得成功"},
    401: {"description": "トークンが無効です"},
    404: {"description": "認証情報が見つかりません"},
    500: {"description": "サーバーエラー"}
})
def get_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    auth = db.query(AuthProvider).filter(
        AuthProvider.user_id == current_user.id,
        AuthProvider.provider == "email"
    ).first()

    if not auth:
        raise HTTPException(status_code=404, detail="認証情報が見つかりません")

    return UserResponse(
        id=current_user.id,
        email=auth.email,
        created_at=current_user.created_at
    )