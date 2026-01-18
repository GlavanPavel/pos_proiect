import secrets

from urllib.request import Request
from fastapi import HTTPException, Response, status
from fastapi_app.models import Bilet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from fastapi_app.schemas import BiletResponse, BiletCreate
from .builder import _build_bilet_response
from .helper import _get_ticket_db, _get_pachet_db, _get_event_db, get_pachet_availability, get_event_available_seats


async def get_ticket(cod: str, session: AsyncSession, request: Request, user_id: int, role: str) -> BiletResponse:
    ticket = await _get_ticket_db(cod, session)

    # Managerul poate vedea biletul doar dacă deține evenimentul/pachetul
    if role == "owner-event":
        is_owner = await _check_ticket_ownership_for_manager(session, ticket, user_id)
        if not is_owner:
            raise HTTPException(status_code=403, detail="Acces interzis")

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
    try:
        await session.commit()
        await session.refresh(ticket)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Eroare la salvarea biletului în baza de date SQL"
        )

    return _build_bilet_response(ticket, request)


async def update_ticket(cod: str, data: BiletCreate, session: AsyncSession, request: Request, user_id: int, role: str) -> BiletResponse:
    await verify_ticket(data, session)
    ticket = await _get_ticket_db(cod, session)

    if role == "owner-event":
        is_owner = await _check_ticket_ownership_for_manager(session, ticket, user_id)
        if not is_owner:
            raise HTTPException(status_code=403, detail="Nu puteti modifica biletele altor manageri")


    update_data = data.model_dump()
    for field, value in update_data.items():
        setattr(ticket, field, value)

    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    return _build_bilet_response(ticket, request)


async def delete_ticket(cod: str, session: AsyncSession, user_id: int, role: str):
    ticket = await _get_ticket_db(cod, session)

    if role == "owner-event":
        is_owner = await _check_ticket_ownership_for_manager(session, ticket, user_id)
        if not is_owner:
            raise HTTPException(status_code=403, detail="Acces interzis")

    await session.delete(ticket)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def _check_ticket_ownership_for_manager(session: AsyncSession, ticket: Bilet, user_id: int) -> bool:
    if ticket.evenimentID:
        event = await _get_event_db(session, ticket.evenimentID)
        return event.id_owner == user_id
    if ticket.pachetID:
        packet = await _get_pachet_db(session, ticket.pachetID)
        return packet.id_owner == user_id
    return False