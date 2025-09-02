from sqlalchemy.orm import Session
from datetime import date
from sqlalchemy import func

from backend.db.session import SessionLocal
from backend.db.models import Week, UserWeekPreference, Group, GroupMember, User
from backend.features.points.point_service import distribute_ranking_bp_rewards
from backend.db.models.tables.mvp_awards import MVPAward
from backend.db.models.tables.sp_records import SPRecord

# 週の状態を更新（前週をclosed、今週をactive）
def close_last_week_and_activate_new(db: Session):
    today = date.today()
    this_week = db.query(Week).filter(
        Week.start_date <= today,
        Week.end_date >= today
    ).first()
    if not this_week:
        return
    if this_week.status == 'active':
        return
    last_active = db.query(Week).filter(Week.status == 'active').first()
    if last_active:
        last_active.status = 'closed'
    this_week.status = 'active'
    db.commit()

# ユーザー希望からグループ割当（既存ロジックそのまま）
def match_users_by_preference(db: Session):
    active_week = db.query(Week).filter(Week.status == 'active').first()
    if not active_week:
        return
    prefs = db.query(UserWeekPreference).filter_by(week_id=active_week.id).all()
    category_to_users = {}
    for pref in prefs:
        category_to_users.setdefault(pref.category, []).append(pref.user)
    for category, users in category_to_users.items():
        group = Group(week_id=active_week.id, category=category)
        db.add(group)
        db.flush()
        for user in users:
            member = GroupMember(user_id=user.id, group_id=group.id)
            db.add(member)
    db.commit()

# MVP計算（週末確定）— SPのみ。BPには影響させない
def _upsert_award(db: Session, week_id: int, user_id: int, category: str, score: int, sp_bonus: int):
    exists = db.query(MVPAward).filter(
        MVPAward.week_id == week_id,
        MVPAward.user_id == user_id,
        MVPAward.category == category
    ).first()
    if exists:
        return
    db.add(MVPAward(week_id=week_id, user_id=user_id, category=category, score=score, sp_bonus=sp_bonus))
    db.commit()

def compute_mvp_awards(db: Session, week_id: int):
    MVP_AWARD_SP_BONUS = 100_000  # 定数化したければ point_constants へ

    # 歩数系（detail.source == "walk"）最大
    top_walk = (
        db.query(SPRecord.user_id, func.coalesce(func.sum(SPRecord.sp), 0).label("sum_sp"))
        .filter(SPRecord.week_id == week_id, SPRecord.detail["source"].astext == "walk")
        .group_by(SPRecord.user_id)
        .order_by(func.coalesce(func.sum(SPRecord.sp), 0).desc())
        .first()
    )
    if top_walk:
        _upsert_award(db, week_id, top_walk.user_id, "max_steps", int(top_walk.sum_sp), MVP_AWARD_SP_BONUS)

    # 距離系（detail.source == "distance"）最大
    top_dist = (
        db.query(SPRecord.user_id, func.coalesce(func.sum(SPRecord.sp), 0).label("sum_sp"))
        .filter(SPRecord.week_id == week_id, SPRecord.detail["source"].astext == "distance")
        .group_by(SPRecord.user_id)
        .order_by(func.coalesce(func.sum(SPRecord.sp), 0).desc())
        .first()
    )
    if top_dist:
        _upsert_award(db, week_id, top_dist.user_id, "max_distance", int(top_dist.sum_sp), MVP_AWARD_SP_BONUS)

    # イベント系（wake/photo 合算）最大
    top_event = (
        db.query(SPRecord.user_id, func.coalesce(func.sum(SPRecord.sp), 0).label("sum_sp"))
        .filter(SPRecord.week_id == week_id, SPRecord.detail["source"].astext.in_(["wake", "photo"]))
        .group_by(SPRecord.user_id)
        .order_by(func.coalesce(func.sum(SPRecord.sp), 0).desc())
        .first()
    )
    if top_event:
        _upsert_award(db, week_id, top_event.user_id, "event_master", int(top_event.sum_sp), MVP_AWARD_SP_BONUS)

    # 皆勤（SP>0 の日数 最大）
    attendance = (
        db.query(SPRecord.user_id, func.count(func.distinct(SPRecord.date)).label("active_days"))
        .filter(SPRecord.week_id == week_id, SPRecord.sp > 0)
        .group_by(SPRecord.user_id)
        .order_by(func.count(func.distinct(SPRecord.date)).desc())
        .first()
    )
    if attendance:
        _upsert_award(db, week_id, attendance.user_id, "attendance_full", int(attendance.active_days), MVP_AWARD_SP_BONUS)

def run_weekly_tasks(db):
    db = SessionLocal()
    try:
        close_last_week_and_activate_new(db)
        last_week = db.query(Week).filter(Week.status == 'closed').order_by(Week.id.desc()).first()
        if last_week:
            # 1) MVP確定（SPボーナスのみ保存）
            compute_mvp_awards(db, week_id=last_week.id)
            # 2) 既存：ランキングBP分配（MVPはBPに影響しない）
            distribute_ranking_bp_rewards(week_id=last_week.id, db=db)
        match_users_by_preference(db)
    finally:
        db.close()
