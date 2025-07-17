from fastapi import APIRouter
from backend.db.models import User, RankingResult

router = APIRouter()

# 所属しているグループのランキングやスコアを返す.履歴を表示する画面(front.ranking)にて使用.
@router.get("/groups/{user_id}/rankings") # <- パス名変かも
def get_rankings (db, user_id, week_id):

    
    return 

    