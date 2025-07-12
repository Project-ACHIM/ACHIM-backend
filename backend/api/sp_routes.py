from fastapi import APIRouter, Depends
from datetime import date
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.schemas.sp import *
from backend.services.point_service import *

router = APIRouter()

# 今回の加算SP（差分）
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

# 今日のsp取得量を返すエンドポイント
@router.get("/today", response_model=SPBalanceResponse)
def get_today_sp_total(user_id: int, week_id: int, db: Session = Depends(get_db)):
    today_sp = get_today_sp(user_id=user_id, week_id=week_id, db=db)
    return SPBalanceResponse(user_id=user_id, current_sp=today_sp)

# 今週の合計sp取得量を返すエンドポイント
@router.get("/week-total", response_model=SPBalanceResponse)
def get_week_total_sp_api(user_id: int, week_id: int, db: Session = Depends(get_db)):
    total = get_weeks_sp_total(user_id, week_id, db)
    return SPBalanceResponse(user_id=user_id, current_sp=total)

# SP内訳取得（任意の日付）
@router.get("/breakdown", response_model=SPBreakdownResponse)
def get_sp_breakdown_api(
    user_id: int,
    week_id: int,
    target_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    if target_date is None:
        target_date = date.today()
        
    breakdown = get_sp_breakdown_by_date(user_id, week_id, target_date, db)
    return SPBreakdownResponse(user_id=user_id, breakdown=breakdown)

# イベント用SP加算（MVP/Wake/Photo)
@router.post("/event", response_model=SPBalanceResponse)
def add_event_sp_api(request: SPEventRequest, db: Session = Depends(get_db)):
    sp = add_sp_by_mode(
        user_id=request.user_id,
        week_id=request.week_id,
        mode=request.mode,
        step_count=0,
        distance_km=0,
        redemption=False,
        db=db
    )
    return SPBalanceResponse(user_id=request.user_id, current_sp=sp)

