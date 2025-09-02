from typing import List, Dict, Any
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException

from backend.features.weeks.week_service import get_week_for_join
from backend.db.models.tables.groups import Group
from backend.db.models.tables.group_members import GroupMember
from backend.db.models.tables.sp_records import SPRecord
from backend.db.models.tables.users import User
from backend.db.models.tables.weeks import Week
from backend.db.models.tables.mvp_awards import MVPAward


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
    # 指定グループ内の“今週のSP合計”を user_id ごとに集計して降順で返す（暫定ランキング用）。
    grp = db.query(Group).filter(Group.id == group_id).first()
    if not grp:
        raise HTTPException(status_code=404, detail="グループが見つかりません")

    # グループメンバー
    members = (
        db.query(User.id, User.name)
        .join(GroupMember, GroupMember.user_id == User.id)
        .filter(GroupMember.group_id == group_id)
        .all()
    )
    user_ids = [m.id for m in members]
    if not user_ids:
        return []

    # 週IDで日次SPを合計
    q = (
        db.query(
            SPRecord.user_id,
            func.coalesce(func.sum(SPRecord.sp), 0).label("total_sp"),
        )
        .filter(SPRecord.week_id == grp.week_id, SPRecord.user_id.in_(user_ids))
        .group_by(SPRecord.user_id)
    )
    rows = q.all()
    totals = {r.user_id: int(r.total_sp) for r in rows}

    # 出力整形
    uname_map = {m.id: m.name for m in members}
    enriched = []
    for uid in user_ids:
        enriched.append(
            {
                "user_id": uid,
                "username": (uname_map.get(uid) or f"user-{uid}"),
                "total_sp": totals.get(uid, 0),
            }
        )

    # ソート：SP降順 → user_id昇順
    enriched.sort(key=lambda x: (-x["total_sp"], x["user_id"]))

    # 競技会方式の順位付け（同点同順位）
    rank = 0
    prev = None
    for i, item in enumerate(enriched):
        if prev is None or item["total_sp"] < prev:
            rank += 1
            prev = item["total_sp"]
        item["rank"] = rank

    return enriched


def get_my_group_ranking(db: Session, user_id: int):
    grp = resolve_user_group_for_current_week(db, user_id)
    board = aggregate_group_sp(db, grp.id)
    return {
        "week_id": grp.week_id,
        "group_id": grp.id,
        "category": grp.category,
        "members": board,
        "is_final": False,
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
        "is_final": False,
    }


# MVP込みの最終集計
def aggregate_group_sp_with_mvp(db: Session, group_id: int) -> List[Dict[str, Any]]:
    grp = db.query(Group).filter(Group.id == group_id).first()
    if not grp:
        raise HTTPException(status_code=404, detail="グループが見つかりません")

    members = (
        db.query(User.id, User.name)
        .join(GroupMember, GroupMember.user_id == User.id)
        .filter(GroupMember.group_id == group_id)
        .all()
    )
    user_ids = [m.id for m in members]
    if not user_ids:
        return []

    # 基本SP
    sp_rows = (
        db.query(
            SPRecord.user_id,
            func.coalesce(func.sum(SPRecord.sp), 0).label("total_sp"),
        )
        .filter(SPRecord.week_id == grp.week_id, SPRecord.user_id.in_(user_ids))
        .group_by(SPRecord.user_id)
        .all()
    )
    totals = {r.user_id: int(r.total_sp) for r in sp_rows}

    # MVPボーナスSP（ユーザーごと合算）
    bonus_rows = (
        db.query(
            MVPAward.user_id,
            func.coalesce(func.sum(MVPAward.sp_bonus), 0).label("bonus_sp"),
        )
        .filter(MVPAward.week_id == grp.week_id, MVPAward.user_id.in_(user_ids))
        .group_by(MVPAward.user_id)
        .all()
    )
    bonus_map = {r.user_id: int(r.bonus_sp) for r in bonus_rows}

    name_map = {m.id: m.name for m in members}
    enriched = []
    for uid in user_ids:
        base = totals.get(uid, 0)
        bonus = bonus_map.get(uid, 0)
        adjusted = base + bonus
        enriched.append({
            "user_id": uid,
            "username": (name_map.get(uid) or f"user-{uid}"),
            "total_sp": base,
            "bonus_sp": bonus,
            "final_result_sp": adjusted,
        })

    # 最終順位は final_result_sp で決定
    enriched.sort(key=lambda x: (-x["final_result_sp"], x["user_id"]))
    rank = 0
    prev = None
    for i, item in enumerate(enriched):
        if prev is None or item["final_result_sp"] < prev:
            rank += 1
            prev = item["final_result_sp"]
        item["rank"] = rank


def get_group_final_ranking(db: Session, group_id: int):
    board = aggregate_group_sp_with_mvp(db, group_id)
    grp = db.query(Group).filter(Group.id == group_id).first()
    if not grp:
        raise HTTPException(status_code=404, detail="グループが見つかりません")
    return {
        "week_id": grp.week_id,
        "group_id": grp.id,
        "category": grp.category,
        "members": board,
        "is_final": True,
    }


