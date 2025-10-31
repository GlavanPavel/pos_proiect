from typing import Optional
from fastapi import Query
from pydantic import BaseModel

class EventFilterParams(BaseModel):
    location: Optional[str] = Query(None, description="Filtru dupa locatie")
    name: Optional[str] = Query(None, description="Filtru dupa nume partial")
    available_tickets: Optional[int] = Query(
        None,
        ge=0,
        description="Filtru dupa numarul de bilete disponibile"
    )

class PachetFilterParams(BaseModel):
    type: Optional[str] = Query(
        None,
        description="Filtru dupa nume partial",
    )
    event_name: Optional[str] = Query(
        None,
        description="Filtru dupa numele evenimentului"
    )
    available_tickets: Optional[int] = Query(
        None,
        ge=0,
        description="Filtru dupa numarul de bilete disponibile"
    )
