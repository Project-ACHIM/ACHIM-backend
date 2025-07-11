from backend.db.models.common import *

# --- sp_records ---
class SPRecord(Base):
    __tablename__ = "sp_records"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    week_id = Column(Integer, ForeignKey("weeks.id"))
    date = Column(Date, nullable=False)
    sp = Column(Integer, nullable=False)
    detail = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="sp_records")