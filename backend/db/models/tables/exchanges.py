from db.models.common import *
from sqlalchemy import Column,Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.db.database import Base #既存のBaseクラスを使用

class Exchange(Base):
    __tablename__ = "exchanges"

    exchange_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), nullable=False)
    coupon_id = Column(Integer, ForeignKey("discount_tickets.coupon_id"), nullable=False)
    exchanged_at = Column(DateTime(timezone=True), server_default=func.now())