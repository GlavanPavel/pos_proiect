from typing import List
import logging
from fastapi import HTTPException, Request

from fastapi_app.models import Pachet, JoinPE, Bilet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, func, and_, delete

from .helper import _get_pachet_db, _get_event_db, get_event_available_seats
from fastapi_app.core.pagination import paginate
from .builder import _build_pachet_response, _build_event_response, _build_bilet_response, \
    _build_association_response
from ..schemas import PachetCreate, EvenimentCollectionResponse, EvenimentResponse, Link, BiletResponse, PachetResponse, PachetFilterParams, PaginatedResponse, PachetEventAssociationResponse
from ..schemas.eveniment import EvenimentCollectionLinks
from ..schemas.pachet import PachetEventAssociation


log = logging.getLogger("uvicorn.error")


async def get_all_packets(
        session: AsyncSession,
        page: int,
        per_page: int,
        filters: PachetFilterParams
) -> PaginatedResponse[PachetResponse]:
    query = select(Pachet).distinct()
    filter_conditions = []

    if filters.type:
        filter_conditions.append(Pachet.descriere.ilike(f"%{filters.type}%"))

    if filters.available_tickets is not None:
        packet_capacity_sq = (
            select(func.min(JoinPE.numarLocuri))
            .where(JoinPE.pachetID == Pachet.id)
            .scalar_subquery()
        )

        sold_for_packet_sq = (
            select(func.count(Bilet.cod))
            .where(Bilet.pachetID == Pachet.id)
            .scalar_subquery()
        )

        available = func.coalesce(packet_capacity_sq, 0) - func.coalesce(sold_for_packet_sq, 0)
        filter_conditions.append(available >= filters.available_tickets)

    if filter_conditions:
        query = query.where(and_(*filter_conditions))

    query = query.order_by(Pachet.id.desc())

    return await paginate(
        query=query,
        page=page,
        per_page=per_page,
        session=session,
        builder=_build_pachet_response
    )


async def get_pachet(id, session, request) -> PachetResponse:
    packet = await _get_pachet_db(session, id)
    return _build_pachet_response(packet, request)


async def create_pachet(
    data: PachetCreate,
    session: AsyncSession,
    request: Request,
    owner_id: int
) -> PachetResponse:
    pachet = Pachet(id_owner=owner_id, **data.model_dump(exclude={"id_owner"}))
    session.add(pachet)
    await session.commit()
    await session.refresh(pachet)

    return _build_pachet_response(pachet, request)


async def update_pachet(id: int, data: PachetCreate, session: AsyncSession, request: Request, user_id: int, role: str) -> PachetResponse:
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


async def delete_pachet(id: int, session: AsyncSession, user_id: int, role: str):
    pachet = await _get_pachet_db(session, id)

    sold_query = select(func.count(Bilet.cod)).where(Bilet.pachetID == id)
    sold_tickets = (await session.execute(sold_query)).scalar_one()

    if sold_tickets > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Pachetul nu poate fi sters. {sold_tickets} bilete au fost vandute pentru el."
        )

    join_query = delete(JoinPE).where(JoinPE.pachetID == id)
    await session.execute(join_query)

    await session.delete(pachet)
    await session.commit()
    return


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
        raise HTTPException(status_code=404, detail="Pachetul n-a fost gasit")

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


async def get_pachet_ticket(
    pachet_id: int,
    ticket_cod: str,
    session: AsyncSession,
    request: Request,
    user_id: int,
    role: str
) -> BiletResponse:
    await _get_pachet_db(session, pachet_id)
    query = (
        select(Bilet)
        .where(Bilet.cod == ticket_cod)
        .where(Bilet.pachetID == pachet_id)
    )

    res = await session.execute(query)
    ticket = res.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Biletul nu a fost gasit")

    if role == "client" and ticket.id_utilizator != user_id:
        raise HTTPException(
            status_code=403,
            detail="Nu aveti permisiunea de a vizualiza acest bilet"
        )

    return _build_bilet_response(ticket, request)


async def get_all_pachet_tickets(
        pachet_id: int,
        session: AsyncSession,
        page: int,
        per_page: int,
        user_id: int,
        role: str
) -> PaginatedResponse[BiletResponse]:
    await _get_pachet_db(session, pachet_id)

    query = select(Bilet).where(Bilet.pachetID == pachet_id)

    if role == "client":
        query = query.where(Bilet.id_utilizator == user_id)

    query = query.order_by(Bilet.cod.desc())

    return await paginate(
        query=query,
        page=page,
        per_page=per_page,
        session=session,
        builder=_build_bilet_response
    )


async def add_event_to_pachet(
        pachet_id: int,
        event_id: int,
        data: PachetEventAssociation,
        session: AsyncSession,
        request: Request
) -> PachetEventAssociationResponse:
    await _get_pachet_db(session, pachet_id)
    eveniment = await _get_event_db(session, event_id)

    existing_join_result = await session.execute(
        select(JoinPE).where(
            and_(
                JoinPE.pachetID == pachet_id,
                JoinPE.evenimentID == event_id
            )
        )
    )
    join_record = existing_join_result.scalars().first()

    # daca asocierea deja exista, locurile precedente ocupate vor fi adaugate la cele disponibile
    old_allocation = 0
    if join_record:
        old_allocation = join_record.numarLocuri

    total_available_for_allocation = await get_event_available_seats(
        session, eveniment, old_allocation
    )

    total_available = total_available_for_allocation + old_allocation

    if data.numarLocuri > total_available:
        raise HTTPException(
            status_code=400,
            detail=f"Nu pot fi alocate {data.numarLocuri} locuri. "
                   f"Evenimentul ID {event_id} mai are {total_available} bilete disponibile."
        )

    if join_record:
        join_record.numarLocuri = data.numarLocuri
        session.add(join_record)
    else:
        join_record = JoinPE(
            pachetID=pachet_id,
            evenimentID=event_id,
            numarLocuri=data.numarLocuri
        )
        session.add(join_record)

    await session.commit()
    await session.refresh(join_record)

    return _build_association_response(join_record, request)

async def delete_event_from_pachet(
        pachet_id: int,
        event_id: int,
        session: AsyncSession,
):
    join_query = (
        select(JoinPE).
        where(JoinPE.pachetID == pachet_id).
        where(JoinPE.evenimentID == event_id)
    )
    join_record = (await session.execute(join_query)).scalars().first()

    if not join_record:
        raise HTTPException(
            status_code=404,
            detail="Asocierea intre eveniment si pachet nu exista"
        )

    ticket_query = select(func.count(Bilet.cod)).where(Bilet.pachetID == pachet_id)
    sold_tickets_count = (await session.execute(ticket_query)).scalar_one()

    if sold_tickets_count > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Nu se poate sterge evenimentul din pachet. {sold_tickets_count} bilete au fost deja vandute"
        )

    await session.delete(join_record)
    await session.commit()

    return