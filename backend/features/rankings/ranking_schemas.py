from typing import List
from pydantic import BaseModel

class GroupMemberRank(BaseModel):
    user_id: int
    username: str
    total_sp: int
    rank: int

class GroupRankingResponse(BaseModel):
    week_id: int
    group_id: int
    category: str
    members: List[GroupMemberRank]