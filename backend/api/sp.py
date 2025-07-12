from http.client import HTTPException
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.db.models import User, SPRecord
import json
from backend.api.get_ids import get_group_id, get_week_id,get_group_menbers_ids

router = APIRouter()

# 所属しているグループのランキングや日別獲得スコア(詳細)を返す。未完成
# @router.get("/groups/{user_id}/rankings_score")
# def sp_detail(db, user_id):
    
#     group_id = get_group_id(db, user_id)
#     week_id = get_week_id(db, group_id)

#     details = (
#         db.
#         query(SPRecord).
#         filter(SPRecord.week_id == week_id).
#         filter(SPRecord.user_id == user_id).
#         all()
#     )
#     return 
