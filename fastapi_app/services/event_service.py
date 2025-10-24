from fastapi import Request, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_app.models import Eveniment
from fastapi_app.schemas.eveniment import EvenimentLinks, EvenimentResponse, EvenimentUpdate, EvenimentCreate
from fastapi_app.schemas.link import Link

async def get_event(session: AsyncSession, id: int, request: Request):
    result = await session.execute(select(Eveniment).where(Eveniment.id == id))
    event = result.scalars().first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    self_href = request.url_for("get_event", id=event.id)
    parent_href = request.url_for("get_all_events")

    event_links = EvenimentLinks(
        self=Link(href=str(self_href), method="GET"),
        parent=Link(href=str(parent_href), method="GET"),
    )

    return EvenimentResponse(event=event, event_links=event_links)

async def delete_event(session: AsyncSession, id: int):
    event = (await session.execute(select(Eveniment).where(Eveniment.id == id))).scalars().first()
    if not event:
        raise HTTPException(status_code=404, detail="Eveniment not found")
    await session.delete(event)
    await session.commit()
    return {"ok": True}

async def update_event(session: AsyncSession, id: int, event: EvenimentUpdate):
    existing_event = (await session.execute(select(Eveniment).where(Eveniment.id == id))).scalars().first()

    if not existing_event:
        raise HTTPException(status_code=404, detail="Event not found")

    update_data = event.model_dump(exclude_unset=True) # to dict

    for field, value in update_data.items():
        setattr(existing_event, field, value)

    await session.commit()
    await session.refresh(existing_event)
    return existing_event

async def create_event(session: AsyncSession, event: EvenimentCreate):
    new_event = Eveniment(**event.model_dump())
    session.add(new_event)
    await session.commit()
    await session.refresh(new_event)
    return new_event