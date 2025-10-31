from fastapi import APIRouter, Request
from .deps import SessionDep
from ..models import Bilet
from ..schemas import BiletResponse, BiletCreate
from ..services import get_ticket, create_ticket, update_ticket, delete_ticket

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.get(
    "/{cod}",
    name="get_ticket",
    response_model=BiletResponse
)
async def get_ticket_route(
        cod: str,
        session: SessionDep,
        request: Request
):
    return await get_ticket(cod, session, request)

@router.post(
    "/",
    name="create_ticket",
    response_model=BiletResponse
)
async def create_ticket_route(
        data: BiletCreate,
        session: SessionDep,
        request: Request
):
    return await create_ticket(data, session, request)

@router.put(
    "/{cod}",
    name="update_ticket",
    response_model=BiletResponse
)
async def update_ticket_route(
        cod: str,
        data: BiletCreate,
        session: SessionDep,
        request: Request
):
    return await update_ticket(cod, data, session, request)

@router.delete(
    "/{cod}",
    name="delete_ticket",
)
async def delete_ticket_route(
        cod: str,
        session: SessionDep
):
    return await delete_ticket(cod, session)