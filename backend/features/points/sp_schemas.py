
from typing import Dict
from pydantic import BaseModel
from enum import Enum
from datetime import date

class SPMode(str, Enum):
    walking = "walking"
    running = "running"
    photo = "photo"
    mvp = "mvp"
    wake = "wake"

class SPAddRequest(BaseModel):
    user_id: int
    week_id: int
    steps: int
    distance_km: float
    mode: SPMode
    redemption: bool = False

class SPBalanceResponse(BaseModel):
    user_id: int
    current_sp: int

class SPEventRequest(BaseModel):
    user_id: int
    week_id: int
    mode: str

class BreakdownBySource(BaseModel):
    by_source: Dict[str, int]
    total: int

class SPBreakdownResponse(BaseModel):
    user_id: int
    breakdown: BreakdownBySource

