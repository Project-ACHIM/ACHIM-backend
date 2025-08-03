from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.core.security import verify_password, create_access_token, hash_password
from backend.features.users.user_crud import get_user_by_email, create_user
from backend.features.auth.auth_schemas import Token, RegisterRequest
from backend.db.session import get_db

router = APIRouter()

@router.post("/login", response_model=Token, responses={
    200: {"description": "ログイン成功"},
    401: {"description": "メールアドレスまたはパスワードが間違っています"},
    500: {"description": "サーバーエラー"}
})
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Token:
    auth = get_user_by_email(db, form_data.username)
    if not auth or not verify_password(form_data.password, auth.password_hash):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワートが間違っています",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(auth.user.id)
    return Token(access_token = access_token, token_type = "bearer")

@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED, responses={
    201: {"description": "ユーザー登録に成功しました"},
    400: {"description": "このメールアドレスはすでに使われています"},
    500: {"description": "サーバーエラー"}
})
async def signup_user(data: RegisterRequest, db: Session = Depends(get_db)) -> Token:
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code = 400, detail = "このメールアドレスはすでに使われています")
    user = create_user(db, email=data.email, hashed_password = hash_password(data.password))
    token = create_access_token(user.id)
    return Token(access_token= token, token_type = "bearer")