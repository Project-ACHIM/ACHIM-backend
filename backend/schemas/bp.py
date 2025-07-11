from pydantic import BaseModel

class BPAddByStepsRequest(BaseModel):
    user_id: int
    steps: int

class BPDecreaseRequest(BaseModel):
    user_id: int
    amount: int

class BPBalanceResponse(BaseModel):
    user_id: int
    current_bp: int

class BPAddByDistanceRequest(BaseModel):
    user_id: int
    week_id: int
    steps: int
    distance_km: float
    mode: str  # "walking", "running", etc.
    redemption: bool = False

