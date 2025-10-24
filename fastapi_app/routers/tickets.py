from fastapi import APIRouter
from .deps import SessionDep
from ..models import Bilet
router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.get("/{cod}")
async def get_ticket(cod: str):
    ticket = Bilet(cod=cod, pachetID=1, evenimentID=2)
    return ticket.cod