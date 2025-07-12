from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.db.models import Week

router = APIRouter()

# 履歴画面にて使用。開始日(月曜日)と終了日(日曜日)を返す。新しい順。
@router.get("/weeks/history")
def get_week_histories(db: Session):
    weeks = (
        db.query(Week)
        .order_by(Week.start_date.desc())
        .all()
    )
    return [
        {
            "id": w.id,
            "start_date": w.start_date,
            "end_date": w.end_date,
            "status": w.status
        }
        for w in weeks
    ]

