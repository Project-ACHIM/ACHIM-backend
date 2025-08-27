from typing import List, Dict, Any
from sqlalchemy import func
from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from backend.features.weeks.week_service import get_week_for_join
from backend.db.models.tables.groups import Group
from backend.db.models.tables.group_members import GroupMember
from backend.db.models.tables.sp_records import SPRecord
from backend.db.models.tables.users import User
from backend.db.models.tables.weeks import Week

def resolve_user_group_for_current_week(db: Session, user_id: int) -> Group:
    week = get_week_for_join(db)
    grp = (
        db.query(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .filter(Group.week_id == week.id, GroupMember.user_id == user_id)
        .first()
    )
    if not grp:
        raise HTTPException(status_code=404, detail="今週のグループに未参加です")
    return grp

def aggregate_group_sp(db: Session, group_id: int) -> List[Dict[str, Any]]:
    """
    指定グループ内の“今週のSP合計”を user_id ごとに集計して降順で返す。
    """
    # グループ情報（週の特定に使う）
    grp = db.query(Group).filter(Group.id == group_id).first()
    if not grp:
        raise HTTPException(status_code=404, detail="グループが見つかりません")

    # グループメンバー
    members = (
        db.query(User.id, User.username)
        .join(GroupMember, GroupMember.user_id == User.id)
        .filter(GroupMember.group_id == group_id)
        .all()
    )
    user_ids = [m.id for m in members]
    if not user_ids:
        return []

    if hasattr(SPRecord, "week_id"):
        q = (
            db.query(
                SPRecord.user_id,
                func.coalesce(func.sum(SPRecord.amount), 0).label("total_sp"),
            )
            .filter(SPRecord.week_id == grp.week_id, SPRecord.user_id.in_(user_ids))
            .group_by(SPRecord.user_id)
        )
    else:
        # SPRecord に week_id が無い場合は、週の開始/終了日で created_at を絞る
        wk = db.query(Week).filter(Week.id == grp.week_id).first()
        if not wk:
            raise HTTPException(status_code=404, detail="週情報が見つかりません")
        q = (
            db.query(
                SPRecord.user_id,
                func.coalesce(func.sum(SPRecord.amount), 0).label("total_sp"),
            )
            .filter(
                SPRecord.user_id.in_(user_ids),
                SPRecord.created_at >= wk.start_date,
                SPRecord.created_at < wk.end_date + timedelta(days=1),
            )
            .group_by(SPRecord.user_id)
        )

    rows = q.all()
    totals = {r.user_id: int(r.total_sp) for r in rows}

    # メンバーに合計を紐づけ、未記録は0
    enriched = []
    uname_map = {m.id: m.username for m in members}
    for uid in user_ids:
        enriched.append(
            {
                "user_id": uid,
                "username": uname_map.get(uid, f"user-{uid}"),
                "total_sp": totals.get(uid, 0),
            }
        )

    # ソート：SP降順 → user_id昇順
    enriched.sort(key=lambda x: (-x["total_sp"], x["user_id"]))

    # 競技会方式の順位付け（同点同順位）
    rank = 1
    for i, item in enumerate(enriched):
        if i > 0 and item["total_sp"] < enriched[i - 1]["total_sp"]:
            rank = i + 1
        item["rank"] = rank

    return enriched

def get_my_group_ranking(db: Session, user_id: int):
    grp = resolve_user_group_for_current_week(db, user_id)
    board = aggregate_group_sp(db, grp.id)
    return {
        "week_id": grp.week_id,
        "group_id": grp.id,
        "category": grp.category,
        "members": board,  # [{user_id, username, total_sp, rank}]
    }

def get_group_ranking(db: Session, group_id: int):
    board = aggregate_group_sp(db, group_id)
    grp = db.query(Group).filter(Group.id == group_id).first()
    if not grp:
        raise HTTPException(status_code=404, detail="グループが見つかりません")
    return {
        "week_id": grp.week_id,
        "group_id": grp.id,
        "category": grp.category,
        "members": board,
    }