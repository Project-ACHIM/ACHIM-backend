from backend.db.models.tables.points import Point
from backend.db.models.tables.ranking_results import RankingResult
from backend.db.models.tables.group_members import GroupMember
from typing import Optional
from sqlalchemy.orm import Session
from datetime import date
from backend.core.point_config import *
from backend.crud.sp_crud import *
from backend.crud.bp_crud import *

# 現在のBP取得
def fetch_current_bp(user_id: int, db: Session) -> int:
    return get_current_bp(user_id, db)

# 歩数に応じたBP加算
def add_bp_for_steps(user_id: int, steps: int, db: Session):
    units = steps // BP_WALK_UNIT
    bp = units * BP_WALK_GAIN
    if bp > 0:
        increase_bp(user_id, bp, reason="steps", db=db)

# 距離に応じたBP加算
def add_bp_for_distance(user_id: int, distance_km: float, db:Session):
    units = int(distance_km // BP_RUN_UNIT)
    bp = units * BP_RUN_GAIN
    if bp > 0:
        increase_bp(user_id, bp, reason="distance", db=db)

# 歩数＋距離による総合BP加算
def add_bp_from_activity(user_id: int, steps: int, distance_km: float, db: Session):
    step_units = steps // BP_WALK_UNIT
    step_bp = step_units * BP_WALK_GAIN

    run_units = int(distance_km // BP_RUN_UNIT)
    run_bp = run_units * BP_RUN_GAIN

    total_bp = step_bp + run_bp
    if total_bp > 0:
        increase_bp(user_id, total_bp, reason="activity", db=db)

# ランキング報酬のBP加算
def add_bp_by_ranking_reward(user_id: int, week_id: int, rank: int, bp_reward: int, db: Session):
    point = db.query(Point).filter(Point.user_id == user_id).first()
    if not point:
        raise ValueError("対象ユーザーが存在しません")

    point.bp_total += bp_reward
    db.commit()

def add_bp_from_bonus(db: Session, user_id: int, week_id: int, amount: int, reason: str, detail: Optional[str] = None):
    point = db.query(Point).filter(Point.user_id == user_id).first()
    if not point:
        raise ValueError("対象ユーザーが存在しません")

    point.bp_total += amount
    db.commit()

# BPの減少処理
def decrease_bp_logic(db: Session, user_id: int, amount: int, reason: str, detail: Optional[str] = None):
    point = db.query(Point).filter(Point.user_id == user_id).first()
    if not point or point.bp_total < amount:
        raise ValueError("BPが不足しているか、不正なユーザーです")
    
    point.bp_total -= amount
    db.commit()

def distribute_ranking_bp_rewards(week_id: int, db: Session):
    results = db.query(RankingResult).filter(RankingResult.week_id == week_id).all()

    for result in results:
        user_id = result.user_id
        rank = result.rank

        multiplier = RANKING_BP_MULTIPLIERS.get(rank)
        if multiplier is None:
            continue

        # group_idの取得
        group_member = db.query(GroupMember).join(GroupMember.group).filter(
            GroupMember.user_id == user_id,
            GroupMember.group.has(week_id=week_id)
        ).first()

        if not group_member:
            continue

        group_id = group_member.group_id

        entry = get_bet_entry(user_id, group_id, db)
        if not entry or entry.bet_bp is None:
            continue

        reward = int(entry.bet_bp * multiplier)
        set_result_bp(entry, reward, db)
        add_ranking_reward_bp(user_id, reward, db)

# SP計算ロジック
def get_unit_info(
    mode: str,
    redemption: bool,
    step_count: int,
    distance_km: float
) -> tuple[int, int, int, str, dict]:
    config_map = {
        ("walking", False): (SP_WALK_UNIT, SP_WALK_GAIN, step_count, "walk"),
        ("walking", True):  (SP_WALK_RDM_UNIT, SP_WALK_RDM_GAIN, step_count, "walk"),
        ("running", False): (SP_RUN_UNIT, SP_RUN_GAIN, distance_km, "distance"),
        ("running", True):  (SP_RUN_RDM_UNIT, SP_RUN_RDM_GAIN, distance_km, "distance")
    }

    config = config_map.get((mode, redemption))
    if not config:
        raise ValueError(f"未対応のアクティビティモードです: mode={mode}, redemption={redemption}")

    unit, gain, value, key = config
    current_units = int(value // unit)
    detail = {"mode": mode, key: value, "redemption": redemption, "source": key}

    return current_units, gain, unit, key, detail


def calc_sp_for_event(mode: str) -> tuple[int, dict]:
    fixed_sp_map = {
        "mvp": SP_MVP_MAX,
        "photo": SP_PHOTO,
        "wake": SP_WAKE,
    }
    sp = fixed_sp_map.get(mode, 0)
    detail = {"source": mode}
    return sp, detail

def add_sp_by_mode(
    user_id: int,
    week_id: int,
    mode: str,
    step_count: int,
    distance_km: float,
    redemption: bool,
    db: Session
) -> int:
    today = date.today()

    if mode in ("walking", "running"):
        current_units, gain, unit, key, detail = get_unit_info(mode, redemption, step_count, distance_km)
        new_sp = current_units * gain

        if new_sp <= 0:
            return 0

        today_total = get_today_sp(user_id, week_id, db)
        remaining = SP_DAY_CAP - today_total
        if remaining <= 0:
            return 0

        max_addable_sp = min(new_sp, remaining)
        record = get_sp_record_by_date(user_id, mode, today, db)

        if record:
            prev_value = record.detail.get(key, 0)
            prev_units = int(prev_value // unit)
            new_units = int(detail[key] // unit)

            unit_diff = new_units - prev_units
            delta_sp = unit_diff * gain

            if unit_diff <= 0 or delta_sp <= 0:
                return 0

            delta_sp = min(delta_sp, remaining)
            update_sp_record(record, record.sp + delta_sp, detail, db)
            return delta_sp
        else:
            add_sp_record(user_id, week_id, today, max_addable_sp, mode, detail, db)
            return max_addable_sp

    elif mode in ("wake", "photo"):
        # 1日1回制限: すでに今日の記録があれば無効
        existing = get_sp_record_by_date(user_id, mode, today, db)
        if existing:
            return 0

        new_sp, detail = calc_sp_for_event(mode)

        today_total = get_today_sp(user_id, week_id, db)
        remaining = SP_DAY_CAP - today_total
        if remaining <= 0:
            return 0

        max_addable_sp = min(new_sp, remaining)
        add_sp_record(user_id, week_id, today, max_addable_sp, mode, detail, db)
        return max_addable_sp

    elif mode == "mvp":
        new_sp, detail = calc_sp_for_event(mode)

        today_total = get_today_sp(user_id, week_id, db)
        remaining = SP_DAY_CAP - today_total
        if remaining <= 0:
            return 0

        max_addable_sp = min(new_sp, remaining)
        add_sp_record(user_id, week_id, today, max_addable_sp, mode, detail, db)
        return max_addable_sp

    else:
        return 0

    
def add_sp_from_activity(
    db: Session,
    user_id: int,
    week_id: int,
    step_count: int,
    distance_km: float,
    mode: str,
    redemption: bool
) -> int:
    return add_sp_by_mode(
        user_id=user_id,
        week_id=week_id,
        mode=mode,
        step_count=step_count,
        distance_km=distance_km,
        redemption=redemption,
        db=db
    )

