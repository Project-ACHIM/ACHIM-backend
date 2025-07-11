from backend.db.models.common import *

class Point(Base):
    __tablename__ = "points"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    bp_total = Column(Integer, default=0, nullable=False)
    bet_bp_pending = Column(Integer, default=0, nullable=False)