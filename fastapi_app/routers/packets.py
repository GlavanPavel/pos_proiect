from fastapi import APIRouter
from .deps import SessionDep

router = APIRouter(prefix="/event-packets", tags=["event-packets"])

@router.get("/{id}")
async def get_packet(id: int):
    return {"event_packet_id": id}

@router.get("/{id}/events")
async def get_packet_events(id: int):
    return {"event_packet_id": id}

@router.get("/{event_packet_id}/event/tickets/{ticket_id}")
async def get_packet_ticket(event_packet_id: int, ticket_id: int):
    return {"event_packet_id": event_packet_id, "ticket_id": ticket_id}