def get_my_group_final_ranking(db: Session, user_id: int):
    grp = (
        db.query(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .filter(GroupMember.user_id == user_id)
        .order_by(Group.week_id.desc())
        .first()
    )
    if not grp:
        raise HTTPException(status_code=404, detail="今週のグループに未参加です")
    return get_group_final_ranking(db, grp.id)


# MVP確定一覧 & 暫定プレビュー
def get_mvp_awards_for_week(db: Session, week_id: int):
    rows = (
        db.query(MVPAward, User.name)
        .join(User, User.id == MVPAward.user_id)
        .filter(MVPAward.week_id == week_id)
        .all()
    )
    awards = []
    for award, username in rows:
        awards.append({
            "user_id": award.user_id,
            "username": username,
            "category": award.category,
            "score": int(award.score),
            "sp_bonus": int(award.sp_bonus),
        })
    return {"week_id": week_id, "awards": awards}


def get_mvp_preview(db: Session, week_id: int):
    # 「いまの時点の暫定トップ」を出すだけ（非確定）
    def top_by_sources(sources: list[str], category: str):
        q = (
            db.query(
                SPRecord.user_id,
                func.coalesce(func.sum(SPRecord.sp), 0).label("sum_sp"),
                User.name,
            )
            .join(User, User.id == SPRecord.user_id)
            .filter(
                SPRecord.week_id == week_id,
                SPRecord.detail["source"].astext.in_(sources),
            )
            .group_by(SPRecord.user_id, User.name)
            .order_by(func.coalesce(func.sum(SPRecord.sp), 0).desc())
        ).first()
        if not q:
            return None
        uid, sum_sp, uname = q
        return {"category": category, "user_id": uid, "username": uname, "score": int(sum_sp)}

    cands = []
    for sources, cat in [(["walk"], "max_steps"), (["distance"], "max_distance"), (["wake", "photo"], "event_master")]:
        r = top_by_sources(sources, cat)
        if r:
            r["notes"] = "暫定1位（最終日に確定します）"
            cands.append(r)
    return {"week_id": week_id, "candidates": cands, "is_final": False}


def _ensure_member(db: Session, user_id: int, group_id: int):
    exists = (
        db.query(GroupMember)
        .filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
        .first()
    )
    if not exists:
        raise HTTPException(status_code=403, detail="当該グループのメンバーではありません")
    
# --- 追加: my + ranks を返すラッパ ---
def get_group_weekly_ranking_my_and_all(
    db: Session,
    viewer_user_id: int,
    group_id: int,
    limit: int = 100,
    offset: int = 0,
):
    # グループ存在と所属チェック
    grp = db.query(Group).filter(Group.id == group_id).first()
    if not grp:
        raise HTTPException(status_code=404, detail="グループが見つかりません")
    _ensure_member(db, viewer_user_id, group_id)

    # 週累積SPランキングを取得（全員分）
    board = aggregate_group_sp(db, group_id)  # [{user_id, username, total_sp, rank}, …]

    # my 抽出（見つからない場合は rank=末尾/total_sp=0 として扱う）
    my_row = next((m for m in board if m["user_id"] == viewer_user_id), None)
    if my_row is None:
        uname = db.query(User.name).filter(User.id == viewer_user_id).scalar()
        my_row = {
            "user_id": viewer_user_id,
            "username": (uname or f"user-{viewer_user_id}"),
            "total_sp": 0,
            "rank": (board[-1]["rank"] + 1) if board else 1,
        }

    # ranks ページング（必要な場合のみ）
    paged = board[offset: offset + limit] if (offset or limit) else board

    # レスポンス成形（UI用のキー名に合わせて）
    def to_rank_item(r: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "user_id": r["user_id"],
            "display_name": (r.get("username") or f"user-{r['user_id']}"),
            "total_sp": int(r["total_sp"]),
            "rank": int(r["rank"]),
            "avatar_url": None,
        }

    return {
        "week_id": grp.week_id,
        "group_id": grp.id,
        "category": grp.category,
        "my": to_rank_item(my_row),
        "ranks": [to_rank_item(r) for r in paged],
    }

def get_group_ranking_secured(db: Session, viewer_user_id: int, group_id: int):
    grp = db.query(Group).filter(Group.id == group_id).first()
    if not grp:
        raise HTTPException(status_code=404, detail="グループが見つかりません")
    _ensure_member(db, viewer_user_id, group_id)
    board = aggregate_group_sp(db, group_id)
    return {
        "week_id": grp.week_id,
        "group_id": grp.id,
        "category": grp.category,
        "members": board,
        "is_final": False,
    }

def get_group_final_ranking_secured(db: Session, viewer_user_id: int, group_id: int):
    grp = db.query(Group).filter(Group.id == group_id).first()
    if not grp:
        raise HTTPException(status_code=404, detail="グループが見つかりません")
    _ensure_member(db, viewer_user_id, group_id)
    board = aggregate_group_sp_with_mvp(db, group_id)
    return {
        "week_id": grp.week_id,
        "group_id": grp.id,
        "category": grp.category,
        "members": board,
        "is_final": True,
    }
