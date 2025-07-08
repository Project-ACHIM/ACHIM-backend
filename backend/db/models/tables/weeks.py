from backend.db.models.common import *


class Week(Base):
    __tablename__ = 'weeks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(20), default='scheduled')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    groups = relationship("Group", back_populates="week", cascade="all, delete-orphan")
    ranking_results = relationship("RankingResult", back_populates="week", cascade="all, delete-orphan")
    user_preferences = relationship("UserWeekPreference", back_populates="week", cascade="all, delete-orphan")