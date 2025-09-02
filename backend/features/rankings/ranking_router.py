from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.features.rankings.ranking_service import *
from backend.features.rankings.ranking_schemas import *
from backend.features.auth.auth_dependencies import get_current_user

router = APIRouter()
@router.get("/group/weekly", response_model=GroupWeeklyRankingResponse)
def group_weekly_ranking(
    group_id: int,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return get_group_weekly_ranking_my_and_all(
        db=db,
        viewer_user_id=current_user.id,
        group_id=group_id,
        limit=limit,
        offset=offset,
    )


@router.get("/me", response_model=GroupRankingResponse)
def my_ranking(user_id: int, db: Session = Depends(get_db)):
    return get_my_group_ranking(db, user_id)

@router.get("/group/{group_id}", response_model=GroupRankingResponse)
def group_ranking(group_id: int, db: Session = Depends(get_db)):
    return get_group_ranking(db, group_id)

# 最終（MVP込み）
@router.get("/final/me", response_model=GroupRankingResponse)
def my_final_ranking(user_id: int, db: Session = Depends(get_db)):
    return get_my_group_final_ranking(db, user_id)

@router.get("/final/group/{group_id}", response_model=GroupRankingResponse)
def group_final_ranking(group_id: int, db: Session = Depends(get_db)):
    return get_group_final_ranking(db, group_id)

# MVP画面
@router.get("/mvp/awards", response_model=MVPAwardResponse)
def mvp_awards(week_id: int, db: Session = Depends(get_db)):
    return get_mvp_awards_for_week(db, week_id)

@router.get("/mvp/preview", response_model=MVPCandidatesResponse)
def mvp_preview(week_id: int, db: Session = Depends(get_db)):
    return get_mvp_preview(db, week_id)
