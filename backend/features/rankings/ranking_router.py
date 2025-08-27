# backend/features/ranking/ranking_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.features.rankings.ranking_service import get_my_group_ranking, get_group_ranking
from backend.features.rankings.ranking_schemas import GroupRankingResponse

router = APIRouter()
@router.get("/me", response_model=GroupRankingResponse)
def my_ranking(user_id: int, db: Session = Depends(get_db)):
    return get_my_group_ranking(db, user_id)

@router.get("/group/{group_id}", response_model=GroupRankingResponse)
def group_ranking(group_id: int, db: Session = Depends(get_db)):
    return get_group_ranking(db, group_id)


    