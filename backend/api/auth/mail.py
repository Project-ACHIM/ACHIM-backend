from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.security import verify_password, create_access_token, hash_password
from crud.user_crud import get_user_by_email, create_user
from schemas.auth import Token, RegisterRequest
from db.session import get_db

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Token:
    user = get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user.id)
    return Token(access_token = access_token, token_type = "bearer")

@router.post("/register", response_model=Token)
async def register_user(data: RegisterRequest, db: Session = Depends(get_db)) -> Token:
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code = 400, detail = "Email already registered")
    user = create_user(db, email=data.email, hashed_password = hash_password(data.password))
    token = create_access_token(user.id)
    return Token(access_token= token, token_type = "bearer")

    