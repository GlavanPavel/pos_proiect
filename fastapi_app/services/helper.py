from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException
from fastapi_app.models import Pachet, Eveniment, Bilet, JoinPE


async def _get_pachet_db(session: AsyncSession, id: int) -> Pachet:
    result = await session.execute(select(Pachet).where(Pachet.id == id))
    packet = result.scalars().first()
    if not packet:
        raise HTTPException(status_code=404, detail="Pachetul nu a fost gasit")
    return packet


async def _get_event_db(session: AsyncSession, id: int) -> Eveniment:
    result = await session.execute(select(Eveniment).where(Eveniment.id == id))
    event = result.scalars().first()
    if not event:
        raise HTTPException(status_code=404, detail="Evenimentul nu a fost gasit")
    return event


async def _get_ticket_db(cod, session):
    result = await session.execute(select(Bilet).where(Bilet.cod == cod))
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Biletul nu a fost gasit")
    return ticket


async def get_pachet_availability(session: AsyncSession, pachet_id: int) -> int:

    capacity_query = (
        select(func.min(JoinPE.numarLocuri))
        .where(JoinPE.pachetID == pachet_id)
    )
    capacity = (await session.execute(capacity_query)).scalar_one_or_none() or 0
    if capacity == 0:
        return 0
    sold_query = (
        select(func.count(Bilet.cod))
        .where(Bilet.pachetID == pachet_id)
    )
    sold = (await session.execute(sold_query)).scalar_one() or 0

    return capacity - sold


async def get_event_available_seats(
        session: AsyncSession,
        eveniment: Eveniment,
        old_allocation: int = 0
) -> int:

    total_capacity = eveniment.numarLocuri
    allocated_sq = (
        select(func.sum(JoinPE.numarLocuri))
        .where(JoinPE.evenimentID == eveniment.id)
        .scalar_subquery()
    )

    sold_sq = (
        select(func.count(Bilet.cod))
        .where(Bilet.evenimentID == eveniment.id)
        .scalar_subquery()
    )

    availability_query = select(
        func.coalesce(total_capacity, 0) -
        (func.coalesce(allocated_sq, 0) - old_allocation) -
        func.coalesce(sold_sq, 0)
    )

    availability = (await session.execute(availability_query)).scalar_one()
    return availability