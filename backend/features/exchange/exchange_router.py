from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.features.exchange.exchange_schemas import DiscountTicketOut
from backend.features.exchange import exchange_crud as crud
from backend.db.session import get_db
router = APIRouter()

@router.get("/tickets", response_model=list[DiscountTicketOut])
def list_tickets(db: Session = Depends(get_db)):
    return crud.get_all_tickets(db)