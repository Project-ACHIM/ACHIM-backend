
from typing import Dict
from pydantic import BaseModel, Field
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

class SPChangeResponse(BaseModel):
    user_id: int
    delta_sp: int = Field(..., description="今回加算されたSP")
    today_total_sp: int = Field(..., description="今日の合計SP")
    week_total_sp: int = Field(..., description="週合計SP")

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

