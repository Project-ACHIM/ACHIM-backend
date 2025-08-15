from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.core.security import decode_access_token
from backend.features.users.user_crud import get_user_by_id
from backend.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/mail/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_id = None
    try:
        user_id = decode_access_token(token)
    except Exception as e:
        pass

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンが無効または期限切れです",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
        )

    user = get_user_by_id(db, user_id)
    if not user:
        # セキュリティ上、ユーザーが存在しないことを明示せず401に統一
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンが無効または期限切れです",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
        )

    return user