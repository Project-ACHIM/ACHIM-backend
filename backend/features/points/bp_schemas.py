from pydantic import BaseModel, Field
from enum import Enum
from typing import Literal
from pydantic import ConfigDict

# BP減少の理由を定義
class BPDecreaseReason(str, Enum):
    BET = "bet"                   # 賭けに使用
    EXCHANGE = "exchange"         # チケットなどとの交換
    RANKING = "ranking"           # ランキング結果による減少
    LOST = "lost"                 # 有効期限切れや喪失など

# 歩数+kmによるBP付与リクエスト
class BPAddActivityRequest(BaseModel):
    user_id: int = Field(..., description="ユーザーID")
    steps: int = Field(0, ge=0, description="歩数")
    distance_km: float = Field(0.0, ge=0, description="移動距離（km）")

    # 既存クライアントから余分なフィールドが来ても無視する
    model_config = ConfigDict(extra="ignore")

# BP消費・減少リクエスト
class BPDecreaseRequest(BaseModel):
    user_id: int = Field(..., description="ユーザーID")
    amount: int = Field(..., gt=0, description="減らすBP量（マイナスではなく絶対値）")
    reason: Literal["bet", "exchange", "ranking", "lost"] = Field(..., description="BP減少の理由")
    detail: str | None = Field(None, description="補足説明（例: ランキング順位や交換アイテム名など）")

# BP量を返すリクエスト
class BPBalanceResponse(BaseModel):
    user_id: int
    current_bp: int

# ランキング報酬によるBP増加リクエスト
class BPRewardFromRankingRequest(BaseModel):
    user_id: int = Field(..., description="ユーザーID")
    week_id: int = Field(..., description="ランキング対象の週ID")
    rank: int = Field(..., gt=0, description="ランキング順位（1位、2位など）")
    bp_reward: int = Field(..., gt=0, description="付与するBP量")

# その他の報酬（使うかわからない）
class BPBonusReason(str, Enum):
    WAKE = "wake"
    PHOTO = "photo"
    MVP = "mvp"
    EVENT = "event"

# その他の報酬によるBP増加リクエスト
class BPBonusRequest(BaseModel):
    user_id: int = Field(..., description="ユーザーID")
    week_id: int = Field(..., description="対象の週ID")
    amount: int = Field(..., gt=0, description="付与するBP量")
    reason: BPBonusReason = Field(..., description="報酬の種類")
    detail: str | None = Field(None, description="補足情報（例：起床時間やイベント名など）")

