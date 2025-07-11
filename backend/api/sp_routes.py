from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.schemas.sp import *
from backend.services.point_service import *

router = APIRouter(prefix="/sp", tags=["SP"])

@router.post("/add", response_model=SPBalanceResponse)
def add_sp(request: SPAddRequest, db: Session = Depends(get_db)):
    current_sp = add_sp_from_activity(
        db=db,
        user_id=request.user_id,
        week_id=request.week_id,
        step_count=request.steps,
        distance_km=request.distance_km,
        mode=request.mode.value,
        redemption=request.redemption
    )
    return SPBalanceResponse(user_id=request.user_id, current_sp=current_sp)