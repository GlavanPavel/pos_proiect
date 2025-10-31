from fastapi import APIRouter, Depends,Query, HTTPException, Request, status
from sqlalchemy import select

from .deps import SessionDep
from .. import services
from ..models import Eveniment
from fastapi_app.schemas.eveniment import EvenimentSchema, EvenimentUpdate, EvenimentCreate, EvenimentLinks, \
    EvenimentResponse, EvenimentCollectionResponse
from ..schemas import PaginatedResponse, EventFilterParams
from ..schemas.bilet import BiletResponse
from ..schemas.pachet import PachetCollectionResponse
from ..services import paginate, _build_event_response, get_all_events

router = APIRouter(prefix="/events", tags=["events"])

@router.get(
    "/",
    name="get_all_events",
    response_model=PaginatedResponse[EvenimentResponse]
)
async def get_all_events_route(
        session: SessionDep,
        page: int = Query(1, ge=1),
        per_page: int = Query(10, ge=1, le=100),
        filters: EventFilterParams = Depends()
):
    builder = _build_event_response
    return await get_all_events(
        page=page,
        per_page=per_page,
        session=session,
        filters=filters
    )


@router.get(
    "/{id}",
    response_model=EvenimentResponse,
    name="get_event"
)
async def get_event(
        request: Request,
        session: SessionDep,
        id: int
):
    return await services.get_event(session, id, request)

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="delete_event"
)
async def delete_event(
        session: SessionDep,
        id: int
):
    return await services.delete_event(session, id)

@router.put(
    "/{id}",
    response_model=EvenimentResponse,
    name="put_event"
)
async def update_event(
        session: SessionDep,
        id: int,
        event: EvenimentUpdate,
        request: Request
):
    return await services.update_event(session, id, event, request)

@router.post(
    "/",
    response_model=EvenimentResponse,
    name="create_event"
)
async def create_event(
        session: SessionDep,
        event: EvenimentCreate,
        request: Request
):
    return await services.create_event(session, event, request)

@router.get(
    "/{id}/event-packets",
    response_model=PachetCollectionResponse,
    name="get_event_packets"
)
async def get_event_packets(
        session: SessionDep,
        id: int,
        request: Request
):
    return await services.get_event_packets(session, id, request)

@router.get(
    "/{event_id}/tickets/{ticket_cod}",
    response_model=BiletResponse,
    name="get_event_ticket"
)
async def get_event_ticket(
        event_id: int,
        ticket_cod: str,
        session: SessionDep,
        request: Request
):
    return await services.get_event_ticket(event_id, ticket_cod, session, request)