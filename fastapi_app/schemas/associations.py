from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from .link import Link

class PachetEventAssociationLinks(BaseModel):
    self: Link
    pachet: Link
    eveniment: Link

class PachetEventAssociationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pachetID: int
    evenimentID: int
    numarLocuri: int

class PachetEventAssociationWithLinks(PachetEventAssociationSchema):
    links: PachetEventAssociationLinks = Field(..., alias="_links")

class PachetEventAssociationResponse(BaseModel):
    asociere: PachetEventAssociationWithLinks
