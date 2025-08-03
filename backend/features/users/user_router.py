from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.features.auth.auth_dependencies import get_current_user
from backend.db.session import get_db
from backend.db.models.tables.auth_providers import AuthProvider
from backend.db.models.tables.users import User
from backend.features.users.user_schemas import UserResponse
from backend.features.users.user_schemas import PubProfileResponse
from backend.features.users.user_schemas import UserUpdateRequest
from backend.db.models.tables.regions import Region

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
        name=current_user.name,
        email=auth.email,
        profile_image=current_user.profile_image,
        age=current_user.age,
        region_id=current_user.region_id,
        birth_date=current_user.birth_date,
        wake_up_time=current_user.wake_up_time,
        notification_enabled=current_user.notification_enabled,
        created_at=current_user.created_at
    )

@router.get("/profile/{user_id}", response_model=PubProfileResponse, responses={
    200: {"description": "公開プロフィール取得成功"},
    404: {"description": "ユーザーが見つかりません"}
})
def get_public_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

    return PubProfileResponse(
        id=user.id,
        name=user.name,
        profile_image=user.profile_image,
        region_id=user.region_id
    )

@router.patch("/profile", response_model=UserResponse, responses={
    200: {"description": "プロフィール更新成功"},
    400: {"description": "無効な入力です"},
    401: {"description": "トークンが無効です"},
    500: {"description": "サーバーエラー"}
})
def update_profile(
    update: UserUpdateRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if update.name is not None:
        current_user.name = update.name
    if update.age is not None:
        current_user.age = update.age
    if update.region is not None:
        region = db.query(Region).filter(Region.name == update.region).first()
        if not region:
            raise HTTPException(status_code=400, detail="指定された地域が見つかりません")
        current_user.region_id = region.id
    if update.wake_up_time is not None:
        current_user.wake_up_time = update.wake_up_time
    if update.notification_enabled is not None:
        current_user.notification_enabled = update.notification_enabled
    
    db.commit()
    db.refresh(current_user)

    auth = db.query(AuthProvider).filter(
        AuthProvider.user_id == current_user.id,
        AuthProvider.provider == "email"
    ).first()

    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=auth.email,
        profile_image=current_user.profile_image,
        age=current_user.age,
        region_id=current_user.region_id,
        birth_date=current_user.birth_date,
        wake_up_time=current_user.wake_up_time,
        notification_enabled=current_user.notification_enabled,
        created_at=current_user.created_at
    )