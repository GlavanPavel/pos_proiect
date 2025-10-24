from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select

from .deps import SessionDep
from .. import services
from ..models import Eveniment
from fastapi_app.schemas.eveniment import EvenimentSchema, EvenimentUpdate, EvenimentCreate, EvenimentLinks, \
    EvenimentResponse

router = APIRouter(prefix="/events", tags=["events"])

@router.get(
    "/",
    name="get_all_events"
)
async def get_all_events(
    request: Request,
    session: SessionDep
):
    pass

@router.get(
    "/{id}",
    response_model=EvenimentResponse)
async def get_event(
        request: Request,
        session: SessionDep,
        id: int
):
    return await services.get_event(session, id, request)

@router.delete(
    "/{id}"
)
async def delete_event(
        session: SessionDep,
        id: int
):
    return await services.delete_event(session, id)

@router.put(
    "/{id}",
    response_model=EvenimentSchema
)
async def update_event(
        session: SessionDep,
        id: int,
        event: EvenimentUpdate
):
    return await services.update_event(session, id, event)

@router.post(
    "/",
    response_model=EvenimentSchema
)
async def create_event(
        session: SessionDep,
        event: EvenimentCreate
):
    return await services.create_event(session, event)

@router.get("/{id}/event-packets")
async def get_event_packets(id: int):
    return {"event_id": id}

@router.get("/{event_id}/tickets/{ticket_id}")
async def get_event_ticket(event_id: int, ticket_id: int):
    return {"event_id": event_id, "ticket_id": ticket_id}