# models/group_ranking_view.py

from backend.db.models.common import *


class GroupRankingView(Base):
    __tablename__ = 'group_ranking_view'
    __table_args__ = {'extend_existing': True}
    __mapper_args__ = {'primary_key': ['group_id', 'user_id']}

    group_id = Column(Integer)
    user_id = Column(Integer)
    user_name = Column(String)
    total_sp = Column(Integer)
    rank = Column(Integer)
