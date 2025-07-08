from datetime import date, timedelta
from backend.service.weekly_tasks import run_weekly_tasks
from backend.db.models import Week, User, UserWeekPreference, Group, GroupMember
import random

howmanydata = 11

#　ダミーデータ挿入(user,pref)
def seed_users_and_preferences(db, week):
    categories = ["walking", "running"]
    users = []


    for i in range(howmanydata):
        user = User(username=f"user{i+1}", email=f"user{i+1}@test.com", hashed_password="dummy")
        db.add(user)
        db.flush()
        users.append(user)

        pref = UserWeekPreference(
            user_id=user.id,
            week_id=week.id,
            category=random.choice(categories)
        )
        db.add(pref)

    db.commit()
    return users

# closedとactiveの週を同時に挿入(本番環境でも使用するであろう関数. activeは絶対に必要)
def insert_closed_and_active_weeks(db):
    today = date.today()

    # 1週間前の closed week
    closed_start = today - timedelta(days=today.weekday() + 7)
    closed_end = closed_start + timedelta(days=6)

    closed_week = Week(
        start_date=closed_start,
        end_date=closed_end,
        status='closed'
    )

    # 今週の active week
    active_start = today - timedelta(days=today.weekday())  # 今週の月曜
    active_end = active_start + timedelta(days=6)

    active_week = Week(
        start_date=active_start,
        end_date=active_end,
        status='active'
    )

    db.add_all([closed_week, active_week])
    db.commit()

    return closed_week, active_week



def test_run_weekly_tasks(db):


    # 2. 対象関数を実行
    run_weekly_tasks()

    # 3. 結果を検証
    active_week = db.query(Week).filter_by(status='active').first()
    assert active_week is not None

    group = db.query(Group).filter_by(week_id=active_week.id).first()
    assert group is not None

    members = db.query(GroupMember).filter_by(group_id=group.id).all()
    assert len(members) == 2

    # 4. テストデータ削除
    db.query(GroupMember).delete()
    db.query(Group).delete()
    db.query(UserWeekPreference).delete()
    db.query(User).delete()
    db.query(Week).delete()
    db.commit()
