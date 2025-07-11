from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.schemas.bp import *
from backend.services.point_service import *

router = APIRouter(prefix="/bp", tags=["BP"])

@router.post("/add", response_model=BPBalanceResponse)
def add_bp(request: BPAddByDistanceRequest, db: Session = Depends(get_db)):
    current_bp = add_bp_for_distance(
        db=db,
        user_id=request.user_id,
        week_id=request.week_id,
        steps=request.steps,
        distance_km=request.distance_km,
        mode=request.mode,
        redemption=request.redemption
    )
    return BPBalanceResponse(user_id=request.user_id, current_bp=current_bp)

