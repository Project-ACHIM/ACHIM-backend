from backend.db.models.common import *

class RankingResult(Base):
    __tablename__ = "ranking_results"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    week_id = Column(Integer, ForeignKey("weeks.id", ondelete="CASCADE"), nullable=False)
    total_sp = Column(Integer, nullable=False)
    rank = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="ranking_results")
    week = relationship("Week", back_populates="ranking_results")