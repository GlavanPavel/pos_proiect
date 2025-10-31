from typing import List
import logging
from fastapi import HTTPException, Request, Response, status

from fastapi_app.models import Pachet, JoinPE, Bilet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from .builder import _build_pachet_response, _build_event_response, _build_bilet_links, _build_bilet_response
from ..schemas import PachetCreate, EvenimentCollectionResponse, EvenimentResponse, Link, BiletSchema, BiletWithLinks, \
    BiletResponse, PachetResponse
from ..schemas.eveniment import EvenimentCollectionLinks

log = logging.getLogger("uvicorn.error")

async def _get_pachet_db(session: AsyncSession, id: int) -> Pachet:
    result = await session.execute(select(Pachet).where(Pachet.id == id))
    packet = result.scalars().first()
    if not packet:
        raise HTTPException(status_code=404, detail="Packet not found")
    return packet


async def get_pachet(id, session, request) -> PachetResponse:
    packet = await _get_pachet_db(session, id)
    return _build_pachet_response(packet, request)


async def create_pachet(data: PachetCreate, session: AsyncSession, request: Request) -> PachetResponse:
    pachet = Pachet(**data.model_dump())
    session.add(pachet)
    await session.commit()
    await session.refresh(pachet)

    return _build_pachet_response(pachet, request)


async def update_pachet(id: int, data: PachetCreate, session: AsyncSession, request: Request) -> PachetResponse:
    result = await session.execute(select(Pachet).where(Pachet.id == id))
    pachet = result.scalars().first()
    if not pachet:
        pachet = Pachet(id=id, **data.model_dump())
    else:
        update_data = data.model_dump()
        for field, value in update_data.items():
            setattr(pachet, field, value)

    session.add(pachet)
    await session.commit()
    await session.refresh(pachet)
    return _build_pachet_response(pachet, request)


async def delete_pachet(id: int, session: AsyncSession):
    pachet = await _get_pachet_db(session, id)
    await session.delete(pachet)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

async def get_pachet_events(id: int, session: AsyncSession, request: Request) -> EvenimentCollectionResponse:
    query = (
        select(Pachet)
        .where(Pachet.id == id)
        .options(
            joinedload(Pachet.pachet_associations)
            .joinedload(JoinPE.eveniment)
        )
    )

    result = await session.execute(query)
    pachet = result.scalars().first()

    if not pachet:
        raise HTTPException(status_code=404, detail="Packet not found")

    evenimente_list: List[EvenimentResponse] = []
    for eveniment in pachet.evenimente:
        evenimente_list.append(
            _build_event_response(eveniment, request)
        )

    collection_self_href = request.url_for("get_pachet_events", id=id)
    collection_parent_href = request.url_for("get_pachet", id=id)

    collection_links = EvenimentCollectionLinks(
        self=Link(href=str(collection_self_href), method="GET"),
        parent=Link(href=str(collection_parent_href), method="GET")
    )

    return EvenimentCollectionResponse(
        evenimente=evenimente_list,
        _links=collection_links
    )

async def get_pachet_ticket(pachet_id: int, ticket_cod: str, session: AsyncSession, request: Request) -> BiletResponse:
    await _get_pachet_db(session, pachet_id)
    query = (
        select(Bilet)
        .where(Bilet.cod == ticket_cod)
        .where(Bilet.pachetID == pachet_id)
    )

    res = await session.execute(query)
    ticket = res.scalars().first()
    if not ticket:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket with code {ticket_cod} not found for packet {pachet_id}"
        )

    return _build_bilet_response(ticket, request)