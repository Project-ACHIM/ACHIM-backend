from db.models.common import *

class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    week_id = Column(Integer, ForeignKey('weeks.id'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # リレーション（必要に応じて）
    week = relationship("Week", back_populates="groups")
    bp_entries = relationship("BpEntry", back_populates="groups")
    members = relationship("GroupMember", back_populates="groups")