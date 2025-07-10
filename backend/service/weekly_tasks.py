# service/weekly_tasks.py

from datetime import datetime
from sqlalchemy.orm import Session

# from crud.week import get_scheduled_week_to_activate, update_week_status
# from crud.group import create_or_get_group, add_user_to_group
# from crud.group_member import get_matched_user_ids
# from crud.user import get_unmatched_users
# from models import GroupMember

from sqlalchemy.orm import Session
from datetime import datetime, date
from backend.db.models import Week, UserWeekPreference, Group, GroupMember, User
from backend.db.session import get_db   #db.session.py


# 週の状態を更新する処理（前週をclosed、今週をactive）
def close_last_week_and_activate_new(db: Session):
    
    today = date.today()

    # 今週の週データを取得（activeにすべきもの）
    this_week = db.query(Week).filter(
        Week.start_date <= today,
        Week.end_date >= today
    ).first()

    if not this_week:
        return  # 対象週がない場合は処理しない

    # すでに active なら処理済みと判断
    if this_week.status == 'active':
        return

    # 前の active な週を closed にする
    last_active = db.query(Week).filter(Week.status == 'active').first()
    if last_active:
        last_active.status = 'closed'

    # 今週を active に更新
    this_week.status = 'active'
    db.commit()


 # ユーザーの週ごとのジャンル選好に基づきマッチングする
def match_users_by_preference(db: Session):
    # 現在 active な週を取得
    active_week = db.query(Week).filter(Week.status == 'active').first()
    if not active_week:
        return

    # ジャンルごとにグループを作成し、ユーザーを割り当てる
    preferences = db.query(UserWeekPreference).filter_by(week_id=active_week.id).all()

    category_to_users = {}
    for pref in preferences:
        category_to_users.setdefault(pref.category, []).append(pref.user)

    for category, users in category_to_users.items():
        # グループをジャンル別に1つずつ作成（必要に応じて分割ロジック追加可）
        group = Group(week_id=active_week.id, category=category)
        db.add(group)
        db.flush()  # ID確保

        for user in users:
            member = GroupMember(user_id=user.id, group_id=group.id)
            db.add(member)

    db.commit()


def run_weekly_tasks(db:Session):
    # 外部から呼び出すエントリポイント
    db = next(get_db())
    close_last_week_and_activate_new(db)
    match_users_by_preference(db)
    db.close()