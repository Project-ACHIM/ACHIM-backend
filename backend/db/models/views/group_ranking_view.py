from db.models.common import *

class GroupRankingView(Base):
    __table__ = Table(
        "group_ranking_view",
        metadata,
        Column("group_id", Integer, primary_key=True),
        Column("user_id", Integer, primary_key=True),
        Column("user_name", String),
        Column("total_sp", Integer),
        Column("rank", Integer),
        autoload_with=engine
    )