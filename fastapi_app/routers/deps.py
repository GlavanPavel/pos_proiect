from typing import Annotated
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_app.services.database import get_db_session
from fastapi_app.schemas.link import Link, LinkCollection

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]

class HATEOASLinkBuilder:
    def __init__(self, self_route_name: str, parent_route_name: str):
        self.self_route_name = self_route_name
        self.parent_route_name = parent_route_name

    def __call__(self, request: Request, id: int) -> LinkCollection:

        self_href = request.url_for(self.self_route_name, id=id)
        parent_href = request.url_for(self.parent_route_name)

        self_link = Link(href=str(self_href), method="GET")
        parent_link = Link(href=str(parent_href), method="GET")

        return LinkCollection(self=self_link, parent=parent_link)

event_links_builder = HATEOASLinkBuilder(
    self_route_name="get_event",
    parent_route_name="get_all_events"
)
