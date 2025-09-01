from backend.db.models.tables.points import Point
from backend.db.models.tables.ranking_results import RankingResult
from backend.db.models.tables.group_members import GroupMember
from typing import Optional
from sqlalchemy.orm import Session
from datetime import date
from backend.features.points.point_constants import *
from backend.features.points.sp_crud import (
    add_sp_record, update_sp_record, get_sp_record_by_date, get_today_sp
)
from backend.features.points.bp_crud import (
    get_current_bp, increase_bp, get_bet_entry, set_result_bp, add_ranking_reward_bp
)
from backend.features.points.bp_cursor_crud import get_cursor, upsert_cursor
from backend.features.weeks.week_service import today_local


# 現在のBP取得
def fetch_current_bp(user_id: int, db: Session) -> int:
    return get_current_bp(user_id, db)

def add_bp_from_cumulative(
    db: Session,
    user_id: int,
    steps_total: int,
    distance_total_km: float,
    device_id: str | None = None,
    sent_date: date | None = None,
) -> int:
    """
    累積（当日トータル）から“単位差分のみ”を加算。
    - 端末リトライや順不同にも耐性あり
    - 当日が変わればカーソルは日付キーで自然リセット
    """
    # アプリのTZでの“今日”
    on_date = sent_date or today_local()

    # 現在の累積から “単位数” を計算
    new_walk_units = steps_total // BP_WALK_UNIT
    new_run_units = int(distance_total_km // BP_RUN_UNIT)

    cur = get_cursor(db, user_id, on_date, device_id)
    if cur is None:
        # 初回：累積ぶんを丸ごと“単位換算”で付与
        delta_walk_units = new_walk_units
        delta_run_units  = new_run_units
    else:
        # 通常：単位差分のみ
        delta_walk_units = max(new_walk_units - cur.last_walk_units, 0)
        delta_run_units  = max(new_run_units  - cur.last_run_units, 0)

    bp_gain = delta_walk_units * BP_WALK_GAIN + delta_run_units * BP_RUN_GAIN
    if bp_gain > 0:
        increase_bp(user_id, bp_gain, reason="activity", db=db)

    # カーソル更新
    upsert_cursor(
        db=db,
        user_id=user_id,
        on_date=on_date,
        device_id=device_id,
        last_walk_units=new_walk_units,
        last_run_units=new_run_units,
        last_steps_total=steps_total,
        last_distance_total_km=distance_total_km,
    )

    # 最新残高を返却
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
def add_bp_from_activity(user_id: int, steps: int,distance_km: float, db: Session ):
    step_units = steps // BP_WALK_UNIT
    step_bp = step_units * BP_WALK_GAIN
    run_units = int(distance_km // BP_RUN_UNIT)
    run_bp = run_units * BP_RUN_GAIN
    total_bp = step_bp + run_bp
    if total_bp > 0:
        increase_bp(user_id, total_bp, reason="activity", db=db)
    return get_current_bp(user_id, db)

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
) -> tuple[str, int, int, int, str, dict]:
    if mode == "walking":
        record_mode = "walking_rdm" if redemption else "walking"
        unit  = SP_WALK_RDM_UNIT if redemption else SP_WALK_UNIT
        gain  = SP_WALK_RDM_GAIN if redemption else SP_WALK_GAIN
        value = step_count
        key   = "walk"
    elif mode == "running":
        record_mode = "running_rdm" if redemption else "running"
        unit  = SP_RUN_RDM_UNIT if redemption else SP_RUN_UNIT
        gain  = SP_RUN_RDM_GAIN if redemption else SP_RUN_GAIN
        value = distance_km
        key   = "distance"
    else:
        raise ValueError(f"未対応のアクティビティモードです: mode={mode}, redemption={redemption}")

    current_units = int(value // unit)
    detail = {
        "mode": mode,               # 入力モード
        "record_mode": record_mode, # 保存モード（*_rdm を区別）
        key: value,
        "unit": unit,
        "gain": gain,
        "redemption": redemption,
        "source": key,              # breakdown 用
    }
    return record_mode, current_units, gain, unit, key, detail


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
    today = today_local()

    if mode in ("walking", "running"):
        record_mode, current_units, gain, unit, key, detail = get_unit_info(
            mode, redemption, step_count, distance_km
        )
        new_sp = current_units * gain
        if new_sp <= 0:
            return 0

        today_total = get_today_sp(user_id, week_id, db)
        remaining = SP_DAY_CAP - today_total
        if remaining <= 0:
            return 0

        max_addable_sp = min(new_sp, remaining)
        # ← “保存モード”で1日1レコードに分ける
        record = get_sp_record_by_date(user_id, week_id, record_mode, today, db)

        if record:
            prev_value = record.detail.get(key, 0)
            prev_unit  = record.detail.get("unit", unit)  # 互換性のため
            prev_units = int(prev_value // prev_unit)
            new_units  = int(detail[key] // unit)

            unit_diff = new_units - prev_units
            delta_sp  = unit_diff * gain

            if unit_diff <= 0 or delta_sp <= 0:
                return 0

            delta_sp = min(delta_sp, remaining)
            update_sp_record(record, record.sp + delta_sp, detail, db)
            return delta_sp
        else:
            add_sp_record(user_id, week_id, today, max_addable_sp, record_mode, detail, db)
            return max_addable_sp

    elif mode in ("wake", "photo"):
        existing = get_sp_record_by_date(user_id, week_id, mode, today, db)
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

