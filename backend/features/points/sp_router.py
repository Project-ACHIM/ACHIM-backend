from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from sqlalchemy.orm import Session
from typing import Optional
from backend.db.session import get_db
from backend.features.auth.auth_dependencies import get_current_user
from backend.utils.utils import validate_user
from backend.features.points.sp_schemas import *
from backend.features.points.point_service import *
from backend.features.weeks.week_service import today_local

router = APIRouter()

# SP加算（差分）
@router.post("/add", response_model=SPBalanceResponse, responses={
    200: {"description": "SP加算成功"},
    401: {"description": "認証されていません"},
    403: {"description": "不正なSP操作です"},
    500: {"description": "サーバーエラー"}
})
def add_sp(
    request: SPAddRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    validate_user(request.user_id, current_user.id)
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


# 今日のSP取得量
@router.get("/today", response_model=SPBalanceResponse, responses={
    200: {"description": "本日のSP取得成功"},
    403: {"description": "不正なアクセス"},
    500: {"description": "サーバーエラー"}
})
def get_today_sp_total(
    user_id: int,
    week_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    validate_user(user_id, current_user.id)
    today_sp = get_today_sp(user_id=user_id, week_id=week_id, db=db)
    return SPBalanceResponse(user_id=user_id, current_sp=today_sp)


# 今週の合計SP取得量
@router.get("/week-total", response_model=SPBalanceResponse, responses={
    200: {"description": "週間SP取得成功"},
    403: {"description": "不正なアクセス"},
    500: {"description": "サーバーエラー"}
})
def get_week_total_sp_api(
    user_id: int,
    week_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    validate_user(user_id, current_user.id)
    total = get_weeks_sp_total(user_id, week_id, db)
    return SPBalanceResponse(user_id=user_id, current_sp=total)


# 任意日付のSP内訳
@router.get("/breakdown", response_model=SPBreakdownResponse, responses={
    200: {"description": "SP内訳取得成功"},
    403: {"description": "不正なアクセス"},
    500: {"description": "サーバーエラー"}
})
def get_sp_breakdown_api(
    user_id: int,
    week_id: int,
    target_date: Optional[date] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    validate_user(user_id, current_user.id)
    if target_date is None:
        target_date = today_local()
    breakdown = get_sp_breakdown_by_date(user_id, week_id, target_date, db)
    return SPBreakdownResponse(user_id=user_id, breakdown=breakdown)


# イベント系SP加算（MVP・Wake・Photo）
@router.post("/event", response_model=SPBalanceResponse, responses={
    200: {"description": "イベントSP加算成功"},
    403: {"description": "不正なSP操作です"},
    500: {"description": "サーバーエラー"}
})
def add_event_sp_api(
    request: SPEventRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    validate_user(request.user_id, current_user.id)
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
