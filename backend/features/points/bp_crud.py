from backend.db.models.tables.points import Point
from backend.db.models.tables.bp_entries import BpEntry
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from backend.features.points.point_constants import *

# 指定ユーザーの現在のBP残高を取得
def get_current_bp(user_id: int, db: Session) -> int:
    point = db.query(Point).filter(Point.user_id == user_id).first()
    return point.bp_total if point else 0


# 指定ユーザーのBPを増加させる。amount: 増加量, reason: 加算理由
def increase_bp(user_id: int, amount: int, reason: str, db: Session) -> None:
    point = db.query(Point).filter(Point.user_id == user_id).first()

    if not point:
        point = Point(user_id=user_id, bp_total=0, bet_bp_pending=0)
        db.add(point)
        db.flush()

    point.bp_total += amount
    db.commit()

# 指定ユーザーのBPを減少させる。amount: 減少量
def decrease_bp(user_id: int, amount: int, db: Session) -> None:
    point = db.query(Point).filter(Point.user_id == user_id).first()

    if point.bp_total < amount:
        raise ValueError("BP残高が不足しています")
    
    point.bp_total -= amount
    db.commit()

# 賭け結果のBPを記録 result_bp: ランキング結果の報酬BP
def update_bet_result(user_id: int, group_id: int, result_bp: int, db: Session) -> None:
    entry = db.query(BpEntry).filter(
        BpEntry.user_id == user_id,
        BpEntry.group_id == group_id
    ).first()

    if not entry:
        raise ValueError("賭け情報が見つかりません")
    
    entry.result_bp = result_bp
    db.commit()

# 指定ユーザー・週の賭けBPエントリー取得
def get_bet_entry(user_id: int, group_id: int, db: Session) -> BpEntry | None:
    return db.query(BpEntry).filter(
        BpEntry.user_id == user_id,
        BpEntry.group_id == group_id
    ).first()

# ランキング報酬の加算（Point）
def add_ranking_reward_bp(user_id: int, reward_bp: int, db: Session):
    point = db.query(Point).filter(Point.user_id == user_id).first()
    if not point:
        point = Point(user_id=user_id, bp_total=0, bet_bp_pending=0)
        db.add(point)
        db.flush()
    point.bp_total += reward_bp
    db.commit()

# エントリ結果BPの更新
def set_result_bp(entry: BpEntry, result_bp: int, db: Session):
    entry.result_bp = result_bp
    db.commit()


