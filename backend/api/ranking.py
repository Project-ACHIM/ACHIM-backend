from http.client import HTTPException
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.db.models import User, RankingResult
import json
from backend.api.history import get_week_history

router = APIRouter()

# 所属しているグループのランキングやスコアを返す.履歴を表示する画面(front.ranking)にて使用.
@router.get("/groups/{user_id}/rankings") # <- パス名変かも
def get_rankings (db, user_id, week_id):

    
    result = (
        db.query(RankingResult)
        .join(User)
        .filter(RankingResult.week_id == week_id)
        .filter(RankingResult.user_id == user_id)
        .all()
    )

    if result:
        return {
            "user_id": result.user_id,
            "week_id": result.week_id,
            "total_sp": result.total_sp,
            "rank": result.rank
        }
    else:
        return {
            "user_id": user_id,
            "week_id": week_id,
            "message": "ランキングデータが見つかりませんでした"
        }

    