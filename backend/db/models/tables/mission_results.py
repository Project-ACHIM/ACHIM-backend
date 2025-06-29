from backend.db.models.common import *

class MissionResult(Base):
    __tablename__ = 'mission_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    mission_type = Column(String(30), nullable=False)  # wakeup, step, photo, etc.
    date = Column(Date, nullable=False)
    status = Column(String(20))                        # success / failed / invalid
    detail = Column(JSONB)                             # 歩数や位置、画像情報など
    sp_earned = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # リレーション
    user = relationship("User", back_populates="mission_results")