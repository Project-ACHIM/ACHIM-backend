from sqlalchemy.orm import Session
from backend.db.models.tables.discount_tickets import DiscountTicket

def get_all_tickets(db: Session):
    return db.query(DiscountTicket).all()