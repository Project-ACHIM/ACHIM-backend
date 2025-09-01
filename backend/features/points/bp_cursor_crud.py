from sqlalchemy.orm import Session
from datetime import date as DateType
from backend.db.models.tables.bp_ingest_cursors import BpIngestCursor

def get_cursor(db: Session, user_id: int, on_date: DateType, device_id: str | None) -> BpIngestCursor | None:
    return (
        db.query(BpIngestCursor)
        .filter(
            BpIngestCursor.user_id == user_id,
            BpIngestCursor.date == on_date,
            BpIngestCursor.device_id.is_(device_id) if device_id is None else BpIngestCursor.device_id == device_id
        )
        .first()
    )

def upsert_cursor(
    db: Session,
    user_id: int,
    on_date: DateType,
    device_id: str | None,
    last_walk_units: int,
    last_run_units: int,
    last_steps_total: int,
    last_distance_total_km: float,
) -> BpIngestCursor:
    cur = get_cursor(db, user_id, on_date, device_id)
    if cur:
        cur.last_walk_units = last_walk_units
        cur.last_run_units = last_run_units
        cur.last_steps_total = last_steps_total
        cur.last_distance_total_km = last_distance_total_km
    else:
        cur = BpIngestCursor(
            user_id=user_id,
            date=on_date,
            device_id=device_id,
            last_walk_units=last_walk_units,
            last_run_units=last_run_units,
            last_steps_total=last_steps_total,
            last_distance_total_km=last_distance_total_km,
        )
        db.add(cur)
    db.commit()
    db.refresh(cur)
    return cur
