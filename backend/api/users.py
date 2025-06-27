from fastapi import APIRouter, Depends
from api.auth.dependencies import get_current_user
from schemas.user import UserResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user = Depends(get_current_user)):
    return current_user
