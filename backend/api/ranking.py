from http.client import HTTPException
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.db.models import User, RankingResult
import json
from backend.api.get_ids import get_group_id, get_week_id

# 自身のランキングを返す
def get_ranking (db, user_id):

    group_id = get_group_id(db, user_id)
    week_id = get_week_id(db, group_id)


    rankings = (
        db.query(RankingResult)
        .join(User)
        .filter(RankingResult.week_id == week_id)
        .filter(RankingResult.user_id.in_(user_ids))
        .all()
    )
    ranking = {}
    return ranking