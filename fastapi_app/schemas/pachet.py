from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from fastapi_app.schemas.link import Link


class PachetLinks(BaseModel):
    self: Link
    parent: Optional[Link] = None

class PachetSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    id_owner: int
    nume: str
    locatie: str
    descriere: str

class PachetCreate(BaseModel):
    id_owner: int
    nume: str
    locatie: str
    descriere: str


class PachetWithLinks(PachetSchema):
    links: PachetLinks = Field(..., alias="_links")

class PachetResponse(BaseModel):
    pachet: PachetWithLinks

class PachetCollectionLinks(BaseModel):
    self: Link
    parent: Link

class PachetCollectionResponse(BaseModel):
    pachete: List[PachetResponse]
    links: PachetCollectionLinks = Field(..., alias="_links")

class PachetEventAssociation(BaseModel):
    numarLocuri: int = Field(..., gt=0)