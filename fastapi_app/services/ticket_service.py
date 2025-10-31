import secrets

from urllib.request import Request
from fastapi import HTTPException, Response, status
from fastapi_app.models import Bilet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi_app.schemas import BiletResponse, BiletCreate
from .builder import _build_bilet_response
from .event_service import _get_event_db
from .packet_service import _get_pachet_db


async def _get_ticket_db(cod, session):
    result = await session.execute(select(Bilet).where(Bilet.cod == cod))
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Bilt not found")
    return ticket

async def get_ticket(cod: str, session: AsyncSession, request: Request) -> BiletResponse:
    ticket = await _get_ticket_db(cod, session)
    return _build_bilet_response(ticket, request)

async def verify_ticket(data: BiletCreate, session: AsyncSession):
    if data.pachetID is None and data.evenimentID is None:
        raise HTTPException(
            status_code=400,
            detail="Ticket must be linked to either a pachetID or an evenimentID."
        )
    elif data.pachetID is not None and data.evenimentID is not None:
        raise HTTPException(
            status_code=400,
            detail="Ticket cannot be linked to both a pachetID and an evenimentID."
        )

    # verific daca exista parintele aferent biletului
    if data.pachetID is not None:
        await _get_pachet_db(session, data.pachetID)
    elif data.evenimentID is not None:
        await _get_event_db(session, data.evenimentID)

async def create_ticket(data: BiletCreate, session: AsyncSession, request: Request) -> BiletResponse:
    await verify_ticket(data, session)
    new_cod = secrets.token_hex(12)

    # verific unicitatea codului
    result = await session.execute(select(Bilet).where(Bilet.cod == new_cod))
    existing_ticket = result.scalars().first()

    while existing_ticket:
        new_cod = secrets.token_hex(12)
        result = await session.execute(select(Bilet).where(Bilet.cod == new_cod))
        existing_ticket = result.scalars().first()

    ticket = Bilet(
        cod=new_cod,
        pachetID=data.pachetID,
        evenimentID=data.evenimentID
    )

    session.add(ticket)
    await session.commit()

    return _build_bilet_response(ticket, request)

async def update_ticket(cod: str, data: BiletCreate, session: AsyncSession, request: Request) -> BiletResponse:
    await verify_ticket(data, session)

    ticket = await _get_ticket_db(cod, session)

    update_data = data.model_dump()
    for field, value in update_data.items():
        setattr(ticket, field, value)

    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    return _build_bilet_response(ticket, request)

async def delete_ticket(cod: str, session: AsyncSession):
    ticket = await _get_ticket_db(cod, session)

    await session.delete(ticket)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)