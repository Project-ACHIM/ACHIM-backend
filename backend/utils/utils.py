from fastapi import HTTPException

def validate_user(request_user_id: int, current_user_id: int):
    if request_user_id != current_user_id:
        raise HTTPException(status_code=403, detail="不正なユーザー操作です")
