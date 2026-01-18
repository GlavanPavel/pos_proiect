from typing import List
from fastapi import Request, HTTPException, Response, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from fastapi_app.models import Eveniment, JoinPE, Bilet
from fastapi_app.schemas.bilet import BiletResponse
from fastapi_app.schemas.eveniment import (
    EvenimentResponse,
    EvenimentUpdate,
    EvenimentCreate, )
from fastapi_app.schemas.link import Link
from fastapi_app.schemas.pachet import PachetResponse, PachetCollectionResponse, \
    PachetCollectionLinks
from .helper import _get_event_db
from fastapi_app.core.pagination import paginate
from .builder import _build_event_response, _build_pachet_response, _build_bilet_response
from ..schemas import EventFilterParams, PaginatedResponse


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
        # nr de bilete vandute direct
        sold_individually_sq = (
            select(func.count(Bilet.cod))
            .where(Bilet.evenimentID == Eveniment.id)
            .scalar_subquery()
        )

        # nr de bilete rezervate unui pachet
        allocated_to_packets_sq = (
            select(func.sum(JoinPE.numarLocuri))
            .where(JoinPE.evenimentID == Eveniment.id)
            .scalar_subquery()
        )

        available = (
                func.coalesce(Eveniment.numarLocuri, 0) -
                func.coalesce(allocated_to_packets_sq, 0) -
                func.coalesce(sold_individually_sq, 0)
        )

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


async def create_event(
        session: AsyncSession,
        data: EvenimentCreate,
        request: Request,
        owner_id: int
) -> EvenimentResponse:
    event_dict = data.model_dump()
    # id-ul e luat din token
    event_dict["id_owner"] = owner_id

    event = Eveniment(**event_dict)
    session.add(event)
    await session.commit()
    await session.refresh(event)

    return _build_event_response(event, request)


async def update_event(session: AsyncSession, id: int, data: EvenimentUpdate, request: Request, user_id: int, role: str) -> EvenimentResponse:
    event = await _get_event_db(session, id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)

    session.add(event)
    await session.commit()
    await session.refresh(event)
    return _build_event_response(event, request)


async def delete_event(session: AsyncSession, id: int, user_id: int, role: str):
    event = await _get_event_db(session, id)

    sold_query = select(func.count(Bilet.cod)).where(Bilet.evenimentID == id)
    sold_tickets = (await session.execute(sold_query)).scalar_one()

    if sold_tickets > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Evenimentul nu poate fi sters. {sold_tickets} bilete au fost vandute pentru el."
        )

    join_query = select(func.count(JoinPE.pachetID)).where(JoinPE.evenimentID == id)
    associated_packets = (await session.execute(join_query)).scalar_one()

    if associated_packets > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Evenimentul nu poate fi sters. El face parte din {associated_packets} pachete."
        )

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
        raise HTTPException(status_code=404, detail="Evenimentul n-a fost gasit")

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


async def get_event_ticket(event_id, ticket_cod, session, request, user_id, role) -> BiletResponse:
    await _get_event_db(session, event_id)
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
            detail=f"Biletul cu codul {ticket_cod} n-a fost gasit pentru evenimentul cu id-ul {event_id}"
        )

    if role == "client" and ticket.id_utilizator != user_id:
        raise HTTPException(status_code=403, detail="Acces interzis la biletul altui utilizator")

    return _build_bilet_response(ticket, request)


async def get_all_event_tickets(
        event_id: int,
        session: AsyncSession,
        page: int,
        per_page: int,
        user_id: int,  # Parametru nou
        role: str  # Parametru nou
) -> PaginatedResponse[BiletResponse]:
    await _get_event_db(session, event_id)

    query = select(Bilet).where(Bilet.evenimentID == event_id)

    # daca utlizatorul e client vede doar biletele lui
    if role == "client":
        query = query.where(Bilet.id_utilizator == user_id)

    # daca e owner atunci poate vedea toate biletele pt evenimentul sau
    query = query.order_by(Bilet.cod.desc())

    return await paginate(
        query=query,
        page=page,
        per_page=per_page,
        session=session,
        builder=_build_bilet_response
    )