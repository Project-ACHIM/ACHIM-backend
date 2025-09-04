from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.features.groups.group_service import join_group, get_join_status, fill_with_demo
from backend.features.groups.group_schemas import JoinRequest, JoinResponse, StatusResponse
from backend.features.auth.auth_dependencies import get_current_user
from backend.core.response import success_response

router = APIRouter()

@router.post("/join")
def join(req: JoinRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user),):
    result: JoinResponse = join_group(
        db, user_id=current_user.id, category=req.category, bet_bp=req.bet_bp
    )
    fill_with_demo(db, result.group_id)
    return success_response(result)


@router.get("/status")
def status(db: Session = Depends(get_db), current_user = Depends(get_current_user),):
    result: StatusResponse = get_join_status(db, user_id=current_user.id)
    return success_response(result)
