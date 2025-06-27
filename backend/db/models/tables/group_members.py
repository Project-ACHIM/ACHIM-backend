from db.models.common import *

class GroupMember(Base):
    __tablename__ = 'group_members'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    joined_at = Column(TIMESTAMP, server_default=func.now())

    # リレーション
    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="group_memberships")