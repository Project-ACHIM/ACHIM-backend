from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.features.auth.auth_dependencies import get_current_user
from backend.features.points.bp_schemas import *
from backend.features.points.point_service import *
from backend.utils.utils import validate_user

router = APIRouter()

# 現在のBP取得
@router.get("/balance/{user_id}", response_model=BPBalanceResponse, responses={
    200: {"description": "現在のBP取得成功"},
    401: {"description": "認証されていません（トークン不正/期限切れ）"},
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

# 歩数・距離によるBP加算（歩数/距離のみを使う）
@router.post("/add", response_model=BPChangeResponse, responses={
    200: {"description": "BP加算成功"},
    400: {"description": "リクエストが不正です"},
    401: {"description": "認証されていません"},
    403: {"description": "不正なBP操作です"},
    500: {"description": "サーバーエラー"}
})
def add_bp(
    request: BPAddActivityRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 自分自身のみ操作可
    validate_user(request.user_id, current_user.id)

    if (request.steps or 0) <= 0 and (request.distance_km or 0.0) <= 0.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="歩数または距離のいずれかを指定してください",
        )

    # 差分算出：呼び出し前後の残高差分を delta として返す
    before = fetch_current_bp(request.user_id, db)
    after = add_bp_from_activity(
        user_id=request.user_id,
        steps=request.steps or 0,
        distance_km=request.distance_km or 0.0,
        db=db,
    )
    delta = after - before
    return BPChangeResponse(user_id=request.user_id, delta_bp=delta, current_bp=after)

# 累積（HealthKit）インジェスト
@router.post("/ingest", response_model=BPChangeResponse, responses={
    200: {"description": "累積データを反映しBPを加算（差分）しました"},
    400: {"description": "リクエストが不正です"},
    401: {"description": "認証されていません"},
    403: {"description": "不正なBP操作です"},
    500: {"description": "サーバーエラー"}
})
def ingest_bp_cumulative(
    request: BPIngestRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    validate_user(request.user_id, current_user.id)

    if (request.steps_total or 0) < 0 or (request.distance_total_km or 0.0) < 0.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="累積の歩数/距離は0以上で指定してください",
        )

    before = fetch_current_bp(request.user_id, db)
    after = add_bp_from_cumulative(
        db=db,
        user_id=request.user_id,
        steps_total=request.steps_total or 0,
        distance_total_km=request.distance_total_km or 0.0,
        sent_date=request.sent_date,
    )
    delta = after - before
    return BPChangeResponse(user_id=request.user_id, delta_bp=delta, current_bp=after)

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

# MVP・起床・写真等のボーナス（BPでは使用しない想定）
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
