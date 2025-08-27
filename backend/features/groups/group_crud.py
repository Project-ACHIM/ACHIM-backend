from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, asc

from backend.db.models.tables.groups import Group
from backend.db.models.tables.group_members import GroupMember
from backend.db.models.tables.users import User
from backend.core.config import settings

# 指定ユーザーが指定週で所属しているグループを返す（未参加なら None）
def get_user_group_in_week(db: Session, user_id: int, week_id: int) -> Optional[Group]:
    return (
        db.query(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .filter(GroupMember.user_id == user_id, Group.week_id == week_id)
        .first()
    )
# 指定週に参加済みかどうかを返す
def is_user_joined_in_week(db: Session, user_id: int, week_id: int) -> bool:
    return get_user_group_in_week(db, user_id, week_id) is not None

# グループの人数・メンバー
def get_group_member_count(db: Session, group_id: int) -> int:
    return db.query(func.count(GroupMember.id)).filter(GroupMember.group_id == group_id).scalar() or 0

def list_group_members(db: Session, group_id: int) -> List[User]:
    return (
        db.query(User)
        .join(GroupMember, GroupMember.user_id == User.id)
        .filter(GroupMember.group_id == group_id)
        .all()
    )

# 定員制の割当（空き優先→無ければ新規）
# 週×カテゴリ内の定員未満のグループを1つ選ぶ。
# 少人数優先 → 先に作られたグループ優先。
def pick_group_with_capacity(db: Session, week_id: int, category: str, max_members: int) -> Optional[Group]:
    subq = (
        db.query(
            Group.id.label("gid"),
            func.count(GroupMember.id).label("mcount")
        )
        .outerjoin(GroupMember, GroupMember.group_id == Group.id)
        .filter(Group.week_id == week_id, Group.category == category)
        .group_by(Group.id)
        .subquery()
    )

    return (
        db.query(Group)
        .join(subq, subq.c.gid == Group.id)
        .filter(subq.c.mcount < max_members)
        .order_by(asc(subq.c.mcount), asc(Group.created_at))
        .first()
    )

def _create_group(db: Session, week_id: int, category: str) -> Group:
    group = Group(week_id=week_id, category=category)
    db.add(group)
    db.flush()  # ID確保
    return group

def get_or_create_group_with_capacity(db: Session, week_id: int, category: str) -> Group:
    group = pick_group_with_capacity(db, week_id, category, settings.GROUP_MAX_MEMBERS)
    if group:
        return group
    return _create_group(db, week_id, category)

# 参加登録（グループに追加）
# すでに同じ group_id に所属していればそのまま返す
def add_member_to_group(db: Session, user_id: int, group_id: int) -> GroupMember:
    existing = (
        db.query(GroupMember)
        .filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
        .first()
    )
    if existing:
        return existing

    member = GroupMember(user_id=user_id, group_id=group_id)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

# 週×カテゴリで参加させる
def join_week_category(db: Session, user_id: int, week_id: int, category: str) -> Group:
    # 同時参加競合対策として、直前に満席化していたら新規作成に逃がす。

    group = get_or_create_group_with_capacity(db, week_id=week_id, category=category)

    if get_group_member_count(db, group.id) >= settings.GROUP_MAX_MEMBERS:
        group = _create_group(db, week_id, category)

    add_member_to_group(db, user_id=user_id, group_id=group.id)
    return group
