from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.schemas.discount_ticket import DiscountTicketOut
from backend.crud import discount_ticket as crud
from backend.db.database import get_db

router = APIRouter()

@router.get("/tickets", response_model=list[DiscountTicketOut])
def list_tickets(db: Session = Depends(get_db)):
    return crud.get_all_tickets(db)