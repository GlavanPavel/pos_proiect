from typing import List
from fastapi import Request, HTTPException, Response, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from fastapi_app.models import Eveniment, JoinPE, Bilet
from fastapi_app.schemas.bilet import BiletSchema, BiletResponse, BiletWithLinks
from fastapi_app.schemas.eveniment import (
    EvenimentResponse,
    EvenimentUpdate,
    EvenimentCreate, EvenimentCollectionResponse, EvenimentCollectionLinks,
)
from fastapi_app.schemas.link import Link
from fastapi_app.schemas.pachet import PachetResponse, PachetCollectionResponse, \
    PachetCollectionLinks
from .pagination import paginate
from .builder import _build_event_response, _build_pachet_response, _build_bilet_links, _build_bilet_response
from ..schemas import EventFilterParams, PaginatedResponse


async def _get_event_db(session: AsyncSession, id: int) -> Eveniment:
    result = await session.execute(select(Eveniment).where(Eveniment.id == id))
    event = result.scalars().first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


async def get_all_events(
        session: AsyncSession,
        page: int,
        per_page: int,
        filters: EventFilterParams
) -> PaginatedResponse[EvenimentResponse]:
    query = select(Eveniment)
    filter_conditions = []

    if filters.location:
        filter_conditions.append(Eveniment.locatie == filters.location)

    if filters.name:
        filter_conditions.append(Eveniment.nume.ilike(f"%{filters.name}%"))

    if filters.available_tickets is not None:
        sold_tickets_sq = (
            select(func.count(Bilet.cod))
            .where(Bilet.evenimentID == Eveniment.id)
            .scalar_subquery()
        )
        available = func.coalesce(Eveniment.numarLocuri, 0) - func.coalesce(sold_tickets_sq, 0)
        filter_conditions.append(available >= filters.available_tickets)

    if filter_conditions:
        query = query.where(and_(*filter_conditions))

    query = query.order_by(Eveniment.id.desc())

    return await paginate(
        query=query,
        page=page,
        per_page=per_page,
        session=session,
        builder=_build_event_response
    )


async def get_event(session: AsyncSession, id: int, request: Request) -> EvenimentResponse:
    event = await _get_event_db(session, id)
    return _build_event_response(event, request)


async def create_event(session: AsyncSession, data: EvenimentCreate, request: Request) -> EvenimentResponse:
    event = Eveniment(**data.model_dump())
    session.add(event)
    await session.commit()
    await session.refresh(event)

    return _build_event_response(event, request)


async def update_event(session: AsyncSession, id: int, data: EvenimentUpdate, request: Request) -> EvenimentResponse:
    event = await _get_event_db(session, id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)

    session.add(event)
    await session.commit()
    await session.refresh(event)
    return _build_event_response(event, request)


async def delete_event(session: AsyncSession, id: int) -> dict:
    event = await _get_event_db(session, id)

    await session.delete(event)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def get_event_packets(session: AsyncSession, id: int, request: Request) -> PachetCollectionResponse:
    query = (
        select(Eveniment)
        .where(Eveniment.id == id)
        .options(
            joinedload(Eveniment.eveniment_associations)
            .joinedload(JoinPE.pachet)
        )
    )

    result = await session.execute(query)
    event = result.scalars().first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    pachete_list: List[PachetResponse] = []
    for pachet in event.pachete:
        pachete_list.append(
            _build_pachet_response(pachet, request)
        )

    collection_self_href = request.url_for("get_event_packets", id=id)
    collection_parent_href = request.url_for("get_event", id=id)

    collection_links = PachetCollectionLinks(
        self=Link(href=str(collection_self_href), method="GET"),
        parent=Link(href=str(collection_parent_href), method="GET")
    )

    return PachetCollectionResponse(
        _links=collection_links,
        pachete=pachete_list
    )


async def get_event_ticket(event_id, ticket_cod, session, request) -> BiletResponse:
    await _get_event_db(session, event_id) # pentru a verifica daca evenimentul exista

    query = (
        select(Bilet)
        .where(Bilet.cod == ticket_cod)
        .where(Bilet.evenimentID == event_id)
    )

    res = await session.execute(query)
    ticket = res.scalars().first()
    if not ticket:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket with code {ticket_cod} not found for event {event_id}"
        )

    return _build_bilet_response(ticket, request)