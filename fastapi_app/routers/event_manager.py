from fastapi import APIRouter
from . import events, packets, tickets

router = APIRouter(prefix="/event-manager", tags=["event-manager"])
router.include_router(events.router)
router.include_router(packets.router)
router.include_router(tickets.router)
