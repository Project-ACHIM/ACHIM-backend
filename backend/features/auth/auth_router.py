from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.core.security import verify_password, create_access_token, hash_password
from backend.features.users.user_crud import *
from backend.features.auth.auth_schemas import Token, RegisterRequest
from backend.db.session import get_db
from backend.core.response import success_response
from backend.core.errors import UnauthorizedException, BadRequestException

router = APIRouter()


@router.post("/login", responses={
    200: {"description": "ログイン成功"},
    401: {"description": "メールアドレスまたはパスワードが間違っています"}
})
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    email = form_data.username.strip().lower()
    auth_provider = get_auth_provider_by_email(db, email)
    if not auth_provider or not verify_password(form_data.password, auth_provider.password_hash):
        raise UnauthorizedException("メールアドレスまたはパスワードが間違っています")

    access_token = create_access_token(auth_provider.user.id)
    return success_response(
        Token(access_token=access_token, token_type="bearer").model_dump(),
        message="ログインに成功しました"
    )



@router.post("/signup", status_code=status.HTTP_201_CREATED, responses={
    201: {"description": "ユーザー登録に成功しました"},
    409: {"description": "このメールアドレスはすでに使われています"}
})
async def signup_user(data: RegisterRequest, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    if get_auth_provider_by_email(db, email):
        raise BadRequestException("このメールアドレスはすでに使われています")

    user = create_user(db, email=email, hashed_password=hash_password(data.password))
    token = create_access_token(user.id)
    return success_response(
        Token(access_token=token, token_type="bearer").model_dump(),
        message="ユーザー登録に成功しました"
    )
