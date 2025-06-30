from backend.db.models.common import *

class BpEntry(Base):
    __tablename__ = 'bp_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    bet_bp = Column(Integer, nullable=False)
    result_bp = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        UniqueConstraint('user_id', 'group_id', name='uq_user_group'),
    )

    # Optional: リレーション（必要に応じて）
    user = relationship("User", back_populates="bp_entries")
    group = relationship("Group", back_populates="bp_entries")
    group = relationship("Group", back_populates="members")