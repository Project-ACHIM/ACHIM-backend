from pydantic import BaseModel

class DiscountTicketOut(BaseModel):
    coupon_id: int
    ticket_name: str
    description: str | None
    point_cost: int
    image_url: str | None

    class Config:
        orm_mode = True