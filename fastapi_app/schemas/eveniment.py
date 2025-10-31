from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from fastapi_app.schemas.link import LinkCollection, Link


class EvenimentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    id_owner: int
    nume: str
    locatie: str
    descriere: str
    numarLocuri: int

class EvenimentCreate(BaseModel):
    id_owner: int
    nume: str
    locatie: str
    descriere: str
    numarLocuri: int

class EvenimentUpdate(BaseModel):
    id_owner: Optional[int] = None
    nume: Optional[str] = None
    locatie: Optional[str] = None
    descriere: Optional[str] = None
    numarLocuri: Optional[int] = None

class EvenimentLinks(BaseModel):
    self: Link
    parent: Optional[Link] = None

class EvenimentWithLinks(EvenimentSchema):
    links: EvenimentLinks = Field(..., alias="_links")

class EvenimentResponse(BaseModel):
    event: EvenimentWithLinks

class EvenimentCollectionLinks(BaseModel):
    self: Link
    parent: Link

class EvenimentCollectionResponse(BaseModel):
    evenimente: List[EvenimentResponse]
    links: EvenimentCollectionLinks = Field(..., alias="_links")