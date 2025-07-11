from backend.db.models.common import *

class UserWeekPreference(Base):
    __tablename__ = "user_week_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_id = Column(Integer, ForeignKey("weeks.id"), nullable=False)
    category = Column(String(20), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "week_id", name="uq_user_week"),
    )

    # リレーション
    user = relationship("User", back_populates="week_preferences")
    week = relationship("Week", back_populates="user_preferences")