import os
from datetime import date
from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.db.models.tables.weeks import Week
from backend.core.config import settings
from datetime import datetime
from zoneinfo import ZoneInfo

def today_local():
    return datetime.now(ZoneInfo(settings.APP_TIMEZONE)).date()

# status='active' の週を返す
def get_active_week(db: Session) -> Week:
    wk = db.query(Week).filter(Week.status == "active").first()
    if not wk:
        raise HTTPException(status_code=404, detail="activeな週が見つかりません")
    return wk

# 途中参加用（今日が含まれる週（start_date <= today <= end_date）を返す）ひとまず開発用
def get_today_week(db: Session) -> Week:
    today = today_local()
    wk = db.query(Week).filter(
        Week.start_date <= today,
        Week.end_date >= today
    ).first()
    if not wk:
        raise HTTPException(status_code=404, detail="今日を含む週が見つかりません")
    return wk

def get_week_for_join(db: Session) -> Week:
    if settings.APP_ENV == "production":
        return get_active_week(db)
    return get_today_week(db)

# 本番環境用　月曜日からの参加
def require_monday_if_production():
    if settings.APP_ENV != "production":
        return
    if not settings.MONDAY_JOIN_ONLY:
        return
    if today_local().weekday() != 0:  # 0 = Monday
        raise HTTPException(status_code=400, detail="参加は月曜日のみ可能です")