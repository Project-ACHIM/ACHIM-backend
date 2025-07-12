from backend.db.models.common import *
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

# 割引券テーブルのモデル
class DiscountTicket(Base):
    __tablename__ = "discount_tickets" # データベース上のテーブル名

    coupon_id = Column(Integer, primary_key=True, autoincrement=True)# クーポンID（主キー、自動採番）
    ticket_name = Column(String(100),nullable=False)# 商品名
    description = Column(Text)# 商品の詳細説明
    point_cost = Column(Integer, nullable=False)# このクーポンを交換するために必要なBPポイント
    image_url = Column(String(255))# 商品画像のURL（
    created_at = Column(DateTime(timezone=True),server_default=func.now()) # 登録日時（デフォルトで現在時刻）
    update_at = Column(DateTime(timezone=True),onupdate=func.now())# 更新日時（更新時に自動で現在時刻をセット）