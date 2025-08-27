from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.features.weeks.week_service import get_week_for_join, require_monday_if_production
from backend.features.groups.group_crud import is_user_joined_in_week, join_week_category
from backend.features.groups.group_schemas import GroupCategory
from backend.features.points.point_service import decrease_bp_logic
from backend.db.models.tables.points import Point
from backend.db.models.tables.bp_entries import BpEntry

def ensure_enough_bp(db: Session, user_id: int, bet_bp: int):
    pt = db.query(Point).filter(Point.user_id == user_id).first()
    if not pt or (pt.bp_total or 0) < bet_bp:
        raise HTTPException(status_code=400, detail="BP残高が不足しています")

def create_bet_entry(db: Session, user_id: int, group_id: int, bet_bp: int):
    entry = BpEntry(user_id=user_id, group_id=group_id, bet_bp=bet_bp, result_bp=0)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def join_group(db: Session, user_id: int, category: GroupCategory, bet_bp: int):
    """
    参加の単一入口:
      - 本番: 月曜のみ判定
      - 週の決定（active or 今日の週）
      - 同週重複参加チェック
      - BP残高確認→BET減算
      - 週×カテゴリの空きグループへ参加（無ければ新規）
      - 賭けBPの履歴記録
      - 参加結果を返却
    """
    require_monday_if_production()
    week = get_week_for_join(db)

    if is_user_joined_in_week(db, user_id, week.id):
        raise HTTPException(status_code=400, detail="既に今週のグループに参加しています")

    ensure_enough_bp(db, user_id, bet_bp)
    decrease_bp_logic(db, user_id=user_id, amount=bet_bp, reason="BET", detail=f"{category.value}参加")

    group = join_week_category(db, user_id=user_id, week_id=week.id, category=category.value)
    create_bet_entry(db, user_id=user_id, group_id=group.id, bet_bp=bet_bp)

    pt = db.query(Point).filter(Point.user_id == user_id).first()
    return {
        "message": "参加が完了しました",
        "week_id": week.id,
        "group_id": group.id,
        "category": category,
        "bet_bp": bet_bp,
        "bp_balance": pt.bp_total if pt else 0,
    }

def get_join_status(db: Session, user_id: int):
    week = get_week_for_join(db)
    joined = is_user_joined_in_week(db, user_id, week.id)
    return {"week_id": week.id, "is_joined": joined}
