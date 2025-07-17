from sqlalchemy.orm import Session
from backend.db.models import Week

# 履歴登録
def insert_history(db: Session):
    print

# 履歴参照
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

