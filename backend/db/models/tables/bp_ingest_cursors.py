from backend.db.models.common import *

# HealthKitの『当日累積』を安全に差分化するためのカーソル。
# 同一ユーザー×日付×デバイスで、最後に処理した“単位数”を保持する。
class BpIngestCursor(Base):
    __tablename__ = "bp_ingest_cursors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)  # アプリTZでの“その日”

    # 最後に処理した“単位数”（歩・距離で割った整数）を保持
    last_walk_units = Column(Integer, default=0, nullable=False)
    last_run_units = Column(Integer, default=0, nullable=False)

    # 最後に見た累積原値も保持（デバッグ/監査用）
    last_steps_total = Column(BigInteger, default=0, nullable=False)
    last_distance_total_km = Column(Float, default=0.0, nullable=False)

    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_bp_cursor_user_date"),
        Index("idx_bp_cursor_user_date", "user_id", "date"),
    )