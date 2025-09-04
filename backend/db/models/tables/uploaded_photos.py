#from sqlalchemy import Date, DateTime, Column, ForeignKey, Integer, String
from backend.db.models.common import *
from datetime import datetime
from sqlalchemy import func

class UploadedPhoto(Base):
    __tablename__ = "uploaded_photos"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    filename = Column(String, nullable=False)
    url = Column(String, nullable=False)
    is_demo  = Column(Boolean, default=False, nullable=False)

    # 日付単位の管理
    upload_date = Column(Date, server_default=func.current_date())
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("Group", back_populates="photos")
    user = relationship("User", back_populates="photos")
    votes = relationship("PhotoVote", back_populates="photo", cascade="all, delete")
