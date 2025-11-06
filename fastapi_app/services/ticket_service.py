import secrets

from urllib.request import Request
from fastapi import HTTPException, Response, status
from fastapi_app.models import Bilet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from fastapi_app.schemas import BiletResponse, BiletCreate
from .builder import _build_bilet_response
from .helper import _get_ticket_db, _get_pachet_db, _get_event_db, get_pachet_availability, get_event_available_seats


async def get_ticket(cod: str, session: AsyncSession, request: Request) -> BiletResponse:
    ticket = await _get_ticket_db(cod, session)
    return _build_bilet_response(ticket, request)

async def verify_ticket(data: BiletCreate, session: AsyncSession):
    if data.pachetID is None and data.evenimentID is None:
        raise HTTPException(
            status_code=400,
            detail="Biletul trebuie asociat unui eveniment sau pachet"
        )
    elif data.pachetID is not None and data.evenimentID is not None:
        raise HTTPException(
            status_code=400,
            detail="Biletul trebuie asociat doar unui eveniment sau pachet"
        )

    if data.pachetID is not None:
        await _get_pachet_db(session, data.pachetID)
        available = await get_pachet_availability(session, data.pachetID)

        if available <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"Nu mai sunt bilete disponibile pentru pachetul {data.pachetID}."
            )
    elif data.evenimentID is not None:
        eveniment = await _get_event_db(session, data.evenimentID)
        available = await get_event_available_seats(session, eveniment)

        if available <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"Nu mai sunt bilete disponibile pentru evenimentul {data.evenimentID}."
            )


async def create_ticket(data: BiletCreate, session: AsyncSession, request: Request) -> BiletResponse:
    await verify_ticket(data, session)

    new_cod = secrets.token_hex(12)

    # se verifica daca codul e unic
    result = await session.execute(select(Bilet).where(Bilet.cod == new_cod))
    while result.scalars().first():
        new_cod = secrets.token_hex(12)
        result = await session.execute(select(Bilet).where(Bilet.cod == new_cod))

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