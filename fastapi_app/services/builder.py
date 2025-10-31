from fastapi import Request, HTTPException
from fastapi_app.models import Pachet, Eveniment, Bilet
from fastapi_app.schemas import (
    PachetSchema, Link, EvenimentLinks, EvenimentSchema, EvenimentWithLinks,
    EvenimentResponse, PachetLinks, PachetResponse, PachetWithLinks,
    BiletLinks, BiletSchema, BiletWithLinks, BiletResponse
)


def _build_event_links(event: Eveniment, request: Request) -> EvenimentLinks:
    self_href = request.url_for("get_event", id=event.id)
    return EvenimentLinks(
        self=Link(href=str(self_href), method="GET"),
    )


def _build_event_response(event: Eveniment, request: Request) -> EvenimentResponse:
    event_data = EvenimentSchema.model_validate(event)
    event_links = _build_event_links(event, request)

    event_with_links = EvenimentWithLinks(
        **event_data.model_dump(),
        _links=event_links
    )
    return EvenimentResponse(event=event_with_links)


def _build_pachet_links(pachet: Pachet, request: Request) -> PachetLinks:
    self_href = request.url_for("get_pachet", id=pachet.id)
    return PachetLinks(
        self=Link(href=str(self_href), method="GET"),
    )


def _build_pachet_response(pachet: Pachet, request: Request) -> PachetResponse:
    pachet_data = PachetSchema.model_validate(pachet)
    pachet_links = _build_pachet_links(pachet, request)

    pachet_with_links = PachetWithLinks(
        **pachet_data.model_dump(),
        _links=pachet_links
    )
    return PachetResponse(pachet=pachet_with_links)


def _build_bilet_links(
        ticket: Bilet,
        request: Request
) -> BiletLinks:
    if ticket.evenimentID:
        self_href = request.url_for(
            "get_ticket", cod=ticket.cod
        )
        parent_href = request.url_for("get_event", id=ticket.evenimentID)
    elif ticket.pachetID:
        self_href = request.url_for(
            "get_ticket", cod=ticket.cod
        )
        parent_href = request.url_for("get_pachet", id=ticket.pachetID)
    else:
        raise HTTPException(status_code=500, detail="Link builder called without parent ID")

    return BiletLinks(
        self=Link(href=str(self_href), method="GET"),
        parent=Link(href=str(parent_href), method="GET")
    )


def _build_bilet_response(
        ticket: Bilet,
        request: Request
) -> BiletResponse:
    ticket_data = BiletSchema.model_validate(ticket)
    ticket_links = _build_bilet_links(
        ticket, request
    )

    ticket_with_links = BiletWithLinks(
        **ticket_data.model_dump(),
        _links=ticket_links
    )

    return BiletResponse(ticket=ticket_with_links)