from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.api.auth.dependencies import get_current_user
from backend.schemas.bp import *
from backend.services.point_service import *
from backend.utils.utils import validate_user

router = APIRouter()

# 現在のBP取得
@router.get("/balance/{user_id}", response_model=BPBalanceResponse, responses={
    200: {"description": "現在のBP取得成功"},
    403: {"description": "他ユーザーのBPは取得できません"},
    404: {"description": "ユーザーが見つかりません"},
    500: {"description": "サーバーエラー"}
})
def get_current_bp(
    user_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    validate_user(user_id, current_user.id)
    current = fetch_current_bp(user_id, db)
    return BPBalanceResponse(user_id=user_id, current_bp=current)

# 歩数・距離によるBP加算
@router.post("/add", response_model=BPBalanceResponse, responses={
    200: {"description": "BP加算成功"},
    401: {"description": "認証されていません"},
    403: {"description": "不正なBP操作です"},
    500: {"description": "サーバーエラー"}
})
def add_bp(
    request: BPAddActivityRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    validate_user(request.user_id, current_user.id)

    current_bp = add_bp_from_activity(
        db=db,
        user_id=request.user_id,
        week_id=request.week_id,
        step_count=request.steps,
        distance_km=request.distance_km,
        mode=request.mode,
        redemption=request.redemption
    )
    return BPBalanceResponse(user_id=request.user_id, current_bp=current_bp)

# BP減少（賭けや交換など）
@router.post("/decrease", response_model=BPBalanceResponse, responses={
    200: {"description": "BP減少処理成功"},
    400: {"description": "BP不足またはユーザー不正"},
    401: {"description": "認証されていません"},
    403: {"description": "不正なBP操作です"},
    500: {"description": "サーバーエラー"}
})
def decrease_bp_api(
    request: BPDecreaseRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    validate_user(request.user_id, current_user.id)

    try:
        decrease_bp_logic(
            db=db,
            user_id=request.user_id,
            amount=request.amount,
            reason=request.reason,
            detail=request.detail
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    current = fetch_current_bp(request.user_id, db)
    return BPBalanceResponse(user_id=request.user_id, current_bp=current)

# ランキング報酬BP
@router.post("/reward/ranking", response_model=BPBalanceResponse, responses={
    200: {"description": "ランキング報酬によるBP加算成功"},
    400: {"description": "ユーザーが見つかりません"},
    401: {"description": "認証されていません"},
    403: {"description": "不正なBP操作です"},
    500: {"description": "サーバーエラー"}
})
def add_bp_ranking_reward(
    request: BPRewardFromRankingRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    validate_user(request.user_id, current_user.id)

    try:
        add_bp_by_ranking_reward(
            user_id=request.user_id,
            week_id=request.week_id,
            rank=request.rank,
            bp_reward=request.bp_reward,
            db=db
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    current = fetch_current_bp(request.user_id, db)
    return BPBalanceResponse(user_id=request.user_id, current_bp=current)

# MVP・起床・写真等のボーナスによるBP加算（現在は使わない）
@router.post("/reward/bonus", response_model=BPBalanceResponse, responses={
    200: {"description": "ボーナス報酬によるBP加算成功"},
    400: {"description": "ユーザーが見つかりません"},
    401: {"description": "認証されていません"},
    403: {"description": "不正なBP操作です"},
    500: {"description": "サーバーエラー"}
})
def add_bp_bonus_api(
    request: BPBonusRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    validate_user(request.user_id, current_user.id)

    try:
        add_bp_from_bonus(
            db=db,
            user_id=request.user_id,
            week_id=request.week_id,
            amount=request.amount,
            reason=request.reason,
            detail=request.detail
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    current = fetch_current_bp(request.user_id, db)
    return BPBalanceResponse(user_id=request.user_id, current_bp=current)


