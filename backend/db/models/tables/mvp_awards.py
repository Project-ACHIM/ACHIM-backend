from backend.db.models.common import *

class MVPAward(Base):
    __tablename__ = "mvp_awards"

    id = Column(Integer, primary_key=True)
    week_id = Column(Integer, ForeignKey("weeks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False)
    score = Column(Integer, nullable=False)
    sp_bonus = Column(Integer, default=0, nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("week_id", "user_id", "category", name="uq_mvp_week_user_category"),
        Index("idx_mvp_week_user", "week_id", "user_id"),
    )