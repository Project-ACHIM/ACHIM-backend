from pydantic import BaseModel
from enum import Enum

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

