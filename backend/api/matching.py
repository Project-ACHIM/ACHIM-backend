# services/matching.py

from sqlalchemy.orm import Session
from backend.db.models import User, Week, Group, GroupMember, UserWeekPreference
from datetime import datetime
import random

# 1グループにつき3-5人
MIN_GROUP_SIZE = 3
MAX_GROUP_SIZE = 5

# 指定された週のユーザーをカテゴリごとにグループへマッチングする。
def match_users_to_groups(db: Session, week: Week):
    
    # ステータス確認（念のため）
    if week.status != 'active':
        raise ValueError("Only active week can be used for matching.")

    # すでにマッチ済みのユーザーを除外
    matched_user_ids = db.query(GroupMember.user_id).join(Group).filter(Group.week_id == week.id).subquery()

    # 今週の希望カテゴリを登録している未マッチユーザーをカテゴリごとに取得
    preferences = (
        db.query(UserWeekPreference)
        .filter(UserWeekPreference.week_id == week.id)
        .filter(~UserWeekPreference.user_id.in_(db.query(matched_user_ids)))
        .all()
    )

    # カテゴリごとにグループを分けてマッチング
    category_to_users = {}
    for pref in preferences:
        category_to_users.setdefault(pref.category, []).append(pref.user)

    # ----------------------------------------ランダムに並べ替え(レートシステムを導入するまで仮)---------------------------------------------------------------
    for category, users in category_to_users.items():
        random.shuffle(users)  

        # グループ分け
        i = 0
        while i < len(users):
            # グループサイズを決める（残り人数が少ない場合も考慮）
            remaining = len(users) - i
            if remaining >= MAX_GROUP_SIZE:
                size = MAX_GROUP_SIZE
            elif remaining >= MIN_GROUP_SIZE:
                size = remaining
            else:
                # 最後のグループが3人未満の場合 → 前のグループと調整
                if i == 0:
                    # 最初のグループすら3人未満ならマッチングしない
                    break
                i -= (MAX_GROUP_SIZE - MIN_GROUP_SIZE)
                continue

            group = Group(week_id=week.id, category=category)
            db.add(group)
            db.flush()  # group.id取得のため

            for user in users[i:i+size]: # i ~ i+sizeの間でグループ化
                member = GroupMember(user_id=user.id, group_id=group.id)
                db.add(member)

            i += size

    db.commit()
