from typing import List, Optional
from pydantic import BaseModel
from pydantic.config import ConfigDict

# --- 追加: 画面用（my + ranks の最小集合） ---
class RankItem(BaseModel):
    user_id: int
    display_name: str
    total_sp: int
    rank: int
    avatar_url: Optional[str] = None  # 将来用（今は null でOK）

class GroupWeeklyRankingResponse(BaseModel):
    week_id: int
    group_id: int
    category: str
    my: RankItem
    ranks: List[RankItem]

class GroupMemberRank(BaseModel):
    user_id: int
    username: str
    total_sp: int
    rank: int
    # 最終日にのみ仕様
    bonus_sp: Optional[int] = None
    final_result_sp: Optional[int] = None

class GroupRankingResponse(BaseModel):
    week_id: int
    group_id: int
    category: str
    members: List[GroupMemberRank]
    is_final: bool

class MVPAwardOut(BaseModel):
    user_id: int
    username: str
    category: str
    score: int
    sp_bonus: int
    model_config = ConfigDict(from_attributes=True)

class MVPAwardResponse(BaseModel):
    week_id: int
    awards: List[MVPAwardOut]

class MVPCandidate(BaseModel):
    category: str
    user_id: int
    username: str
    score: int
    notes: str

class MVPCandidatesResponse(BaseModel):
    week_id: int
    candidates: List[MVPCandidate]
    is_final: bool