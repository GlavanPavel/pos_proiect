from fastapi import APIRouter, Request, Query, Depends, status
from .deps import SessionDep
from fastapi_app import services
from fastapi_app.schemas.pachet import (
    PachetCreate,
    PachetResponse,
)
from sqlalchemy import select
from fastapi_app.schemas.bilet import BiletResponse
from fastapi_app.schemas.eveniment import EvenimentCollectionResponse
from ..models import Eveniment, Pachet
from ..schemas import PaginatedResponse
from ..services import _build_pachet_response, paginate

router = APIRouter(prefix="/event-packets", tags=["pachete"])

@router.get(
    "/",
    name="get_all_packets",
    response_model=PaginatedResponse[PachetResponse]
)
async def get_all_events_route(
        session: SessionDep,
        page: int = Query(1, ge=1),
        per_page: int = Query(10, ge=1, le=100)
):
    builder = _build_pachet_response
    return await paginate(
        query=select(Pachet),
        page=page,
        per_page=per_page,
        session=session,
        builder=builder
    )


@router.get(
    "/{id}",
    name="get_pachet",
    response_model=PachetResponse
)
async def get_pachet_route(
        id: int,
        session: SessionDep,
        request: Request
):
    return await services.get_pachet(id, session, request)

@router.post(
    "/",
    name="create_pachet",
    response_model=PachetResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_pachet_route(
        data: PachetCreate,
        session: SessionDep,
        request: Request
):
    return await services.create_pachet(data, session, request)

@router.put(
    "/{id}",
    name="update_pachet",
    response_model=PachetResponse
)
async def update_pachet_route(
        id: int,
        data: PachetCreate,
        session: SessionDep,
        request: Request
):
    return await services.update_pachet(id, data, session, request)

@router.delete(
    "/{id}",
    name="delete_pachet",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_pachet_route(
        id: int,
        session: SessionDep
):
    return await services.delete_pachet(id, session)

@router.get(
    "/{id}/events",
    name="get_pachet_events",
    response_model=EvenimentCollectionResponse
)
async def get_pachet_events_route(
        id: int,
        session: SessionDep,
        request: Request
):
    return await services.get_pachet_events(id, session, request)

@router.get(
    "/{pachet_id}/tickets/{ticket_cod}",
    name="get_pachet_ticket",
    response_model=BiletResponse
)
async def get_pachet_ticket_route(
        pachet_id: int,
        ticket_cod: str,
        session: SessionDep,
        request: Request
):
    return await services.get_pachet_ticket(pachet_id, ticket_cod, session, request)
