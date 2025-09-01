from sqlalchemy.orm import Session
from datetime import date as DateType
from backend.db.models.tables.bp_ingest_cursors import BpIngestCursor

def get_cursor(db: Session, user_id: int, on_date: DateType) -> BpIngestCursor | None:
    return (
        db.query(BpIngestCursor)
        .filter(
            BpIngestCursor.user_id == user_id,
            BpIngestCursor.date == on_date,
        )
        .first()
    )

def upsert_cursor(
    db: Session,
    user_id: int,
    on_date: DateType,
    last_walk_units: int,
    last_run_units: int,
    last_steps_total: int,
    last_distance_total_km: float,
) -> BpIngestCursor:
    cur = get_cursor(db, user_id, on_date)
    if cur:
        cur.last_walk_units = last_walk_units
        cur.last_run_units = last_run_units
        cur.last_steps_total = last_steps_total
        cur.last_distance_total_km = last_distance_total_km
    else:
        cur = BpIngestCursor(
            user_id=user_id,
            date=on_date,
            last_walk_units=last_walk_units,
            last_run_units=last_run_units,
            last_steps_total=last_steps_total,
            last_distance_total_km=last_distance_total_km,
        )
        db.add(cur)
    db.commit()
    db.refresh(cur)
    return cur
