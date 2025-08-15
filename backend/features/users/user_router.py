from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from backend.features.auth.auth_dependencies import get_current_user
from backend.db.session import get_db
from backend.features.users import user_crud
from backend.features.users.user_schemas import UserResponse, PubProfileResponse, UserUpdateRequest
from backend.db.models.tables.regions import Region
from backend.db.models.tables.auth_providers import AuthProvider
from backend.core.response import success_response
from backend.core.errors import NotFoundException, BadRequestException

router = APIRouter()

@router.get("/profile")
def get_profile(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    auth = user_crud.get_auth_provider(db, current_user.id)
    if not auth:
        raise NotFoundException("認証情報が見つかりません")

    data = UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=auth.email,
        profile_image=current_user.profile_image,
        region_id=current_user.region_id,
        wake_up_time=current_user.wake_up_time,
        notification_enabled=current_user.notification_enabled,
        created_at=current_user.created_at,
        is_profile_completed=current_user.is_profile_completed
    )
    return success_response(jsonable_encoder(data), message="プロフィール情報取得成功")


@router.get("/profile/{user_id}")
def get_public_profile(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("ユーザーが見つかりません")
    data = PubProfileResponse.model_validate(user)
    return success_response(data, message="公開プロフィール取得成功")


@router.patch("/profile")
def update_profile(
    update: UserUpdateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 地域チェック
    if update.region_id is not None:
        region = db.query(Region).filter(Region.id == update.region_id).first()
        if not region:
            raise BadRequestException("指定された地域が見つかりません")

    updated_user = user_crud.update_user(db, current_user, **update.model_dump())

    # 本登録判定
    if (
        updated_user.name and
        updated_user.birth_date and
        updated_user.region_id and
        updated_user.wake_up_time
    ):
        updated_user.is_profile_completed = True
        db.commit()
        db.refresh(updated_user)

    auth = user_crud.get_auth_provider(db, updated_user.id)

    data = UserResponse(
        id=updated_user.id,
        name=updated_user.name,
        email=auth.email,
        profile_image=updated_user.profile_image,
        region_id=updated_user.region_id,
        wake_up_time=updated_user.wake_up_time,
        notification_enabled=updated_user.notification_enabled,
        created_at=updated_user.created_at,
        is_profile_completed=updated_user.is_profile_completed  # ←追加
    )
    return success_response(jsonable_encoder(data), message="プロフィール更新成功")
