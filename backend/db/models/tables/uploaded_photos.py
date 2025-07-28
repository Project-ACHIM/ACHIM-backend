#from sqlalchemy import Date, DateTime, Column, ForeignKey, Integer, String
from backend.db.models.common import *


class UploadedPhoto(Base):
    __tablename__ = "uploaded_photos"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    filename = Column(String, nullable=False)
    url = Column(String, nullable=False)

    # 日付単位の管理
    upload_date = Column(Date, default=DateTime.utcnow().date)       # 1日単位
    uploaded_at = Column(DateTime, default=DateTime.utcnow)          # 時刻も欲しければ

    group = relationship("Group", back_populates="photos")
    user = relationship("User", back_populates="photos")
    votes = relationship("PhotoVote", back_populates="photo", cascade="all, delete")
