from backend.db.models.tables.sp_records import SPRecord
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from datetime import date
from backend.core.point_config import *

# SPレコードの追加。 detailは辞書型で受け取り、内部でJSON文字列化
def add_sp_record(user_id: int, week_id: int, record_date: date, sp_value: int, mode: str, detail: dict, db: Session) -> None:
    record = SPRecord(
        user_id=user_id,
        week_id=week_id,
        date=record_date,
        sp=sp_value,
        mode=mode,
        detail=detail
    )
    db.add(record)
    db.commit()

# 更新
def update_sp_record(record: SPRecord, new_sp: int, detail: dict, db: Session) -> None:
    record.sp = new_sp
    record.detail = detail
    db.commit()

# SPレコードの取得
def get_sp_record_by_date(user_id: int, mode: str, target_date: date, db: Session) -> SPRecord | None:
    result = db.execute(
        select(SPRecord).where(
            SPRecord.user_id == user_id,
            SPRecord.date == target_date,
            SPRecord.mode == mode
        )
    )
    return result.scalars().first()
    
# 指定ユーザーの本日文のSP獲得合計を返す。
def get_today_sp(user_id: int, week_id: int, db: Session) -> int:
    today = date.today()
    total = db.query(func.sum(SPRecord.sp)).filter(
        SPRecord.user_id == user_id,
        SPRecord.week_id == week_id,
        SPRecord.date == today
    ).scalar()

    return total or 0

def get_sp_breakdown_by_date(user_id: int, week_id: int, target_date: date, db: Session) -> dict:
    records = db.execute(
        select(SPRecord).where(
            SPRecord.user_id == user_id,
            SPRecord.week_id == week_id,
            SPRecord.date == target_date
        )
    ).scalars().all()

    breakdown = {
        "total": 0,
        "by_source": {}
    }

    for r in records:
        source = r.detail.get("source", "unknown")
        breakdown["total"] += r.sp
        if source not in breakdown["by_source"]:
            breakdown["by_source"][source] = 0
        breakdown["by_source"][source] += r.sp

    return breakdown


def get_weeks_sp_total(user_id: int, week_id: int, db: Session) -> int:
    total = db.query(func.sum(SPRecord.sp)).filter(
        SPRecord.user_id == user_id,
        SPRecord.week_id == week_id
    ).scalar()
    return total or 0

