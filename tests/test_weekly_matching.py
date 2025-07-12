from datetime import date, timedelta
from backend.services.weekly_tasks import run_weekly_tasks
from backend.db.models import Week, User, UserWeekPreference, Group, GroupMember
from backend.db.session import get_db
from backend.db.base import Base
from backend.db.session import engine
from backend.db.set_up import setUp_regions

howmanydata = 11
half = howmanydata // 2  # 整数除算

get_db

#　ダミーデータ挿入(user,pref)
def seed_users_and_preferences(db, week):
    users = []

    for i in range(howmanydata):
        user = User(name=f"user{i+1}", email=f"user{i+1}@test.com", password="dummy", region_id = 1)
        db.add(user)
        db.flush()
        users.append(user)
        if i < half:
            category="walking"
        else:
            category="running"
        pref = UserWeekPreference(
            user_id=user.id,
            week_id=week.id,
            category = category          
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
    # モデル反映のためリフレッシュ
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # 必要なダミーデータ作成
    setUp_regions(db)
    closed_week, active_week = insert_closed_and_active_weeks(db)
    seed_users_and_preferences(db, active_week)

    # 対象関数を実行
    print('run_weekly_tasks()')
    run_weekly_tasks(db)

    # 結果を検証
    active_week = db.query(Week).filter_by(status='active').first()
    assert active_week is not None

    group = db.query(Group).filter_by(week_id=active_week.id).first()
    assert group is not None

    members = db.query(GroupMember).filter_by(group_id=group.id).all()
    assert 3 <= len(members) <= 5, f"group {group.id} has {len(members)} members"

    # テストデータ削除

    drop_all(db)
    models_to_check = [Group, GroupMember, UserWeekPreference, User, Week]

    for model in models_to_check:
        count = db.query(model).count()
        assert count == 0, f"{model.__name__} still has {count} records"


def drop_all(db):
    db.query(GroupMember).delete()
    db.query(Group).delete()
    db.query(UserWeekPreference).delete()
    db.query(User).delete()
    db.query(Week).delete()
    db.commit()
    print('削除完了')

