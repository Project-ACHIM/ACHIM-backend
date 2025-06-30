from db.models.common import *

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    week_id = Column(Integer, ForeignKey("weeks.id"), nullable=False)
    category = Column(String(30))  # 'running', 'walking' など
    created_at = Column(DateTime, server_default=func.now())

    week = relationship("Week", back_populates="groups")
    bp_entries = relationship("BpEntry", back_populates="groups")
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")