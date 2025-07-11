from backend.db.models.tables.points import Point
from backend.db.models.tables.sp_records import SPRecord
from backend.db.models.tables.bp_entries import BpEntry
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
def add_bp_from_steps_and_distance(user_id: int, steps: int, distance_km: float, db: Session):
    step_units = steps // BP_WALK_UNIT
    step_bp = step_units * BP_WALK_GAIN

    run_units = int(distance_km // BP_RUN_UNIT)
    run_bp = run_units * BP_RUN_GAIN

    total_bp = step_bp + run_bp
    if total_bp > 0:
        increase_bp(user_id, total_bp, reason="activity", db=db)

# SP計算ロジック
def calc_sp_for_steps_and_distance(mode: str, redemption: bool, step_count: int, distance_km: float) -> tuple[int, dict, str]:
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
    sp = int((value // unit) * gain)
    detail = {"mode": mode, key: value, "redemption": redemption, "source": key}
    return sp, detail, key


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
        sp, detail, key = calc_sp_for_steps_and_distance(mode, redemption, step_count, distance_km)
    elif mode in ("mvp", "photo", "wake"):
        sp, detail = calc_sp_for_event(mode)
        key = None
    else:
        return 0

    if sp <= 0:
        return 0

    today_total = get_today_sp(user_id, week_id, db)
    remaining = SP_DAY_CAP - today_total
    if remaining <= 0:
        return 0

    total_sp = min(sp, remaining)
    record = get_sp_record_by_date(user_id, mode, today, db)

    if record:
        if key and detail[key] <= record.detail.get(key, 0):
            return 0
        delta_sp = total_sp - record.sp
        if delta_sp <= 0:
            return 0
        update_sp_record(record, total_sp, detail, db)
        return delta_sp
    else:
        add_sp_record(user_id, week_id, today, total_sp, mode, detail, db)
        return total_sp
    
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

