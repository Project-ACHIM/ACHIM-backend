# models/group_ranking_current_view.py

from backend.db.models.common import *

class GroupRankingCurrentView(Base):
    __tablename__ = "group_ranking_current_view"
    __table_args__ = {'extend_existing': True}
    __mapper_args__ = {"primary_key": ['group_id', 'user_id', 'date']}  # 仮のPK

    group_id = Column(Integer)
    user_id = Column(Integer)
    user_name = Column(String)
    date = Column(Date)
    mission_type = Column(String)
    sp = Column(Integer)
    detail = Column(JSON)
    total_sp = Column(Integer)
    rank = Column(Integer)
