from enum import Enum
from typing import Annotated
from pydantic import BaseModel, Field

class GroupCategory(str, Enum):
    running = "running"
    walking = "walking"

BetBP = Annotated[int, Field(ge=100, le=10_000, description="賭けBPは100〜10,000pt")]

class JoinRequest(BaseModel):
    user_id: int
    category: GroupCategory
    bet_bp: BetBP

class JoinResponse(BaseModel):
    message: str
    week_id: int
    group_id: int
    category: GroupCategory
    bet_bp: int
    bp_balance: int

class StatusResponse(BaseModel):
    week_id: int
    is_joined: bool
