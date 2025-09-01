from backend.db.models.common import *

# --- sp_records ---
class SPRecord(Base):
    __tablename__ = "sp_records"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    week_id = Column(Integer, ForeignKey("weeks.id"))
    date = Column(Date, nullable=False)
    sp = Column(Integer, nullable=False)
    mode = Column(String, nullable=False)
    detail = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="sp_records")

    __table_args__ = (
        UniqueConstraint("user_id", "week_id", "date", "mode", name="uq_sp_user_week_date_mode"),
        Index("idx_sp_user_week_date", "user_id", "week_id", "date"),
    )