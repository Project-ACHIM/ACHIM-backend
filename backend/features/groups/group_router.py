from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.features.groups.group_service import join_group, get_join_status
from backend.features.groups.group_schemas import JoinRequest, JoinResponse, StatusResponse

router = APIRouter()

@router.post("/join", response_model=JoinResponse)
def join(req: JoinRequest, db: Session = Depends(get_db)):
    return join_group(db, user_id=req.user_id, category=req.category, bet_bp=req.bet_bp)

@router.get("/status", response_model=StatusResponse)
def status(user_id: int, db: Session = Depends(get_db)):
    return get_join_status(db, user_id=user_id)